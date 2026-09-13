# Validation record

Date: 2026-09-13.

## Offline

Forty unit tests pass. They cover session isolation, registration conflicts, matching release,
activation requirements, bounded reminders, unrelated roles, cumulative token accounting,
missing counters, duplicate rollouts, and decreasing counters.
The official plugin validator and skill validator pass.

## Initial fresh-task workflow smoke test (before the live registry)

A fresh `codex exec` task loaded the installed namespaced skill and all three references.
It discovered the installed `fusion-sidekick` custom agent in the native spawn schema.
It spawned agent `01a0992a-614f-7741-a6a2-787c12542371` with history forking disabled.
The same agent implemented `add` and then `sub` through two briefs.
Both focused checks passed. The main agent also inspected and verified the artifact.
The agent was closed, its registration released, and activation cleared.
Final state was `active: false`, `agent: null`.

The initial sidekick rollout recorded `model: gpt-5.6-luna` and `effort: medium` on both turns.
This verifies configured model routing as recorded by Codex, not independent provider attestation.

Local raw evidence:

- `/tmp/fusion-live-smoke/events.jsonl`
- `/tmp/fusion-live-smoke/result.txt`
- `/tmp/fusion-live-smoke/calc.py`
- `~/.codex/sessions/2026/09/13/rollout-2026-09-13T02-08-06-01a0992a-614f-7741-a6a2-787c12542371.jsonl`

## State-path correction

The first smoke test found that `~/.local/state` was outside the standard sandbox's writable roots.
A command-only environment override let the workflow run but hid that activation from host hooks.
The final implementation instead defaults to a shared user-specific directory under `/tmp` on POSIX.
Commands and hooks now derive the same location without an environment override.
A second fresh task successfully activated the corrected default path under workspace-write.
A host invocation of the hook read that activation and returned the expected reminder.
The test then deactivated the state. This verifies shared-state visibility, not automatic hook delivery.

## Limits

The smoke task explicitly requested the two handoffs; it does not measure spontaneous delegation adherence.
No benchmark or dollar-savings claim follows from this test.
Hook outputs are covered offline; automatic delivery in a trusted live Codex session is not yet verified.
No hook-trust configuration was changed or bypassed.

## Live registry smoke test

A fresh task loaded the installed plugin with an isolated scratch registry.
Its first default-agent spawn used the registry's Luna/medium settings.
After changing the scratch JSON to Astra/low, dispatch returned `replace_after_handoff`.
The task collected the result, closed and released the first agent, resolved again, and spawned the replacement.
Both agents returned the same marker carried in the concise handoff summary.
The native runtime accepted both model/effort pairs. No plugin reinstall occurred during the test.
Lead resolution returned `inherit` for current entry and explicit Astra/medium for delegated entry.
Final state was inactive with no registered agent. Both agents were closed.

Evidence is in `/tmp/fusion-dynamic-smoke/events.jsonl` and `/tmp/fusion-dynamic-smoke/result.txt`.
The test's scratch settings are separate from shipped defaults and the user's live registry.
The final shipped sidekick default is Luna/xhigh. No user-specific model selection is stored in this repository.


## Fidelity revision and live use

The lead authored the instruction changes and a sidekick applied the exact patch without writing new prompt policy.
The first spawn attempt rejected the configured local model identifier. After an explicitly authorized local correction, the native spawn succeeded.
This exposed a setup limitation: schema-valid model names are not proof of runtime availability. No local model identifiers are included here.
The lead reviewed the full diff before reusing the same sidekick for a second validation handoff.
The review also found an ambiguous plugin-root instruction and a bookkeeping-failure fallback that still demanded dispatch. Both instructions were corrected.

Full-session context persistence remains runtime-dependent. A continuation summary after cleanup preserves selected facts, not the original conversation or its cache.
A live implementation handoff does not prove adherence to every revised instruction, automatic hook delivery, or model-pair performance.
