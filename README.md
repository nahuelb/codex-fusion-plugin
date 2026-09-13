# Fusion

An independent implementation of Cognition's Fusion orchestration pattern as a Codex plugin.
A capable main agent plans and reviews. One persistent sidekick implements bounded briefs and verifies the results.
This project is not affiliated with Cognition. It does not include the Devin binary or proprietary prompts.

## Use

Install the plugin from its personal marketplace entry. Initialize the live model file once:

```sh
python3 scripts/model_config.py init
```

Start a fresh Codex task and invoke `Use $fusion to implement <task>`.
Use `fusion:fusion` when the short name is ambiguous.

Edit `~/.config/codex-fusion/models.json` at any time:

```json
{
  "version": 1,
  "lead": {
    "use_current_model": true,
    "model": "gpt-6-astra",
    "reasoning_effort": "medium"
  },
  "sidekick": {
    "model": "gpt-5.6-luna",
    "reasoning_effort": "xhigh"
  }
}
```

The current conversation keeps its model by default.
A caller that delegates a Fusion run uses the configured lead model and effort.
Set `use_current_model` to false to request a delegated lead even from a direct invocation.

Sidekick model or effort changes apply at the next handoff. The running handoff finishes before agent replacement.
Unchanged settings reuse the existing agent. New agents receive the accepted-state summary.
Lead changes apply to the next delegated run. No setting changes an in-flight model call.
No reinstall is needed for JSON edits. The plugin reads the external file on every dispatch.
Invalid JSON blocks new dispatches instead of silently selecting another model.
Save through an atomic file replacement to avoid a temporary parse error during editing.

Use `FUSION_MODELS_FILE` on the Codex host for another absolute registry path.
The initializer preserves an existing valid file. Model availability remains a runtime check.
See [delegated entry](skills/fusion/references/delegated-entry.md) for integration with another conversation.

Hooks require Codex hook trust. Review and enable them through `/hooks` when requested by Codex.
The workflow still operates as instructions without hooks. Hooks do not bypass approvals or verification gates.
Ask to stop Fusion to close and release the sidekick and deactivate the current session.

## Included

- Explicit Fusion skill, runtime adapter, brief format, and sidekick contract.
- Opt-in session state and a single-sidekick registration constraint.
- Advisory reminders after edits, on follow-up input, and on resume/compaction.
- Live lead/sidekick JSON registry and explicit spawn arguments, without model-pinned custom agents.
- Read-only token accounting over explicitly selected Codex rollout files.
- Offline state and accounting tests.

```sh
python3 scripts/model_config.py show
python3 scripts/fusion.py status
python3 scripts/fusion.py dispatch
python3 scripts/token_usage.py --lead /absolute/lead.jsonl --sidekick /absolute/sidekick.jsonl
python3 -m unittest discover -s tests -v
```

State uses `/tmp/codex-fusion-<uid>/state.sqlite3` on macOS/Linux, or the user temporary directory on Windows.
The temporary location supports standard workspace sandboxes. System cleanup can remove activation state.
Override with `FUSION_STATE_DIR` on the Codex host so both commands and hooks inherit the same location.
Setting that variable only inside one tool command does not configure the hook process.
Commands read `CODEX_THREAD_ID`, or accept `--session <actual-id>` after the subcommand.
The state registry does not control native agent processes. Close a sidekick before releasing its ID.

## Fidelity and limits

The core handoff loop, task carve-outs, focused verification, and consolidated review come from the recovered Fusion design.
Codex provides the native agent runtime. The plugin does not recreate Devin's backend or model routing.
The hooks provide reminders, not mandatory delegation or an access-control boundary.
The registry prevents conflicting registrations; it cannot prevent an agent from spawning an unregistered agent.
Subagent conversation continuity is distinct from shell or process continuity. Persistent services remain main-agent-owned.
Cost savings and task quality have not been benchmarked. Token reports do not infer subscription quota or dollar cost.

See [evidence and adaptations](docs/evidence.md) and [evaluation protocol](docs/evaluation.md).

## Local development

The personal marketplace uses `~/plugins/fusion`, a clean export of reviewed `main`.
Refresh that export before reinstalling plugin code; see [installation](docs/installation.md).
Regenerate the cachebuster with the plugin-creator helper before reinstalling changed files.
Run the plugin validator and skill validator, then `codex plugin add fusion@personal`.
Model settings remain in the external registry across reinstalls.
New tasks load installed updates. Existing tasks do not prove that an update loaded.
