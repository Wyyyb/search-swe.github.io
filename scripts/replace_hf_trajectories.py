#!/usr/bin/env python3
"""Replace outdated HF trajectories with the prepared 47-task Luna/Terra release.

--prepare records an exact replacement plan using read-only HF requests.
Without flags, validate that plan offline. --apply uploads, verifies, removes old
release directories, verifies again, and rebuilds the local production homepage.
Uses the existing `hf auth login` session. Never deletes a repository or history.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from import_final_results import DEFAULT_PACKAGE, MODELS
from hf_network import authenticated_api, retry_429
from import_results import ROOT, digest, encode, read, write
from prepare_hf_release import referenced_files
from publication import REPO_ID, fingerprints, load_package
from upload_hf_release import activate, check_site_snapshot, verify_remote

DEFAULT_PLAN = ROOT / '.build/hf-replacement-luna-terra.json'


def remote_files(api, revision):
    return {item.path: {'bytes': item.size, 'hash': item.lfs.sha256 if item.lfs else item.blob_id}
            for item in api.list_repo_tree(REPO_ID, revision=revision, repo_type='dataset', recursive=True)
            if hasattr(item, 'blob_id')}


def outside_release(files, release):
    # The Hub can update LFS attributes while uploading. All other old bytes must
    # remain identical until the final parent-guarded replacement commit.
    return {p: v for p, v in files.items() if not p.startswith(release + '/') and p != '.gitattributes'}


def old_directories(files, release):
    return sorted({'/'.join(p.split('/')[:2]) + '/' for p in files
                   if p.startswith('releases/') and not p.startswith(release + '/')})


def verify_coverage(package, manifest):
    snapshot = read(package / manifest['release_path'] / 'snapshot.json')
    if (manifest['tasks'], manifest['entries'], manifest['trials']) != (47, 2, 94):
        raise ValueError('Replacement requires 47 tasks, two models and 94 trials')
    if {e['model'] for e in snapshot['entries']} != set(MODELS):
        raise ValueError('Replacement may contain only GPT-6 Luna and GPT-6.1 Terra')
    tasks = {t['name'] for t in snapshot['tasks']}
    for entry in snapshot['entries']:
        trials = [t for t in snapshot['trials'] if t['entry'] == entry['id']]
        if len(trials) != 47 or {t['task'] for t in trials} != tasks or not all(t['valid'] for t in trials):
            raise ValueError('Incomplete or invalid model coverage')
    referenced_files(package / manifest['release_path'], snapshot)


def prepare_plan(package, plan_path):
    if plan_path.exists():
        return read(plan_path)
    manifest = load_package(package)
    verify_coverage(package, manifest)
    source_hash = check_site_snapshot(package, manifest)
    api = authenticated_api()
    info = api.repo_info(REPO_ID, repo_type='dataset', revision='main', expand=['sha', 'private', 'gated'])
    if info.private or info.gated:
        raise ValueError('Homepage evidence requires a public, non-gated dataset')
    files = remote_files(api, info.sha)
    release = manifest['release_path']
    if any(p.startswith(release + '/') for p in files):
        raise ValueError('Target release already exists; retain the original replacement plan for retries')
    directories = old_directories(files, release)
    if not directories:
        raise ValueError('No existing release directories to replace')
    deleted = [p for p in files if any(p.startswith(d) for d in directories)]
    plan = {'schema': 1, 'kind': 'replace-trajectories', 'repo_id': REPO_ID,
            'package': str(package), 'base_revision': info.sha,
            'base_tree_sha256': digest(encode(outside_release(files, release))),
            'publication_sha256': fingerprints(package / 'publication.json.gz')['sha256'],
            'site_snapshot_sha256': source_hash, 'release_path': release,
            'delete_directories': directories, 'deleted_files': len(deleted),
            'deleted_bytes': sum(files[p]['bytes'] for p in deleted)}
    write(plan_path, plan)
    print(f'Read-only replacement plan saved: {plan_path}')
    return plan


def check_plan(plan):
    if (plan.get('schema') != 1 or plan.get('kind') != 'replace-trajectories' or plan.get('repo_id') != REPO_ID or
            not re.fullmatch(r'[0-9a-f]{40}', plan.get('base_revision', ''))):
        raise ValueError('Unexpected replacement plan or target dataset')
    release = plan['release_path']
    directories = plan['delete_directories']
    if (not directories or len(set(directories)) != len(directories) or any(
            not re.fullmatch(r'releases/[A-Za-z0-9][A-Za-z0-9._-]*/', d) or d == release + '/' for d in directories)):
        raise ValueError('Deletion must name exact old release directories')
    package = Path(plan['package'])
    manifest = load_package(package)
    if (manifest['release_path'] != release or
            fingerprints(package / 'publication.json.gz')['sha256'] != plan['publication_sha256']):
        raise ValueError('Prepared public package changed; no remote mutation allowed')
    verify_coverage(package, manifest)
    source_hash = check_site_snapshot(package, manifest)
    if source_hash != plan['site_snapshot_sha256']:
        raise ValueError('Local homepage snapshot changed after preparation')
    from build_leaderboard import generate
    generate()  # Catch cost or page failures before uploading or deleting anything.
    return package, manifest, source_hash


def assert_unchanged_old_files(files, plan):
    if (digest(encode(outside_release(files, plan['release_path']))) != plan['base_tree_sha256'] or
            old_directories(files, plan['release_path']) != plan['delete_directories']):
        raise ValueError('HF contains unrelated changes since preparation; no old trajectories were deleted')


def matches(item, expected):
    return bool(item and expected and item['bytes'] == expected['bytes'] and item['hash'] in {expected['sha256'], expected['git_blob']})


def already_applied(files, package, plan):
    return (not old_directories(files, plan['release_path']) and
            all(matches(files.get(p), fingerprints(package / p)) for p in ['README.md', 'publication.json.gz']))


def apply(plan, package, manifest, source_hash, plan_path, site_origin, workers=4, api=None):
    from huggingface_hub import CommitOperationAdd, CommitOperationDelete
    api = api or authenticated_api()
    info = api.repo_info(REPO_ID, repo_type='dataset', revision='main', expand=['sha', 'private', 'gated'])
    if info.private or info.gated:
        raise ValueError('The dataset must remain public and non-gated')
    revision = info.sha
    files = remote_files(api, revision)
    if not already_applied(files, package, plan):
        assert_unchanged_old_files(files, plan)
        # An interrupted upload may contain a subset of this exact package. Never
        # overwrite a conflicting release owned by another publication attempt.
        for path, item in files.items():
            if path.startswith(manifest['release_path'] + '/') and not matches(item, manifest['files'].get(path, {})):
                raise ValueError('Existing files at the new release path differ from the prepared package')
        api.whoami()
        print('Uploading the new release resumably; old trajectories remain intact until verification.', flush=True)
        api.upload_large_folder(REPO_ID, package, repo_type='dataset', revision='main', num_workers=workers,
                                allow_patterns=[manifest['release_path'] + '/**'])
        revision = api.repo_info(REPO_ID, repo_type='dataset', revision='main').sha
        verify_remote(api, package, manifest, revision, site_origin, include_metadata=False)
        files = remote_files(api, revision)
        assert_unchanged_old_files(files, plan)
        if check_site_snapshot(package, manifest) != source_hash:
            raise ValueError('Homepage changed during upload; old trajectories were not deleted')
        operations = [CommitOperationDelete(path_in_repo=d, is_folder=True) for d in plan['delete_directories']]
        operations += [CommitOperationAdd(path_in_repo=p, path_or_fileobj=package / p)
                       for p in ['README.md', 'publication.json.gz']]
        commit = retry_429(lambda: api.create_commit(
            REPO_ID, repo_type='dataset', revision='main', parent_commit=revision, operations=operations,
            commit_message=f'Replace outdated trajectories with {manifest["snapshot_id"]}: Luna + Terra, 94 trials'),
            'replacement commit')
        revision = commit.oid
        write(plan_path.with_suffix('.applied.json'), {'revision': revision, 'publication_sha256': plan['publication_sha256']})
    else:
        print('This exact replacement is already on HF; verifying and finishing local activation.', flush=True)
    files = remote_files(api, revision)
    if not already_applied(files, package, plan):
        raise ValueError('Old releases remain or new metadata differs; homepage was not activated')
    verify_remote(api, package, manifest, revision, site_origin)
    if check_site_snapshot(package, manifest) != source_hash:
        raise ValueError('Local homepage changed; remote release is verified but local activation was skipped')
    activate(package, manifest, revision, source_hash)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--prepare', action='store_true', help='Record the deletion plan; read-only HF requests')
    action.add_argument('--apply', action='store_true', help='Upload, verify, delete old releases, and rebuild production pages')
    parser.add_argument('--package', type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument('--plan', type=Path, default=DEFAULT_PLAN)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--site-origin', default='https://search-swe.github.io')
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    plan = prepare_plan(args.package.resolve(), args.plan) if args.prepare else read(args.plan)
    package, manifest, source_hash = check_plan(plan)
    print(f'Target: {REPO_ID}\nReplace old releases at: {plan["base_revision"]}')
    for path in plan['delete_directories']:
        print('  Delete: ' + path)
    print(f'Remove {plan["deleted_files"]:,} old files ({plan["deleted_bytes"] / 1024**3:.2f} GiB).')
    print(f'Publish {manifest["tasks"]} tasks / {manifest["entries"]} models / {manifest["trials"]} trials; '
          f'{len(manifest["files"]):,} public files ({manifest["total_bytes"] / 1024**3:.2f} GiB).')
    if args.apply:
        apply(plan, package, manifest, source_hash, args.plan, args.site_origin, args.workers)
    else:
        print('No HF writes. Run this script with --apply to perform the reviewed replacement.')


if __name__ == '__main__':
    main()
