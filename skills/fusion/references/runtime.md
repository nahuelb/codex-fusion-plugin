# Codex runtime contract

The plugin supplies workflow instructions and advisory hooks. Native Codex tools execute the work.
Model choices live outside the installed plugin cache. Read them at each handoff.

## Live model selection

For initial entry, run `python3 <plugin-root>/scripts/fusion.py prepare`.
This reads the live registry once, resolves the lead, and activates the session only if this thread will lead.
The registry is `$CODEX_HOME/plugins/fusion/models.json` by default, with the model helper's documented overrides.

- `delegate_lead`: use the returned lead `spawn_args` with [delegated entry](delegated-entry.md). Do not activate the caller or spawn a sidekick there.
- `spawn`: start the sidekick with returned `spawn_args`, its portable contract, and the settled brief.
- `reuse`: send the brief to `agent`. No spawn arguments are needed or returned.
- `replace_after_handoff`: collect and review the current result, close the agent, release its ID, then prepare again and spawn from that fresh decision with accepted-state context.

An already designated Fusion lead uses `prepare --entry lead` before subsequent handoffs. This avoids reselecting the lead after live lead-only edits or inside a delegated run.
Do not run separate lead resolution, activation, and dispatch around a successful preparation. The older commands remain available for diagnostics and compatibility.
Use only the action, agent ID, and spawn arguments returned by preparation. For registry paths and revisions, use `model_config.py show` when diagnosing configuration.
Never use a model-pinned custom agent; use `agent_type: "default"` with the returned model and reasoning effort.
The live user registry selects the model. Do not substitute a model from another workflow or a remembered default.
Missing files require `$setup-fusion`; invalid files block new handoffs. Already running work may finish safely.
If the runtime rejects the selected model or effort, report that mismatch without silently falling back.
A newer explicit user instruction takes precedence; update the live registry when asked, then prepare again.

### Bookkeeping unavailable

If preparation cannot access session state, report bookkeeping and hooks unavailable. For initial entry, resolve `model_config.py resolve --role lead --context current` before proceeding; honor delegated entry if required. An already designated lead skips that lead-selection step.
Track the actual agent ID and spawn settings in the continuation record. Run `model_config.py resolve --role sidekick` before each handoff and compare its model and effort with those actual settings to choose spawn, reuse, or replacement after the handoff.
Do not run prepare, dispatch, register, or release against unavailable bookkeeping. A model-file error is not a bookkeeping fallback. Never bypass permissions to enable it.

A model or reasoning change replaces the sidekick at a handoff boundary. It cannot modify an already running model call.
A lead-only change does not replace the sidekick. Formatting-only edits do not replace it either.
When bookkeeping is available, register the actual spawn settings, even if the file changes while the spawn is in progress:
`python3 <plugin-root>/scripts/fusion.py register --agent <id> --model <spawned-model> --reasoning-effort <spawned-effort>`.
Do not register desired settings as evidence of served settings. Inspect runtime metadata when that distinction matters.

## Fewer model round trips

Where a supported orchestration tool can await dependent calls, run a successful spawn, registration, and wait in one sequential orchestration call. Capture the actual returned ID and the spawn settings; inspect each result before continuing. Never register before spawn succeeds or conceal a registration failure. If registration fails, retain the actual ID, report the failure, and collect or safely stop the agent before any replacement.
For reuse, prepare, inspect the action, send the brief, and wait sequentially in the same orchestration call when supported. Branch on replacement instead of blindly sending to an old ID. Yield while waiting so user updates can be handled.
This batches model round trips, not native operations. Without a supported orchestration surface, perform the same sequence as separate calls. Shell helpers cannot invoke native agent tools.

## Native tool mapping

Inspect available tool schemas before calling them. Names can differ between Codex versions.

| Operation | Current native tool | Important fields |
| --- | --- | --- |
| First brief | `spawn_agent` | returned `spawn_args`, plus `message` containing contract and brief |
| Next brief | `send_input` | `target`, `message` |
| Steer running work | `send_input` | `target`, `message`; use `interrupt: true` when the change must apply immediately |
| Collect result | `wait_agent` | `targets`, supported `timeout_ms` |
| Close completed thread | `close_agent` | Use the live schema's ID field |

The sidekick must not spawn agents. Include its portable contract in each new agent's initial brief.
The registry rejects a second different ID. Close a failed or completed agent before `release --agent <actual-id>`.
Release only updates bookkeeping. A stored ID does not prove a process is alive.
If an agent has lost context, replace it with a compact accepted-state summary after closing and releasing it.
Use bounded waits that permit user updates. Do not repeatedly poll empty state.
If native subagent tools are unavailable, report that Fusion cannot delegate here and complete authorized work directly.
Do not create user-visible Codex tasks as substitute subagents.

## User updates during a handoff

Before resuming a wait, assess every new user message against the running brief. Handle lead-only requests now. Forward relevant changes, answers, or constraints to the sidekick; interrupt for immediate redirection, and queue only when finishing the current brief remains appropriate.
Tell the sidekick to incorporate the update into retained work, not restart it. For a stop request, collect and review partial work and follow the native stop/close contract. A model-setting change still takes effect only at the handoff boundary.
Resume waiting only after deciding that no lead action or steering remains. Deliver promised user answers when available rather than parking them behind another handoff.

## Runtime ownership

Conversation state can survive handoffs. Shell environment, cwd, and background processes are not assumed to survive them.
Use absolute paths or set workdir on each command. Make environment setup reproducible.
The main agent owns persistent servers through supported process session handles.
The sidekick can run a short-lived server and tests within one handoff, then clean it up.
Do not kill unrelated processes or claim a server survives without checking its process handle.
Per-role compaction thresholds and Devin's model routing are not replicated.

## Hooks

Successful preparation or explicit `activate` stores session state outside the repository in a shared temporary location.
Hooks run only when Codex has enabled and trusted them. They supplement this skill.
Active sessions receive short reminders on user input, resume/compaction, and file edits.
Edit reminders are conditional because tool hook payloads lack a stable role identifier.
The plugin does not parse unstable transcripts to infer identity or block edits.
The registry constrains bookkeeping, not native unregistered spawns. `prepare` reports the required action; the agent executes it.
Use `status` to inspect activation, the registered ID, and its requested model settings.
