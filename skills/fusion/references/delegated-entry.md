# Delegating a Fusion run

If `prepare` returned `delegate_lead`, use those returned `spawn_args` without resolving again.
An external caller that explicitly delegates a Fusion run resolves the configured lead before spawning it:

```sh
python3 <plugin-root>/scripts/model_config.py resolve --role lead --context delegated
```

Use the returned `spawn_args` with a bounded task message and `fork_context: false`.
Include the absolute Fusion skill path and this role marker:

```text
You are the Fusion lead for this delegated task. Do not spawn another lead.
Read the supplied Fusion skill and operate its lead/sidekick loop yourself.
Task: <goal, checkout, scope, accepted facts, required checks, and return contract>.
```

The designated Fusion lead runs `fusion.py prepare --entry lead` in its own thread before each handoff; it must not run initial-entry preparation and select another lead. The caller waits for the integrated result.
The lead keeps authority within the caller's brief and returns evidence. The caller owns final user communication and broader integration.
This intentionally adds a caller above the two-agent Fusion pair. It does not permit sidekick nesting.
The runtime must support the additional delegation depth; if it does not, report the limitation rather than recursively retrying.
An existing Fusion lead must honor the role marker and never apply delegated entry again.

`lead.use_current_model: false` requests this same delegated entry from a direct invocation.
It does not mutate the model of the existing conversation.
Lead setting changes affect the next delegated Fusion run. They do not restart an active lead or discard its work.
Creating a separate user-visible task still requires an explicit user request. This contract uses native subagents.
