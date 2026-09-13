# Codex runtime contract

The plugin supplies workflow instructions and advisory hooks. Native Codex tools execute the work.
Model choices live outside the installed plugin cache. Read them at each handoff.

## Live model selection

Run `python3 <plugin-root>/scripts/model_config.py resolve --role lead --context current` when invoked in the current conversation.
With `lead.use_current_model: true`, the result is `inherit`: the current agent becomes the Fusion lead.
The JSON lead model is reserved for delegated entry. Do not change the current conversation's model.
Read [delegated entry](delegated-entry.md) only when a caller delegates a Fusion run or `use_current_model` is false.

With working bookkeeping, before EVERY sidekick spawn or follow-up brief, run `python3 <plugin-root>/scripts/fusion.py dispatch`. If activation failed, use the main skill's explicit fallback instead.
This reads `$CODEX_HOME/plugins/fusion/models.json` afresh. It returns an action and exact `spawn_args`.
Never use a model-pinned custom agent; use `agent_type: "default"` with the returned model and reasoning effort.
The live user registry selects the model. Do not substitute a model from another workflow or copy a remembered default.
If the file is missing, direct the user to `$setup-fusion` before dispatching.
If the file is invalid, stop new dispatches and report the error. Already running work can finish safely.
If the runtime rejects the selected model or effort, report that mismatch without silently falling back.
A newer explicit user instruction takes precedence; update the live registry when asked, then resolve it again.

Handle the dispatch result:

- `spawn`: start the sidekick with the returned arguments and the portable sidekick contract plus brief.
- `reuse`: send the next brief to the returned agent ID.
- `replace_after_handoff`: collect the current handoff's result, review partial work, close the agent, and release its ID.
  Resolve dispatch again, spawn the replacement, and include a concise summary of accepted work and pending checks.

A model or reasoning change replaces the sidekick at a handoff boundary. It cannot modify an already running model call.
A lead-only change does not replace the sidekick. Formatting-only edits do not replace it either.
When bookkeeping is available, register the actual spawn settings, even if the file changes while the spawn is in progress:
`python3 <plugin-root>/scripts/fusion.py register --agent <id> --model <spawned-model> --reasoning-effort <spawned-effort>`.
Do not register desired settings as evidence of served settings. Inspect runtime metadata when that distinction matters.

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

`activate` stores session state outside the repository in a shared temporary location.
Hooks run only when Codex has enabled and trusted them. They supplement this skill.
Active sessions receive short reminders on user input, resume/compaction, and file edits.
Edit reminders are conditional because tool hook payloads lack a stable role identifier.
The plugin does not parse unstable transcripts to infer identity or block edits.
The registry constrains bookkeeping, not native unregistered spawns. `dispatch` reports the required action; the agent executes it.
Use `status` to inspect activation, the registered ID, and its requested model settings.
