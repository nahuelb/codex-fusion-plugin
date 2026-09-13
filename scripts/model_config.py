#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path


DEFAULTS = Path(__file__).resolve().parents[1] / 'config/models.default.json'
EFFORTS = {'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'}


def live_path():
    codex_home = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex').expanduser()
    return Path(os.environ.get('FUSION_MODELS_FILE', str(codex_home / 'plugins/fusion/models.json'))).expanduser()


def validate(data):
    if not isinstance(data, dict) or set(data) != {'version', 'lead', 'sidekick'} or type(data['version']) is not int or data['version'] != 1:
        raise ValueError('Expected version 1 and exactly the lead and sidekick sections.')
    for role in ('lead', 'sidekick'):
        settings = data[role]
        expected = {'model', 'reasoning_effort'} | ({'use_current_model'} if role == 'lead' else set())
        if not isinstance(settings, dict) or set(settings) != expected:
            raise ValueError(f'{role} must contain exactly {sorted(expected)}.')
        model = settings['model']
        if not isinstance(model, str) or not model.strip() or model != model.strip() or any(c.isspace() for c in model):
            raise ValueError(f'{role}.model must be a nonempty model identifier without whitespace.')
        if not isinstance(settings['reasoning_effort'], str) or settings['reasoning_effort'] not in EFFORTS:
            raise ValueError(f'{role}.reasoning_effort must be one of {sorted(EFFORTS)}.')
        if role == 'lead' and type(settings['use_current_model']) is not bool:
            raise ValueError('lead.use_current_model must be true or false.')
    return data


def read():
    path = live_path()
    try:
        data = validate(json.loads(path.read_text()))
    except FileNotFoundError as exc:
        raise ValueError(f'No live model file at {path}. Run $setup-fusion in Codex (or model_config.py init).') from exc
    revision = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
    return {'path': str(path.resolve()), 'revision': revision, 'models': data}


def resolve_loaded(loaded, role, context='current'):
    settings = loaded['models'][role]
    inherit = role == 'lead' and context == 'current' and settings['use_current_model']
    args = {} if inherit else {'agent_type': 'default', 'fork_context': False, 'model': settings['model'], 'reasoning_effort': settings['reasoning_effort']}
    return {'path': loaded['path'], 'revision': loaded['revision'], 'role': role, 'action': 'inherit' if inherit else 'spawn', 'spawn_args': args}


def resolve(role, context='current'):
    return resolve_loaded(read(), role, context)


def initialize():
    path = live_path()
    if path.exists():
        return read()
    defaults = validate(json.loads(DEFAULTS.read_text()))
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('x') as output:
            output.write(json.dumps(defaults, indent=2) + '\n')
    except FileExistsError:
        pass
    return read()


def main():
    parser = argparse.ArgumentParser(description='Read live Fusion model choices without reinstalling the plugin.')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('init')
    commands.add_parser('show')
    sub = commands.add_parser('resolve')
    sub.add_argument('--role', choices=['lead', 'sidekick'], required=True)
    sub.add_argument('--context', choices=['current', 'delegated'], default='current')
    args = parser.parse_args()
    try:
        result = initialize() if args.command == 'init' else read() if args.command == 'show' else resolve(args.role, args.context)
        print(json.dumps(result, indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Fusion model configuration: {exc}\n')


if __name__ == '__main__':
    main()
