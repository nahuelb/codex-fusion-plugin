---
name: fusion
description: Use Fusion for coding work with one persistent sidekick, concise briefs, and main-agent review. Activate only when the user requests Fusion.
---

# Fusion

Use one main agent for judgment and one persistent sidekick for bounded execution.
This is an independent Codex adaptation of Cognition's Fusion design.

## Activate

Read [the runtime contract](references/runtime.md) and [the sidekick contract](references/sidekick.md).
Apply the runtime's lead-selection rule before activation; an already designated Fusion lead proceeds without spawning another lead.
Resolve the plugin root as two directories above this file.
Run `python3 <plugin-root>/scripts/fusion.py activate` in the main thread.
The command uses `CODEX_THREAD_ID`; if unavailable, pass the actual thread ID with `--session`. Never invent an ID.
If state activation fails, report that hooks are unavailable and follow the same workflow through instructions.
Keep Fusion active for follow-up work until the user asks to stop or selects another orchestration workflow.
To stop, close the completed sidekick, release its registered ID, and run `python3 <plugin-root>/scripts/fusion.py deactivate`.
Do not stack Fusion with another delegation workflow. Preserve project verification and permission requirements.

## Keep judgment in the main agent

Own requirements, design, ambiguous investigation, acceptance, and user communication.
Delegate implementation, focused verification, environment repair, and broad searches whose results can be summarized.
Inspect enough evidence to settle assumptions before briefing implementation. Use a discovery brief when the implementation is unsettled.
Treat candidate explanations as hypotheses. Confirm reachability before asserting a root cause.

Keep these tasks in the main agent:

- Trivial edits that can be completed and verified in one or two tool turns.
- Data analysis, measurements, evaluation logic, and pipeline configuration where wrong output can appear plausible.
- The exact text of queries against shared or production systems, including read-only queries. Delegate schema discovery first if needed.
- Rendered-browser implementation and verification as one loop, unless applicable instructions require a dedicated browser subagent.

When another instruction requires a specialist, explain the topology exception. Do not silently call that specialist the cheap sidekick.
Urgent user requests can justify a minimal direct action. Preserve required checks.

## Brief and dispatch

Use [the brief format](references/brief.md). Include only task-relevant context, never the full conversation.
Once an edit is settled, provide its exact file, location, and fenced code. Do not make the sidekick re-derive it.
For an unsettled edit, delegate discovery or explicitly grant bounded implementation discretion. Do not fabricate code to fill a template.
Specify runnable verification commands and pass conditions. Choose the narrowest checks that establish the change.
Reserve required broad checks for a final integration gate. Rerun only when changed inputs or new evidence justify it.
Run `fusion.py dispatch` before each handoff to read the live model registry.
Spawn with `fork_context: false`; reuse the agent until dispatch requests replacement for changed model settings.
Default to waiting for the result. Work concurrently only when the main agent has independent work.
Keep only one writer in the shared checkout. Do not edit owned files while the sidekick works.

## Review and finish

Read the artifacts and verification evidence. Do not treat a sidekick's prose as proof.
Review the entire result before sending one consolidated correction brief.
Avoid redoing settled work or rerunning passing checks without cause. Verify unresolved claims at their source.
The main agent owns acceptance, required integration checks, commits, pushes, and external communications under the user's authorization.
Report results and limitations clearly. Do not claim a sidekick ran unless a spawn succeeded.
Keep a concise continuation record: agent ID, accepted changes, pending checks, and lead-owned process handles.
Close the sidekick and release its registered ID when the work is complete. Keep activation for the next user turn; a later task can spawn a new sidekick.
