---
name: fusion-usage
description: Analyze recorded token usage for the current or a specified Codex session, with lead and sidekick breakdowns. Use when the user asks for Fusion usage, token accounting, or invokes $fusion-usage.
---

# Analyze Fusion usage

Run this read-only workflow in the current agent. Do not delegate, issue model probes, activate Fusion, or modify configuration.
Resolve the installed plugin root as two directories above this skill directory.

For the current session, run `python3 <plugin-root>/scripts/token_usage.py`.
The helper uses `CODEX_THREAD_ID`; it never selects the globally latest session.
For a supplied session, pass `--session <exact-thread-id>`.
If the user gives a task name or link, resolve its exact ID through available task tools first.
Ask for an ID only when the reference is ambiguous or no supported lookup can resolve it.
Do not substitute another session when its logs are unavailable.
For logs supplied by the user, use `--lead <absolute-path>` and repeated `--sidekick <absolute-path>` arguments instead.

Read the helper's JSON result. It discovers related agents through native subagent ancestry, including replaced or closed agents whose logs remain.
It reads only metadata and token records; never expose prompts, tool output, or full session logs in the response.
Local metadata is a version-sensitive format. Treat unavailable, malformed, or duplicated records as evidence limits.

## Attribute the roles

The selected session is the report's lead. A caller above that session is not included.
Native `fusion-sidekick` roles and explicit sidekick selections are classified as sidekicks.
Default agents are unclassified because the same role can represent reviewers or other helpers.
If the user identifies sidekick IDs, or this conversation contains their verified spawn/registration receipts, rerun with repeated `--sidekick-id <id>` arguments.
Otherwise keep the unclassified group visible. Do not label all related agents as sidekicks to simplify the table.
Never infer roles from model names, token volume, directory, or recency.

## Present the report

Lead with the selected session and observation time. State that these are recorded whole-session totals, not a Fusion-only interval.
Show a compact table by role: lead, confirmed sidekicks, and unclassified subagents when present.
Include input, cached input, output, reasoning output, and total tokens. Add individual agent rows when useful for comparison.
Cached input is already part of input; reasoning output is already part of output. Do not add either twice.
Calculate cached/input or token shares only from complete valid counters. A zero denominator has no percentage.
Keep missing usage unknown. Surface warnings about counter resets, forks, missing logs, and incomplete current responses.
The overall total includes unclassified subagents. It covers discovered files only, not proof that every agent log survived.
Do not claim dollar cost, subscription quota, savings, or per-model cost attribution from token counts alone.
The analysis and this response also consume tokens; their final usage may not yet appear in the snapshot.
