# Handoff format

Omit fields that do not apply. Each brief should enable action without another planning round trip.

```text
Goal: <one verifiable outcome>
Workdir: <absolute checkout path>
Own: <files or bounded area; preserve others' changes>
Settled inputs: <facts and prior passing checks; do not re-derive>
Action: <what changes and why, relevant locations, settled interfaces/data shapes/helpers, hard edge cases, exact test cases/assertions/stubs>
```

Use fenced code when it expresses the settled design most clearly; do not supply every implementation line. Leave bounded implementation details to the sidekick.
For discovery, name the question and evidence required instead. Review the returned evidence and settle consequential choices before handing off implementation.
Invite evidence-backed concerns and proposed corrections; retain lead approval of consequential changes.

```text
Verify:
<verbatim command>
Pass: <observable result>
Constraints: <scope, permission boundary, main-agent-owned processes>
Continuity: <accepted facts and checks after runtime-required replacement; omit repeated context for the same agent>
Visual evidence: <required rendered states and screenshot paths, when applicable>
Report: changed paths, checks and results, evidence, blockers.
```

For rework, collect all findings into one brief. State which prior results remain accepted.
