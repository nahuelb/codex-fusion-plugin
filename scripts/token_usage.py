#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


KEYS = ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens', 'total_tokens')


def analyze(path, role):
    totals = None
    models = set()
    warnings = []
    with path.open() as source:
        for number, line in enumerate(source, 1):
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                warnings.append(f'Ignored malformed line {number}')
                continue
            if not isinstance(item, dict):
                continue
            payload = item.get('payload') or {}
            if not isinstance(payload, dict):
                continue
            if item.get('type') == 'turn_context' and payload.get('model'):
                models.add(payload['model'])
            if item.get('type') != 'event_msg' or payload.get('type') != 'token_count':
                continue
            info = payload.get('info') or {}
            usage = info.get('total_token_usage') if isinstance(info, dict) else None
            if isinstance(usage, dict) and all(isinstance(usage.get(k), int) and usage[k] >= 0 for k in KEYS):
                if totals and usage['total_tokens'] < totals['total_tokens']:
                    warnings.append('Cumulative counter decreased; final snapshot may undercount this rollout')
                totals = {k: usage[k] for k in KEYS}
    if totals is None:
        warnings.append('No complete cumulative token snapshot; usage is unknown')
    return {'role': role, 'path': str(path.resolve()), 'models': sorted(models), 'tokens': totals, 'warnings': warnings}


def report(lead, sidekicks):
    paths = [lead, *sidekicks]
    if len({path.resolve() for path in paths}) != len(paths):
        raise ValueError('Each rollout must be listed once.')
    rows = [analyze(lead, 'lead'), *(analyze(path, 'sidekick') for path in sidekicks)]
    known = all(row['tokens'] is not None for row in rows)
    total = {k: sum(row['tokens'][k] for row in rows) for k in KEYS} if known else None
    return {'threads': rows, 'total': total, 'scope': 'Full supplied rollouts, not an activation interval',
            'limitations': 'Final cumulative snapshots; no price or plan-quota inference. Models are observed, not cost attribution. Reasoning is a subset of output; cached input is a subset of input.'}


def main():
    parser = argparse.ArgumentParser(description='Read explicit Codex rollouts without double-counting cumulative snapshots.')
    parser.add_argument('--lead', type=Path, required=True)
    parser.add_argument('--sidekick', type=Path, action='append', default=[])
    args = parser.parse_args()
    try:
        print(json.dumps(report(args.lead, args.sidekick), indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
