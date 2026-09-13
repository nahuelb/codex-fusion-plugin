import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fusion = load('fusion')
usage = load('token_usage')


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'FUSION_STATE_DIR': self.temp.name})
        self.env.start()
        self.db = fusion.connect()

    def tearDown(self):
        self.db.close()
        self.env.stop()
        self.temp.cleanup()

    def command(self, action, session='main', agent=None):
        return fusion.command(self.db, argparse.Namespace(action=action, session=session, agent=agent, model='gpt-5.6-luna', reasoning_effort='medium'))

    def test_explicit_activation_and_isolation(self):
        payload = {'session_id': 'main', 'hook_event_name': 'UserPromptSubmit'}
        self.assertEqual(fusion.hook(self.db, payload), {})
        self.command('activate')
        self.assertIn('hookSpecificOutput', fusion.hook(self.db, payload))
        payload['session_id'] = 'other'
        self.assertEqual(fusion.hook(self.db, payload), {})

    def test_single_registration_and_release(self):
        self.command('activate')
        self.command('register', agent='one')
        self.command('activate')
        self.assertEqual(self.command('status')['agent'], 'one')
        self.command('register', agent='one')
        with self.assertRaises(ValueError):
            self.command('register', agent='two')
        with self.assertRaises(ValueError):
            self.command('release', agent='two')
        with self.assertRaises(ValueError):
            self.command('deactivate')
        self.command('release', agent='one')
        self.command('register', agent='two')
        self.command('release', agent='two')
        self.assertFalse(self.command('deactivate')['active'])

    def test_registration_requires_activation(self):
        with self.assertRaises(ValueError):
            self.command('register', agent='one')

    def test_edit_reminders_are_bounded_and_conditional(self):
        self.command('activate')
        payload = {'session_id': 'main', 'hook_event_name': 'PostToolUse', 'tool_name': 'apply_patch', 'turn_id': 'turn1'}
        first = fusion.hook(self.db, payload)['hookSpecificOutput']['additionalContext']
        self.assertIn('If you are the main agent', first)
        self.assertEqual(fusion.hook(self.db, payload), {})
        payload['turn_id'] = 'turn2'
        self.assertTrue(fusion.hook(self.db, payload))
        payload['tool_name'] = 'Bash'
        self.assertEqual(fusion.hook(self.db, payload), {})

    def test_subagent_reminder_does_not_target_unrelated_roles(self):
        self.command('activate')
        payload = {'session_id': 'main', 'hook_event_name': 'SubagentStart', 'agent_type': 'explorer'}
        self.assertEqual(fusion.hook(self.db, payload), {})
        payload['agent_type'] = 'fusion-sidekick'
        self.assertEqual(fusion.hook(self.db, payload), {})


class UsageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'rollout.jsonl'

    def tearDown(self):
        self.temp.cleanup()

    def write_counts(self, counts):
        lines = []
        for n in counts:
            tokens = dict(zip(usage.KEYS, (n, n // 2, n // 10, 0, n + n // 10)))
            lines.append(json.dumps({'type': 'event_msg', 'payload': {'type': 'token_count', 'info': {'total_token_usage': tokens}}}))
        self.path.write_text('\n'.join(lines))

    def test_cumulative_snapshots_are_not_summed(self):
        self.write_counts([100, 200, 200])
        result = usage.report(self.path, [])
        self.assertEqual(result['total']['input_tokens'], 200)
        self.assertEqual(result['total']['total_tokens'], 220)

    def test_unknown_usage_stays_unknown(self):
        self.path.write_text('{bad\n{}\n')
        result = usage.report(self.path, [])
        self.assertIsNone(result['total'])
        self.assertEqual(len(result['threads'][0]['warnings']), 2)

    def test_duplicate_rollout_is_rejected(self):
        self.write_counts([100])
        with self.assertRaises(ValueError):
            usage.report(self.path, [self.path])

    def test_reset_is_reported(self):
        self.write_counts([200, 100])
        self.assertIn('decreased', usage.analyze(self.path, 'lead')['warnings'][0])


if __name__ == '__main__':
    unittest.main()
