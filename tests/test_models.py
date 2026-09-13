import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import fusion
import model_config


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'models.json'
        self.env = patch.dict(os.environ, {'FUSION_MODELS_FILE': str(self.path), 'FUSION_STATE_DIR': str(Path(self.temp.name) / 'state')})
        self.env.start()
        model_config.initialize()
        self.db = fusion.connect()
        self.call('activate')

    def tearDown(self):
        self.db.close()
        self.env.stop()
        self.temp.cleanup()

    def call(self, action, agent=None, model='gpt-5.6-luna', effort='xhigh', entry='current', session='test'):
        return fusion.command(self.db, argparse.Namespace(action=action, session=session, agent=agent, model=model, reasoning_effort=effort, entry=entry))

    def change(self, role, key, value):
        data = json.loads(self.path.read_text())
        data[role][key] = value
        self.path.write_text(json.dumps(data))

    def test_lead_inherits_current_but_delegated_lead_is_explicit(self):
        self.assertEqual(model_config.resolve('lead')['action'], 'inherit')
        self.assertEqual(model_config.resolve('lead', 'delegated')['spawn_args']['model'], 'gpt-6-astra')
        self.change('lead', 'use_current_model', False)
        self.assertEqual(model_config.resolve('lead')['action'], 'spawn')

    def test_model_change_requires_replacement_without_mutating_active_registration(self):
        self.assertEqual(self.call('dispatch')['action'], 'spawn')
        self.call('register', agent='one')
        self.assertEqual(self.call('dispatch')['action'], 'reuse')
        self.change('sidekick', 'model', 'gpt-6-astra')
        dispatch = self.call('dispatch')
        self.assertEqual(dispatch['action'], 'replace_after_handoff')
        self.assertEqual(dispatch['spawn_args']['model'], 'gpt-6-astra')
        self.assertEqual(self.call('status')['model'], 'gpt-5.6-luna')
        with self.assertRaises(ValueError):
            self.call('register', agent='one', model='gpt-6-astra')
        self.call('release', agent='one')
        self.assertEqual(self.call('dispatch')['action'], 'spawn')
        self.call('register', agent='two', model='gpt-6-astra')
        self.assertEqual(self.call('dispatch')['action'], 'reuse')

    def test_effort_change_also_requires_replacement(self):
        self.call('register', agent='one')
        self.change('sidekick', 'reasoning_effort', 'high')
        self.assertEqual(self.call('dispatch')['action'], 'replace_after_handoff')

    def test_lead_and_formatting_changes_preserve_sidekick(self):
        self.call('register', agent='one')
        self.path.write_text(json.dumps(json.loads(self.path.read_text()), indent=4))
        self.assertEqual(self.call('dispatch')['action'], 'reuse')
        self.change('lead', 'model', 'another/provider-model')
        self.assertEqual(self.call('dispatch')['action'], 'reuse')

    def test_invalid_file_does_not_silently_fallback(self):
        self.call('register', agent='one')
        self.path.write_text('{partial')
        with self.assertRaises(ValueError):
            self.call('dispatch')
        self.assertEqual(self.call('status')['agent'], 'one')

    def test_unknown_keys_are_rejected(self):
        self.change('sidekick', 'reasoning_effrot', 'high')
        with self.assertRaises(ValueError):
            model_config.read()

    def test_initializer_preserves_user_values(self):
        self.change('sidekick', 'model', 'custom/model')
        model_config.initialize()
        self.assertEqual(model_config.resolve('sidekick')['spawn_args']['model'], 'custom/model')

    def test_missing_file_requires_setup(self):
        self.path.unlink()
        with self.assertRaises(ValueError):
            self.call('dispatch')


    def test_prepare_inactive_activates_and_returns_spawn(self):
        result = self.call('prepare', session='fresh')
        self.assertEqual(result['action'], 'spawn')
        self.assertIn('spawn_args', result)
        self.assertNotIn('agent', result)
        self.assertEqual(result['spawn_args']['model'], 'gpt-5.6-luna')
        self.assertEqual(result['spawn_args']['reasoning_effort'], 'xhigh')
        status = self.call('status', session='fresh')
        self.assertTrue(status['active'])
        self.assertIsNone(status['agent'])
        again = self.call('prepare', session='fresh')
        self.assertEqual(again['action'], 'spawn')
        self.assertNotIn('agent', again)

    def test_prepare_same_model_returns_exact_reuse(self):
        self.call('register', agent='one')
        result = self.call('prepare')
        self.assertEqual(result, {'action': 'reuse', 'agent': 'one'})

    def test_prepare_model_change_requires_replacement_without_mutating_registration(self):
        self.call('register', agent='one')
        self.change('sidekick', 'model', 'gpt-6-astra')
        result = self.call('prepare')
        self.assertEqual(result['action'], 'replace_after_handoff')
        self.assertEqual(result['agent'], 'one')
        self.assertEqual(result['spawn_args']['model'], 'gpt-6-astra')
        status = self.call('status')
        self.assertEqual(status['model'], 'gpt-5.6-luna')
        self.assertEqual(status['agent'], 'one')

    def test_prepare_effort_change_requires_replacement_without_mutating_registration(self):
        self.call('register', agent='one')
        self.change('sidekick', 'reasoning_effort', 'high')
        result = self.call('prepare')
        self.assertEqual(result['action'], 'replace_after_handoff')
        self.assertEqual(result['agent'], 'one')
        self.assertEqual(result['spawn_args']['reasoning_effort'], 'high')
        self.assertEqual(self.call('status')['reasoning_effort'], 'xhigh')

    def test_prepare_delegate_lead_without_activation(self):
        self.change('lead', 'use_current_model', False)
        result = self.call('prepare', session='lead-fresh')
        self.assertEqual(result['action'], 'delegate_lead')
        self.assertEqual(result['spawn_args']['model'], 'gpt-6-astra')
        self.assertFalse(self.call('status', session='lead-fresh')['active'])
        lead_result = self.call('prepare', session='lead-fresh', entry='lead')
        self.assertEqual(lead_result['action'], 'spawn')
        self.assertIn('spawn_args', lead_result)
        self.assertTrue(self.call('status', session='lead-fresh')['active'])

    def test_prepare_delegate_lead_preserves_existing_registration(self):
        self.call('register', agent='one')
        self.change('lead', 'use_current_model', False)
        result = self.call('prepare')
        self.assertEqual(result['action'], 'delegate_lead')
        status = self.call('status')
        self.assertEqual(status['agent'], 'one')
        self.assertEqual(status['model'], 'gpt-5.6-luna')

    def test_prepare_entry_lead_ignores_lead_only_change(self):
        self.call('register', agent='one')
        self.change('lead', 'model', 'another/provider-model')
        self.assertEqual(self.call('prepare', entry='lead'), {'action': 'reuse', 'agent': 'one'})
        self.assertEqual(self.call('prepare'), {'action': 'reuse', 'agent': 'one'})

    def test_prepare_invalid_config_does_not_activate_or_alter(self):
        original = self.path.read_text()
        try:
            self.path.write_text('{partial')
            with self.assertRaises(ValueError):
                self.call('prepare', session='bad-fresh')
            self.assertFalse(self.call('status', session='bad-fresh')['active'])
        finally:
            self.path.write_text(original)
        self.call('register', agent='one')
        try:
            self.path.write_text('{partial')
            with self.assertRaises(ValueError):
                self.call('prepare')
            status = self.call('status')
            self.assertEqual(status['agent'], 'one')
            self.assertEqual(status['model'], 'gpt-5.6-luna')
        finally:
            self.path.write_text(original)

    def test_prepare_missing_config_does_not_activate_or_alter(self):
        original = self.path.read_text()
        self.path.unlink()
        try:
            with self.assertRaises(ValueError):
                self.call('prepare', session='missing-fresh')
            self.assertFalse(self.call('status', session='missing-fresh')['active'])
        finally:
            self.path.write_text(original)
        self.call('register', agent='one')
        self.path.unlink()
        try:
            with self.assertRaises(ValueError):
                self.call('prepare')
            self.assertEqual(self.call('status')['agent'], 'one')
        finally:
            self.path.write_text(original)

    def test_prepare_isolated_from_another_session(self):
        self.call('register', agent='one')
        other = self.call('prepare', session='other')
        self.assertEqual(other['action'], 'spawn')
        self.assertTrue(self.call('status', session='other')['active'])
        status = self.call('status')
        self.assertEqual(status['agent'], 'one')
        self.assertEqual(status['model'], 'gpt-5.6-luna')

    def test_prepare_reads_config_once(self):
        with patch.object(model_config, 'read', wraps=model_config.read) as mock_read:
            self.call('prepare', session='once-current')
            self.assertEqual(mock_read.call_count, 1)
        with patch.object(model_config, 'read', wraps=model_config.read) as mock_read:
            self.call('prepare', session='once-lead', entry='lead')
            self.assertEqual(mock_read.call_count, 1)

    def test_prepare_cli_smoke(self):
        script = Path(__file__).resolve().parents[1] / 'scripts' / 'fusion.py'
        env = dict(os.environ)
        proc = subprocess.run(
            [sys.executable, str(script), 'prepare', '--session', 'cli-test'],
            capture_output=True, text=True, env=env, timeout=15,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        output = json.loads(proc.stdout)
        self.assertEqual(output['action'], 'spawn')
        self.assertIn('spawn_args', output)
        self.assertTrue(self.call('status', session='cli-test')['active'])
        bad = subprocess.run(
            [sys.executable, str(script), 'prepare', '--session', 'cli-test', '--entry', 'bogus'],
            capture_output=True, text=True, env=env, timeout=15,
        )
        self.assertNotEqual(bad.returncode, 0)


class RegistryPathTests(unittest.TestCase):
    def test_default_and_empty_codex_home(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True), patch.object(Path, 'home', return_value=Path(directory)):
            expected = Path(directory) / '.codex/plugins/fusion/models.json'
            self.assertEqual(model_config.live_path(), expected)
            os.environ['CODEX_HOME'] = ''
            self.assertEqual(model_config.live_path(), expected)

    def test_custom_codex_home_initializes_and_preserves_registry(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'CODEX_HOME': directory}, clear=True):
            expected = Path(directory) / 'plugins/fusion/models.json'
            loaded = model_config.initialize()
            self.assertEqual(Path(loaded['path']), expected.resolve())
            data = loaded['models']
            data['sidekick']['model'] = 'custom/model'
            expected.write_text(json.dumps(data))
            model_config.initialize()
            self.assertEqual(model_config.resolve('sidekick')['spawn_args']['model'], 'custom/model')

    def test_explicit_file_wins_over_codex_home(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'CODEX_HOME': directory, 'FUSION_MODELS_FILE': str(Path(directory) / 'chosen.json')}, clear=True):
            loaded = model_config.initialize()
            self.assertEqual(Path(loaded['path']), (Path(directory) / 'chosen.json').resolve())
            self.assertFalse((Path(directory) / 'plugins/fusion/models.json').exists())


if __name__ == '__main__':
    unittest.main()
