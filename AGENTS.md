# Project boundaries

Read `~/.agents/AGENTS.md` before work when it exists.
Keep Fusion independent from pstack and coordinator. Use current official Codex documentation and live tool schemas for runtime changes.
Preserve one sidekick per Fusion lead, bounded handoffs, main-agent acceptance, and the user's permission boundaries.
Advisory hooks are not an access-control boundary. Bookkeeping does not prove native agent state.

Use Python's standard library unless a dependency has a concrete benefit. Run `python3 scripts/check.py` before committing.
Test changes to session state, model resolution, replacement decisions, and token accounting.
Keep runtime state, user model settings, credentials, raw rollouts, and extracted third-party prompts out of Git.
Write research documentation in original prose with public references.

## Live model configuration

The user's live registry is `$CODEX_HOME/plugins/fusion/models.json`, or the path selected by `FUSION_MODELS_FILE`.
Read it before every handoff. Changes must not require plugin reinstallation.
Keep shipped defaults in `config/models.default.json`; never overwrite an existing user registry during setup or release.
A model change takes effect at a handoff boundary. Never claim it changes an in-flight call.
The current main model stays selected by default. Delegated Fusion runs resolve the configured lead.

## Git workflow

Use $review-before-push before any push, PR creation, or PR update.
Read its shared instructions at `~/.agents/skills/review-before-push/SKILL.md`.
Review the complete outgoing diff and fix confirmed findings before publishing.

Use pull requests for substantive changes after the initial reviewed repository bootstrap.
Small, non-behavioral changes may go directly to `main`.
Describe the problem, intended behavior, tradeoffs, and validation in each PR.
Merge with a merge commit. Preserve individual commits; do not squash or rebase when merging.
Include the problem, approach, and PR reference in the merge message.
Monitor GitHub checks to completion and investigate failures.

## Local plugin updates

Keep the installed plugin aligned with reviewed `main` after each push or merge.
A branch push does not authorize merging or installing unmerged work. Report pending integration separately.
Before the final commit, update the cachebuster:

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py" "$(git rev-parse --show-toplevel)"
```

Include that manifest change in the reviewed commit. Run `python3 scripts/check.py` afterward.
Follow [the installation procedure](docs/installation.md) to resolve the local marketplace and reinstall.
Verify the marketplace source is the intended clean reviewed checkout before installation.
Do not change marketplace configuration to conceal a source mismatch. Preserve unrelated work and the live model registry.
Record the source commit and installed version. Compare installed files with the reviewed source.
Verify namespaced skill loading in a fresh task after runtime changes. Existing tasks do not prove an update loaded.
Report push, main integration, installation, and runtime verification separately.
