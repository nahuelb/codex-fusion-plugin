#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile

import model_config


REMINDER = (
    'Fusion is active. Keep judgment and acceptance in the main agent. '
    'Reuse the registered sidekick; send bounded briefs, wait by default, '
    'and batch review feedback. Read the fusion skill if its contract was compacted.'
)
EDIT_REMINDER = (
    'Fusion edit checkpoint. If you are the main agent, delegate further routine '
    'implementation unless a documented carve-out applies. If you are the sidekick, '
    'finish the edit batch before focused checks. Preserve required verification.'
)


def connect():
    temporary = Path('/tmp') if os.name == 'posix' else Path(tempfile.gettempdir())
    identity = str(os.getuid()) if hasattr(os, 'getuid') else 'user'
    base = Path(os.environ.get('FUSION_STATE_DIR', str(temporary / f'codex-fusion-{identity}')))
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    db = sqlite3.connect(base / 'state.sqlite3', timeout=2)
    db.execute('CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, active INTEGER NOT NULL, agent TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS reminders (session TEXT, turn TEXT, PRIMARY KEY(session, turn))')
    db.execute('CREATE TABLE IF NOT EXISTS agent_models (session TEXT PRIMARY KEY, model TEXT, effort TEXT)')
    return db


def state(db, session):
    row = db.execute('SELECT active, agent FROM sessions WHERE id = ?', (session,)).fetchone()
    setting = db.execute('SELECT model, effort FROM agent_models WHERE session = ?', (session,)).fetchone()
    return {'session': session, 'active': bool(row and row[0]), 'agent': row[1] if row else None,
            'model': setting[0] if setting else None, 'reasoning_effort': setting[1] if setting else None}


def dispatch_result(current, selected):
    settings = selected['spawn_args']
    same = current['model'] == settings['model'] and current['reasoning_effort'] == settings['reasoning_effort']
    selected['action'] = 'spawn' if not current['agent'] else 'reuse' if same else 'replace_after_handoff'
    selected['agent'] = current['agent']
    return selected


def command(db, args):
    session = args.session or os.environ.get('CODEX_THREAD_ID')
    if not session:
        raise ValueError('No CODEX_THREAD_ID; pass the actual main thread ID with --session.')
    with db:
        db.execute('BEGIN IMMEDIATE')
        current = state(db, session)
        if args.action == 'prepare':
            loaded = model_config.read()
            if args.entry == 'current':
                lead = model_config.resolve_loaded(loaded, 'lead')
                if lead['action'] == 'spawn':
                    return {'action': 'delegate_lead', 'spawn_args': lead['spawn_args']}
            selected = model_config.resolve_loaded(loaded, 'sidekick')
            db.execute('INSERT INTO sessions VALUES (?, 1, NULL) ON CONFLICT(id) DO UPDATE SET active = 1', (session,))
            decision = dispatch_result(current, selected)
            result = {'action': decision['action']}
            if decision['agent']:
                result['agent'] = decision['agent']
            if decision['action'] != 'reuse':
                result['spawn_args'] = decision['spawn_args']
            return result
        elif args.action == 'activate':
            db.execute('INSERT INTO sessions VALUES (?, 1, NULL) ON CONFLICT(id) DO UPDATE SET active = 1', (session,))
        elif args.action == 'dispatch':
            if not current['active']:
                raise ValueError('Activate this session first.')
            selected = model_config.resolve('sidekick')
            return dispatch_result(current, selected)
        elif args.action == 'deactivate':
            if current['agent']:
                raise ValueError('Close the sidekick and release its registration before deactivating.')
            db.execute('DELETE FROM sessions WHERE id = ?', (session,))
            db.execute('DELETE FROM reminders WHERE session = ?', (session,))
            db.execute('DELETE FROM agent_models WHERE session = ?', (session,))
        elif args.action == 'register':
            if not current['active']:
                raise ValueError('Activate this session first.')
            if current['agent'] and current['agent'] != args.agent:
                raise ValueError('A sidekick is already registered. Close it and release its ID before replacement.')
            existing = (current['model'], current['reasoning_effort'])
            requested = (args.model, args.reasoning_effort)
            if current['agent'] and existing != requested:
                raise ValueError('Cannot change settings of a registered agent. Replace it after its handoff.')
            db.execute('UPDATE sessions SET agent = ? WHERE id = ?', (args.agent, session))
            db.execute('INSERT OR REPLACE INTO agent_models VALUES (?, ?, ?)', (session, *requested))
        elif args.action == 'release':
            if current['agent'] != args.agent:
                raise ValueError('Agent ID does not match the registered sidekick.')
            db.execute('UPDATE sessions SET agent = NULL WHERE id = ?', (session,))
            db.execute('DELETE FROM agent_models WHERE session = ?', (session,))
        return state(db, session)


def hook(db, payload):
    session = payload.get('session_id')
    if not isinstance(session, str) or not state(db, session)['active']:
        return {}
    event = payload.get('hook_event_name')
    context = None
    if event in ('UserPromptSubmit', 'SessionStart'):
        context = REMINDER + ' Run fusion.py prepare --entry lead before the next handoff to reread the live model file.'
        agent = state(db, session)['agent']
        if agent:
            context += f' Registered sidekick: {agent}. Check its actual status before reuse.'
    elif event == 'PostToolUse' and payload.get('tool_name') in ('apply_patch', 'Edit', 'Write'):
        turn = payload.get('turn_id')
        if isinstance(turn, str) and turn:
            with db:
                inserted = db.execute('INSERT OR IGNORE INTO reminders VALUES (?, ?)', (session, turn)).rowcount
            if inserted:
                context = EDIT_REMINDER
    if context:
        return {'hookSpecificOutput': {'hookEventName': event, 'additionalContext': context}}
    return {}


def main():
    parser = argparse.ArgumentParser(description='Session-scoped Fusion bookkeeping and advisory hooks.')
    commands = parser.add_subparsers(dest='action', required=True)
    for name in ('activate', 'deactivate', 'status', 'register', 'release', 'dispatch', 'prepare'):
        sub = commands.add_parser(name)
        sub.add_argument('--session')
        if name in ('register', 'release'):
            sub.add_argument('--agent', required=True)
        if name == 'register':
            sub.add_argument('--model', required=True)
            sub.add_argument('--reasoning-effort', required=True, choices=sorted(model_config.EFFORTS))
        if name == 'prepare':
            sub.add_argument('--entry', choices=['current', 'lead'], default='current')
    commands.add_parser('hook')
    args = parser.parse_args()
    try:
        with connect() as db:
            if args.action == 'hook':
                payload = json.load(sys.stdin)
                result = hook(db, payload) if isinstance(payload, dict) else {}
            else:
                result = command(db, args)
        print(json.dumps(result))
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(f'Fusion: {exc}', file=sys.stderr)
        if args.action == 'hook':
            print('{}')
        else:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
