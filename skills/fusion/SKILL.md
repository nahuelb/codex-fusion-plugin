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
Resolve the plugin root as two directories above this skill directory (the directory containing SKILL.md).
Run `python3 <plugin-root>/scripts/fusion.py activate` in the main thread.
The command uses `CODEX_THREAD_ID`; if unavailable, pass the actual thread ID with `--session`. Never invent an ID.
If state activation fails, report that bookkeeping and hooks are unavailable. Track the agent ID and actual spawn settings in the continuation record; run `python3 <plugin-root>/scripts/model_config.py resolve --role sidekick` before each handoff and apply the same reuse/replacement rules without dispatch or registration commands.
Keep Fusion active for follow-up work until the user asks to stop or selects another orchestration workflow.
To stop, steer active work to a safe stopping point when needed, collect its partial result, then close the sidekick, release its registered ID, and deactivate. Do not wait for unwanted work to finish unchanged. Skip bookkeeping commands when activation failed.
Do not stack Fusion with another delegation workflow. Preserve project verification and permission requirements.

## Keep judgment in the main agent

Own requirements, design, ambiguous investigation, acceptance, and user communication.
Delegate implementation, focused verification, environment repair, and broad searches whose results can be summarized.
Inspect enough evidence to settle assumptions before briefing implementation. Use a discovery brief when the implementation is unsettled.
Treat candidate explanations as hypotheses. Confirm reachability before asserting a root cause.

Keep these tasks in the main agent:

- Trivial edits that can be completed and verified in one or two tool turns.
- Authoring and judging correctness-critical work: data analysis, measurements, prompt/rubric/grader/evaluation text, and scoring, threshold, sampling, pipeline, or model configuration. Delegate only mechanical execution of an exact lead-authored recipe; author and check its meaning yourself.
- The exact text of queries against shared or production systems, including read-only queries. Delegate schema discovery first if needed.
- Rendered-browser implementation and verification as one loop, unless applicable instructions require a dedicated browser subagent.

When another instruction requires a specialist, explain the topology exception. Do not silently call that specialist the cheap sidekick.
Urgent user requests can justify a minimal direct action. Preserve required checks.

## Brief and dispatch

Use [the brief format](references/brief.md). Include only task-relevant context, never the full conversation.
Once an edit is settled, provide its exact file, location, and fenced code. Do not make the sidekick re-derive it.
If consequential choices remain unsettled, delegate discovery first. Settle interfaces, data shapes, edge cases, and test cases before implementation. Allow discretion only over minor details within that design; do not ask the sidekick to select an architecture or invent acceptance criteria.
Specify runnable verification commands and pass conditions. Choose the narrowest checks that establish the change.
Reserve required broad checks for a final integration gate. Rerun only when changed inputs or new evidence justify it.
Run `fusion.py dispatch` before each handoff to read the live model registry, using the activation-failure fallback above when needed.
Spawn with `fork_context: false`; reuse the agent until dispatch requests replacement for changed model settings.
Default to waiting for the result. Work concurrently only when the main agent has independent work.
Keep only one writer in the shared checkout. Do not edit owned files while the sidekick works.

## Review and finish

Read the artifacts and verification evidence. Do not treat a sidekick's prose as proof.
Review the full diff and evidence at each completed handoff before further action. Send all corrections in one brief; after an initial miss, prefer rework over taking implementation back.
When a blocker needs direction, answer its questions together and hand execution back. Take over when authority is required or repeated guided attempts have exhausted useful approaches.
For visual deliverables, inspect the rendered artifact or required specialist evidence before acceptance. A build or DOM check alone does not establish visual correctness; report unavailable visual verification explicitly.
Avoid redoing settled work or rerunning passing checks without cause. Verify unresolved claims at their source.
The main agent owns acceptance, required integration checks, commits, pushes, and external communications under the user's authorization.
Report results and limitations clearly. Do not claim a sidekick ran unless a spawn succeeded.
Keep a concise continuation record: agent ID, accepted changes, pending checks, and lead-owned process handles.
Reuse the same sidekick through implementation, corrections, and related follow-ups while the runtime permits. A handoff result alone is not a reason to replace it.
When work ends and runtime cleanup requires closing completed agents, first preserve accepted facts, changed paths, passing checks, pending work, and process handles. Close and release it, then include that summary in the next sidekick brief. This preserves selected context, not Devin's full persistent conversation or prompt cache.
Keep activation for follow-up work until the user stops Fusion.
