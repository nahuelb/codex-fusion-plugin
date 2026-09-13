# Evidence and adaptations

Research baseline: 2026-09-13, Devin CLI v3000.10.21.
Sources: [Cognition announcement](https://cognition.com/blog/local-fusion), locally inspected binary strings, and the prior pstack research report.
The binary was inspected without authentication or a live Fusion session.
Embedded templates reveal instruction variants; static strings do not establish their selection conditions or effective defaults.
This plugin paraphrases the recovered behavior. It does not redistribute the original prompt dump.

| Recovered mechanism | Plugin implementation | Evidence boundary |
| --- | --- | --- |
| One persistent sidekick; briefs and results | Reuse a native agent while permitted; summarize before runtime-required cleanup; no history fork | Full session continuity and cache preservation are not guaranteed |
| Lead plans, reviews, and owns authority | Fusion skill and sidekick contract | Embedded lead and sidekick guidance |
| Design-level plans, settled interfaces and tests, optional snippets | Brief format and lead contract | Recovered base lead guidance; a stricter fragment also exists |
| Batch edits, verify narrowly, consolidate feedback | Both contracts | Embedded guidance |
| Critical measurement and query carve-outs | Main-agent ownership | Embedded lead guidance |
| First-edit and first-message reminders | Advisory hooks while active | Approximation; no reliable edit-role identifier |
| Sidekick runtime continuity | Main agent owns persistent processes | Deliberate Codex adaptation |
| Per-role compaction and backend model routing | Not implemented | No established plugin equivalent |
| Per-role dollar telemetry | Local rollout token totals | No price or quota equivalence claimed |

## Reproduce the local inspection

The prior investigation installed `~/.local/share/devin/cli/_versions/current/bin/devin`.
Extract strings locally with `strings -n 8 <binary> > /tmp/devin-strings.txt`.
Search for `You are the Sidekick subagent`, `first_edit_reminder`, and `local_fusion`.
The prior `/tmp/devin-re/strings8.txt` contains sidekick tool text near lines 2510–2560, lead guidance near 18890–18995,
and sidekick guidance near 19355–19420. Offsets depend on the exact build and extraction tool.
Source paths mention `chisel-agent/src/local_fusion/{mod,guidance,sidekick_tool,sidekick_inheritable}.rs`.
These strings establish embedded contracts, not verified execution of every branch.

## Runtime probe from the prior investigation

One subagent received two briefs through a reused conversation.
The first set a shell variable and launched a background heartbeat process.
The second observed an empty variable, a dead process, one heartbeat line, and a reset working directory.
This is evidence for that tested environment, not a universal claim about all Codex backends.
The implementation therefore does not depend on process persistence across sidekick handoffs.
The earlier recommendation to transfer Devin's surviving-runtime brief line unchanged is withdrawn.

## Official Codex contracts checked during implementation

- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents?surface=app): named agents, model pins, and native lifecycle.
- [Hooks](https://learn.chatgpt.com/docs/hooks): event schemas, additional context, tool coverage, and trust.

Tool hook payloads do not provide a stable main-agent/subagent identifier.
The plugin uses conditional edit reminders and makes no role-specific enforcement claim.
Sidekick grounding is supplied in the spawn brief. Dynamic selection uses the default agent with explicit model arguments.
Subagents inherit the user's sandbox configuration; the plugin does not relax it.

## Instruction fidelity

Lead instructions retain consequential design and correctness-critical authorship, including prompts and evaluation configuration. Sidekick briefs carry settled decisions; bounded implementation details remain discretionary. User updates are assessed before waiting, and relevant changes steer the running handoff.
The sidekick self-reviews, attempts bounded recovery, and returns evidence, including explicit visual-verification status.
Fusion assumes capable sidekicks throughout. It uses the recovered design-level brief guidance instead of requiring replacement snippets for every edit.
The [Cognition blog](https://cognition.com/blog/local-fusion#tuning-the-harness-for-different-model-pairings) supports more implementation discretion, planning-support exploration, and challenges from stronger sidekicks.
This plugin applies those boundaries uniformly at the user's requested policy boundary. It has no weak-sidekick setting or automatic capability classification.

### Evidence boundaries for the default guidance

For Devin CLI v3000.10.21 (611c1cba), the prior `strings -n 8` extraction contains:

- Lines 18928–18930: design-level lead plans, settled consequential interfaces and tests, with optional snippets.
- Lines 18956–18958: a separate stricter fragment requiring exact code locations, replacement snippets, and verification outcomes.
- Lines 18953–18955: exploration alternatives and assembly placeholders, without a verified selector.
- Lines 19359–19366: a persistent sidekick, authoritative supplied inputs, minor mismatch recovery, and batched blocker questions.

These line references use newline splitting (`split('\n')`); offsets depend on the extraction tool and binary.
The instructions use original plugin wording. Design-level briefs paraphrase recovered CLI text; encouraging planning-support discovery and evidence-backed challenges is a blog-supported adaptation.
No exact strong-sidekick challenge prompt was recovered. Searches for pushback-related strings did not locate one; this does not prove no such prompt exists.
Lead-framing and model-routing strings establish machinery, not the model-to-template mapping. No authenticated runtime trace verifies that mapping.
This is not a verified Devin strong-sidekick preset. Model-pair selection logic remains unreplicated.

## Selection decisions

Luna is a configurable local pairing choice, not a claim that it matches Cognition's SWE-2 economics.
The current main model stays selected. Main-agent retention avoids an unsolicited model change.
No recovered benchmark result establishes this plugin's cost or quality.
