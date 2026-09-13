# Evaluation protocol

Compare this plugin, pstack, and a single-agent baseline on the same repository snapshots and tasks.
Use at least three runs per task and rotate run order. Keep model settings, permissions, and acceptance checks recorded.
Include a bounded code change, a bug investigation, a broad refactor, and correctness-critical analysis.

Record acceptance success, elapsed time, lead and sidekick tokens, handoff count, rework count, and required-check results.
Use fresh rollouts per trial so whole-rollout token totals match the trial scope.
Keep cached input separate. Do not add cached input to total input or reasoning output to output again.
Supply each rollout once to `scripts/token_usage.py`. Missing counters remain unknown, never zero.
A decreased cumulative counter makes the report potentially incomplete; resolve that before comparing totals.
Do not infer dollar cost from mixed-model rollouts or subscription usage from token counts.

Runtime acceptance for this plugin:

1. A fresh task discovers the installed fusion skill and reads the live model registry.
2. Activation creates state only for that main thread.
3. A routine implementation brief spawns one sidekick without copying the full conversation.
4. A rework brief reuses the same ID and preserves accepted context.
5. The main agent reviews artifacts and runs remaining required checks.
6. Close, release, and deactivate leave no registered agent.
7. An unrelated task receives no Fusion reminders.

Offline unit tests cover bookkeeping and token math. They do not prove model behavior or hook trust.
Record live acceptance results separately from offline validation.
