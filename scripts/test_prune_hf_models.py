"""Model withdrawals preserve retained evidence and require explicit remote execution."""
import copy
import unittest
from pathlib import Path
from unittest.mock import patch

import prune_hf_models as prune
from import_results import apply_selection


class ModelWithdrawalTests(unittest.TestCase):
    def snapshots(self):
        policy = {'schema': 1, 'updated_at': '2026-11-04', 'excluded_models': [prune.MODEL]}
        previous = {'schema': 1, 'id': 'old', 'observed_at': '2026-10-31', 'source_hashes': {'source': 'hash'},
                    'tasks': [{'name': 'task', 'hardware': 'cpu'}],
                    'entries': [{'id': 'keep', 'model': 'keep-model', 'agent_version': '1'},
                                {'id': 'retire', 'model': prune.MODEL, 'agent_version': '1'}],
                    'trials': [{'id': model + '-task', 'task': 'task', 'entry': model, 'score': 1,
                                'tokens': {'total_tokens': 30}, 'trajectory_url': f'trials/{model}/manifest.json',
                                'redacted_fields': 2} for model in ['keep', 'retire']],
                    'publication': {'schema': 1}}
        current = apply_selection(previous, policy)
        current.pop('publication')
        current['trials'][0].update(trajectory_url='local-url', redacted_fields=0)
        return previous, current, policy

    def test_selection_preserves_retained_urls_evidence_and_source(self):
        previous, current, policy = self.snapshots()
        public = prune.retained_snapshot(previous, current, [prune.MODEL])
        self.assertEqual(public['trials'], previous['trials'][:1])
        self.assertEqual(public['entries'], previous['entries'][:1])
        self.assertEqual(public['tasks'], previous['tasks'])
        self.assertEqual(current['trials'][0]['redacted_fields'], 0)
        self.assertEqual(len(previous['trials']), 2)
        self.assertEqual(apply_selection(public, policy), public)

    def test_wrong_model_or_changed_retained_evidence_is_rejected(self):
        previous, current, _ = self.snapshots()
        with self.assertRaises(ValueError):
            prune.retained_snapshot(previous, current, ['keep-model'])
        for change in ['score', 'tokens', 'trial_id', 'entry_version', 'task']:
            updated = copy.deepcopy(current)
            if change == 'score':
                updated['trials'][0]['score'] += 1
            elif change == 'tokens':
                updated['trials'][0]['tokens']['total_tokens'] += 1
            elif change == 'trial_id':
                updated['trials'][0]['id'] = 'different'
            elif change == 'entry_version':
                updated['entries'][0]['agent_version'] = '2'
            else:
                updated['tasks'][0]['hardware'] = 'gpu'
            with self.subTest(change=change), self.assertRaises(ValueError):
                prune.retained_snapshot(previous, updated, [prune.MODEL])

    def test_deletion_uses_exact_model_identity_not_name_substrings(self):
        previous, _, _ = self.snapshots()
        previous['entries'][0]['model'] = prune.MODEL + '-other'
        self.assertEqual(prune.deletion_paths(previous, [prune.MODEL], 'releases/test'),
                         ['releases/test/trials/retire-task/'])

    def test_no_empty_selection_or_other_model_plan_is_accepted(self):
        previous, _, policy = self.snapshots()
        policy['excluded_models'].append('keep-model')
        with self.assertRaises(ValueError):
            apply_selection(previous, policy)
        with self.assertRaises(ValueError):
            prune.check_plan({'schema': 1, 'kind': 'model-withdrawal', 'repo_id': prune.REPO_ID,
                              'base_revision': 'a' * 40, 'removed_models': ['another-model']})

    def test_default_command_cannot_delete_remote_files(self):
        plan = {'base_revision': 'a' * 40, 'delete_directories': ['releases/test/trials/retire/'],
                'deleted_files': 1, 'deleted_bytes': 100, 'update_files': ['README.md']}
        with patch('sys.argv', ['prune_hf_models.py']), patch.object(prune, 'read', return_value=plan), \
             patch.object(prune, 'check_plan', return_value=(Path('/tmp'), {'tasks': 47, 'entries': 3, 'trials': 141}, 'hash')), \
             patch.object(prune, 'apply') as apply:
            prune.main()
            apply.assert_not_called()


if __name__ == '__main__':
    unittest.main()
