"""Replacement must preserve old data on failure and recover from lost commit responses."""
import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from huggingface_hub import CommitOperationDelete

import replace_hf_trajectories as replace
from import_results import digest, encode
from publication import fingerprints


class FakeHub:
    def __init__(self, package, manifest):
        self.package, self.manifest = package, manifest
        self.sha = 'a' * 40
        self.files = {p: {'bytes': 3, 'hash': 'old'} for p in
                      ['.gitattributes', 'README.md', 'publication.json.gz', 'releases/old/trials/old.json', 'LICENSE']}
        self.calls, self.upload_failure, self.unrelated_change, self.lost_response = [], False, False, False

    def repo_info(self, *args, **kwargs):
        return SimpleNamespace(sha=self.sha, private=False, gated=False)

    def list_repo_tree(self, *args, **kwargs):
        return [SimpleNamespace(path=p, size=v['bytes'], blob_id=v['hash'], lfs=None) for p, v in self.files.items()]

    def whoami(self):
        self.calls.append('auth')

    def upload_large_folder(self, *args, **kwargs):
        self.calls.append('upload')
        assert kwargs['allow_patterns'] == ['releases/new/**']
        assert 'releases/old/trials/old.json' in self.files
        if self.upload_failure:
            raise RuntimeError('upload interrupted')
        for p, f in self.manifest['files'].items():
            if p.startswith('releases/new/'):
                self.files[p] = {'bytes': f['bytes'], 'hash': f['git_blob']}
        self.sha = 'b' * 40
        if self.unrelated_change:
            self.files['releases/old/trials/old.json']['hash'] = 'someone-else-edited-this'

    def create_commit(self, *args, **kwargs):
        self.calls.append('commit')
        assert kwargs['parent_commit'] == self.sha
        for operation in kwargs['operations']:
            if isinstance(operation, CommitOperationDelete):
                assert operation.path_in_repo == 'releases/old/' and operation.is_folder
                self.files = {p: v for p, v in self.files.items() if not p.startswith(operation.path_in_repo)}
            else:
                p = operation.path_in_repo
                assert p in {'README.md', 'publication.json.gz'}
                f = fingerprints(self.package / p)
                self.files[p] = {'bytes': f['bytes'], 'hash': f['git_blob']}
        self.sha = 'c' * 40
        if self.lost_response:
            raise RuntimeError('commit response lost')
        return SimpleNamespace(oid=self.sha)


class ReplacementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.package = Path(self.tmp.name) / 'package'
        for p in ['README.md', 'publication.json.gz', 'releases/new/snapshot.json']:
            destination = self.package / p
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text('new public bytes: ' + p)
        self.manifest = {'release_path': 'releases/new', 'snapshot_id': 'new', 'files': {
            p: fingerprints(self.package / p) for p in ['README.md', 'releases/new/snapshot.json']}}
        self.api = FakeHub(self.package, self.manifest)
        self.plan = {'schema': 1, 'kind': 'replace-trajectories', 'repo_id': replace.REPO_ID,
                     'base_revision': 'a' * 40, 'release_path': 'releases/new',
                     'base_tree_sha256': digest(encode(replace.outside_release(self.api.files, 'releases/new'))),
                     'delete_directories': ['releases/old/'], 'publication_sha256': 'fixed'}
        self.plan_path = Path(self.tmp.name) / 'plan.json'
        self.verifications = []

    def verify(self, api, package, manifest, revision, origin, include_metadata=True):
        self.api.calls.append('verify-final' if include_metadata else 'verify-new')
        self.assertEqual(revision, self.api.sha)
        self.assertIn('releases/new/snapshot.json', self.api.files)
        self.assertEqual('releases/old/trials/old.json' in self.api.files, not include_metadata)
        self.verifications.append(include_metadata)

    def apply(self, verifier=None):
        with patch.object(replace, 'verify_remote', side_effect=verifier or self.verify), \
             patch.object(replace, 'check_site_snapshot', return_value='site-hash'), \
             patch.object(replace, 'activate') as activate:
            replace.apply(self.plan, self.package, self.manifest, 'site-hash', self.plan_path,
                          'https://search-swe.github.io', api=self.api)
            return activate

    def test_verified_upload_precedes_exact_deletion_and_activation(self):
        activate = self.apply()
        self.assertEqual(self.api.calls, ['auth', 'upload', 'verify-new', 'commit', 'verify-final'])
        self.assertIn('LICENSE', self.api.files)
        self.assertIn('.gitattributes', self.api.files)
        self.assertNotIn('releases/old/trials/old.json', self.api.files)
        activate.assert_called_once_with(self.package, self.manifest, 'c' * 40, 'site-hash')

    def test_upload_failure_preserves_old_data_and_metadata(self):
        before = copy.deepcopy(self.api.files)
        self.api.upload_failure = True
        with self.assertRaisesRegex(RuntimeError, 'upload interrupted'):
            self.apply()
        self.assertEqual(self.api.files, before)
        self.assertNotIn('commit', self.api.calls)

    def test_verification_failure_never_deletes_old_release(self):
        def failed(*args, **kwargs):
            raise ValueError('download integrity failed')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            self.apply(failed)
        self.assertIn('releases/old/trials/old.json', self.api.files)
        self.assertEqual(self.api.files['README.md']['hash'], 'old')
        self.assertNotIn('commit', self.api.calls)

    def test_concurrent_changes_abort_cleanup(self):
        self.api.unrelated_change = True
        with self.assertRaisesRegex(ValueError, 'unrelated changes'):
            self.apply()
        self.assertNotIn('commit', self.api.calls)
        self.assertIn('releases/old/trials/old.json', self.api.files)

    def test_lost_commit_response_can_finish_without_reupload_or_deletion(self):
        self.api.lost_response = True
        with self.assertRaisesRegex(RuntimeError, 'response lost'):
            self.apply()
        self.api.calls.clear()
        activate = self.apply()
        self.assertEqual(self.api.calls, ['verify-final'])
        activate.assert_called_once()

    def test_partial_upload_resumes_but_conflicting_payload_is_rejected(self):
        self.api.upload_large_folder(allow_patterns=['releases/new/**'])
        self.api.calls.clear()
        self.apply()
        self.assertIn('commit', self.api.calls)
        self.setUp()
        self.api.files['releases/new/unlisted.json'] = {'bytes': 4, 'hash': 'unexpected'}
        with self.assertRaisesRegex(ValueError, 'differ from'):
            self.apply()
        self.assertNotIn('upload', self.api.calls)

    def test_broad_or_current_release_deletion_is_rejected_offline(self):
        for directory in ['releases/', 'releases/../', 'releases/new/', '/', 'README.md']:
            with self.subTest(directory=directory), self.assertRaisesRegex(ValueError, 'exact old release'):
                replace.check_plan({**self.plan, 'delete_directories': [directory]})


if __name__ == '__main__':
    unittest.main()
