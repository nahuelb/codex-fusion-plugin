# Evaluation protocol

Compare this plugin, pstack, and a single-agent baseline on the same repository snapshots and tasks.
Use at least three runs per task and rotate run order. Keep model settings, permissions, and acceptance checks recorded.
Include a bounded code change, a bug investigation, a broad refactor, and correctness-critical analysis.

Record acceptance success, elapsed time, lead and sidekick tokens, handoff count, rework count, and required-check results.
Use fresh rollouts per trial so whole-rollout token totals match the trial scope.
Keep cached input separate. Do not add cached input to total input or reasoning output to output again.
Use `$fusion-usage` for a current or specified session snapshot. Confirm sidekick identities before comparing role totals.
For explicit file input, supply each rollout once to `scripts/token_usage.py`. Missing counters remain unknown, never zero.
A decreased cumulative counter makes the report potentially incomplete; resolve that before comparing totals.
Do not infer dollar cost from mixed-model rollouts or subscription usage from token counts.

Runtime acceptance for this plugin:

1. A fresh task discovers the installed fusion skill and reads the live model registry.
2. Preparation reads models once and activates only the designated main thread; delegated-lead selection leaves the caller inactive.
3. A routine implementation brief spawns one sidekick without copying the full conversation.
4. A rework brief reuses the same ID and preserves accepted context.
5. The main agent reviews artifacts and runs remaining required checks.
6. After required cleanup, close and release leave no registered agent; retain a continuation summary for related work. Explicitly stopping Fusion also deactivates it.
7. An unrelated task receives no Fusion reminders.

Offline unit tests cover bookkeeping and token math. They do not prove model behavior or hook trust.
Record live acceptance results separately from offline validation.


Instruction acceptance scenarios (record observed behavior separately from written policy):

- Related follow-up: reuse the same available sidekick; if cleanup required replacement, carry accepted results and checks without claiming full cache continuity.
- User changes a running brief: assess the change before waiting again and steer the same agent; preserve already accepted work.
- Unsettled interface: delegate discovery, then have the lead settle the interface and test expectations before implementation.
- Request to create a grader or production query: the lead authors and judges its logic; any sidekick work mechanically applies that exact recipe.
- Failed check: the sidekick attempts an in-scope repair, reruns affected checks, and reports remaining blockers with evidence.
- Unrendered UI: report visually unverified rather than treating a build as visual evidence.
- Unavailable bookkeeping: preserve the actual agent ID and settings in a continuation record, resolve live models directly, and avoid prepare/dispatch/register commands until bookkeeping is available.

These are lead-authored evaluation cases, not automated proof of agent behavior.
