"""Withdraw GLM 5.3 Flash locally; delete its exact HF trial directories only with --apply."""
from __future__ import annotations

import argparse
import copy
import gzip
import json
import re
import shutil
from pathlib import Path

from import_results import ROOT, apply_selection, digest, encode, read, selection_policy, write
from leaderboard_costs import apply_costs
from prepare_hf_release import finalize, referenced_files
from publication import REPO_ID, check_text, fingerprints, load_package
from prune_hf_tasks import apply, validate_delta
from upload_hf_release import check_site_snapshot

MODEL = 'z-ai/glm-5.3-flash'
DEFAULT_BASE = ROOT / '.build/hf-trajectories-47'
DEFAULT_PACKAGE = ROOT / '.build/hf-trajectories-without-glm'
DEFAULT_PLAN = ROOT / '.build/hf-model-removal-2026-11-04.json'
CONTENT = ROOT / 'content/leaderboard'


def retained_snapshot(previous, current, removed):
    """Reject changed tasks, scores, usage, configurations, or retained trial IDs."""
    old_models = {e['model'] for e in previous['entries']}
    new_models = {e['model'] for e in current['entries']}
    if (old_models - new_models != set(removed) or new_models - old_models or
            set(current.get('selection', {}).get('excluded_models', [])) != set(removed)):
        raise ValueError('Model difference does not match the withdrawal policy')
    expected = apply_selection(previous, current['selection'])

    def comparable(snapshot):
        result = copy.deepcopy(snapshot)
        result.pop('publication', None)
        for trial in result['trials']:
            trial.pop('trajectory_url', None)
            trial.pop('redacted_fields', None)
        return result

    if comparable(current) != comparable(expected):
        raise ValueError('Retained task metadata, model configuration, or trial evidence changed')
    return expected


def deletion_paths(previous, models, release):
    ids = {e['id'] for e in previous['entries'] if e['model'] in models}
    return sorted(f'{release}/trials/{t["id"]}/' for t in previous['trials'] if t['entry'] in ids)


def prepare(base_package, package, plan_path):
    if plan_path.exists():
        plan = read(plan_path)
        check_plan(plan)
        print(f'Existing withdrawal plan verified: {plan_path}')
        return plan
    storage = read(CONTENT / 'storage.json')
    if (storage.get('provider') != 'huggingface' or storage.get('repo_id') != REPO_ID or
            not re.fullmatch(r'[0-9a-f]{40}', storage.get('revision', '')) or storage.get('pending_model_removal')):
        raise ValueError('Preparation requires the currently verified HF release')
    base = load_package(base_package, check_content=False)
    base_hash = fingerprints(base_package / 'publication.json.gz')['sha256']
    if (base_hash != storage['publication_sha256'] or base['snapshot_id'] != storage['snapshot_id'] or
            base['release_path'] != storage['release_path'] or base['source_hashes'] != storage['source_hashes']):
        raise ValueError('Base package does not match the pinned website release')
    source = (CONTENT / 'release.json').read_bytes()
    if digest(source) != storage['site_snapshot_sha256'] or check_site_snapshot(base_package, base) != digest(source):
        raise ValueError('Website source differs from the verified base package')
    policy = selection_policy()
    if not policy or policy['excluded_models'] != [MODEL]:
        raise ValueError('This withdrawal must select only GLM 5.3 Flash')
    previous_site = json.loads(source)
    current = apply_selection(previous_site, policy)
    release = base['release_path']
    previous = read(base_package / release / 'snapshot.json')
    public = retained_snapshot(previous, current, [MODEL])
    directories = deletion_paths(previous, [MODEL], release)
    # Authenticate the original cost supplement before retaining its unchanged amounts.
    prices = (CONTENT / 'official-pricing.json').read_bytes()
    costs = read(CONTENT / 'costs.json')
    apply_costs(previous_site, costs, json.loads(prices), digest(source), digest(prices))
    current_source = encode(current)
    costs['snapshot_id'] = current['id']
    costs['snapshot_sha256'] = digest(current_source)
    trial_ids = {t['id'] for t in current['trials']}
    costs['trials'] = {key: value for key, value in costs['trials'].items() if key in trial_ids}

    if package.exists() and any(package.iterdir()):
        updated = load_package(package, check_content=False)
        if read(package / release / 'snapshot.json') != public:
            raise ValueError('Output package belongs to another update; choose an empty --package')
    else:
        for relative in base['files']:
            if relative in {'README.md', release + '/snapshot.json'} or any(relative.startswith(d) for d in directories):
                continue
            target = package / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(base_package / relative, target)
        updated = finalize(package, public, release)
    deleted = validate_delta(base, updated, directories)
    check_text(package / release / 'snapshot.json')
    check_text(package / 'README.md')
    referenced_files(package / release, public)

    # A selected subset can keep reading the already-verified immutable HF bytes.
    # The dataset's own summary/inventory remains at the base until the user runs --apply.
    pending = {**storage, 'snapshot_id': current['id'], 'site_snapshot_sha256': digest(current_source),
               'pending_model_removal': {'base_snapshot_id': previous_site['id'], 'models': [MODEL]}}
    plan = {'schema': 1, 'kind': 'model-withdrawal', 'repo_id': REPO_ID,
            'base_revision': storage['revision'], 'base_package': str(base_package), 'package': str(package),
            'base_publication_sha256': base_hash,
            'publication_sha256': fingerprints(package / 'publication.json.gz')['sha256'],
            'site_snapshot_sha256': digest(current_source), 'selection': policy,
            'removed_models': [MODEL], 'delete_directories': directories,
            'deleted_files': len(deleted), 'deleted_bytes': sum(base['files'][p]['bytes'] for p in deleted),
            'update_files': ['README.md', release + '/snapshot.json', 'publication.json.gz'],
            'commit_message': f'Withdraw GLM 5.3 Flash; retain {len(current["trials"])} trials across 3 models'}
    # Keep the previous local metadata outside the published website for recovery/auditing.
    backup = plan_path.with_suffix('.before.json')
    write(backup, {'snapshot': previous_site, 'storage': storage, 'costs': read(CONTENT / 'costs.json')})
    write(plan_path, plan)
    write(CONTENT / 'release.json', current_source)
    write(CONTENT / 'releases' / f'{current["id"]}.json', current_source)
    old_archive = CONTENT / 'releases' / f'{previous_site["id"]}.json'
    if old_archive.exists() and old_archive.name != f'{current["id"]}.json':
        old_archive.unlink()
    write(CONTENT / 'costs.json', (json.dumps(costs, indent=2, sort_keys=True) + '\n').encode())
    write(CONTENT / 'storage.json', pending)
    from build_leaderboard import generate, write_pages
    changed, removed = write_pages(generate(production=True))
    print(f'Updated homepage: {len(current["tasks"])} tasks / {len(current["entries"])} models / {len(current["trials"])} trials.')
    print(f'Generated {changed} files; removed {removed} obsolete pages. HF has not been changed.')
    print(f'Prepared plan: {plan_path}')
    return plan


def check_plan(plan):
    if (plan.get('schema') != 1 or plan.get('kind') != 'model-withdrawal' or
            plan.get('repo_id') != REPO_ID or plan.get('removed_models') != [MODEL] or
            not re.fullmatch(r'[0-9a-f]{40}', plan.get('base_revision', ''))):
        raise ValueError('Unexpected model withdrawal plan or target')
    if plan['selection'] != selection_policy():
        raise ValueError('Website selection changed after preparation')
    package, base_package = Path(plan['package']), Path(plan['base_package'])
    for folder, field in [(package, 'publication_sha256'), (base_package, 'base_publication_sha256')]:
        if fingerprints(folder / 'publication.json.gz')['sha256'] != plan[field]:
            raise ValueError('Publication inventory changed after preparation')
    base = json.loads(gzip.decompress((base_package / 'publication.json.gz').read_bytes()))
    updated = load_package(package, check_content=False)
    release = base['release_path']
    previous_path = base_package / release / 'snapshot.json'
    if fingerprints(previous_path) != base['files'][release + '/snapshot.json']:
        raise ValueError('Base snapshot changed after preparation')
    previous = read(previous_path)
    current = read(CONTENT / 'release.json')
    if digest((CONTENT / 'release.json').read_bytes()) != plan['site_snapshot_sha256']:
        raise ValueError('Website result selection changed after preparation')
    public = retained_snapshot(previous, current, plan['removed_models'])
    if (read(package / release / 'snapshot.json') != public or
            deletion_paths(previous, plan['removed_models'], release) != plan['delete_directories']):
        raise ValueError('Prepared withdrawal differs from the selected model')
    deleted = validate_delta(base, updated, plan['delete_directories'])
    if len(deleted) != plan['deleted_files'] or sum(base['files'][p]['bytes'] for p in deleted) != plan['deleted_bytes']:
        raise ValueError('Deletion totals changed')
    if plan['update_files'] != ['README.md', release + '/snapshot.json', 'publication.json.gz']:
        raise ValueError('Only the dataset card, snapshot and inventory may be updated')
    check_text(package / release / 'snapshot.json')
    check_text(package / 'README.md')
    referenced_files(package / release, public)
    # Catch stale costs/build inputs before the remote mutation, rather than after it.
    from build_leaderboard import generate
    generate(production=True)
    return package, updated, check_site_snapshot(package, updated)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--prepare', action='store_true', help='Prepare the exact deletion and update homepage locally; no HF requests')
    action.add_argument('--apply', action='store_true', help='Delete GLM trial directories, update metadata, verify, and pin the website')
    parser.add_argument('--base-package', type=Path, default=DEFAULT_BASE)
    parser.add_argument('--package', type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument('--plan', type=Path, default=DEFAULT_PLAN)
    parser.add_argument('--site-origin', default='https://search-swe.github.io')
    args = parser.parse_args()
    if args.prepare:
        prepare(args.base_package.absolute(), args.package.absolute(), args.plan)
        return
    plan = read(args.plan)
    package, manifest, source_hash = check_plan(plan)
    print(f'Target: {REPO_ID}\nBase commit: {plan["base_revision"]}\nModel: {MODEL}')
    print(f'Remove {len(plan["delete_directories"])} trial directories / {plan["deleted_files"]:,} files / {plan["deleted_bytes"] / 1024**2:.2f} MiB:')
    for directory in plan['delete_directories']:
        print('  ' + directory)
    print(f'Keep {manifest["tasks"]} tasks / {manifest["entries"]} models / {manifest["trials"]} trials. Update only: ' + ', '.join(plan['update_files']))
    if not args.apply:
        print('Offline check only. Run with --apply to perform this exact HF update.')
        return
    apply(plan, package, manifest, source_hash, args.plan, args.site_origin)


if __name__ == '__main__':
    main()
