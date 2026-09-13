# Installation and local reload

The personal marketplace entry uses `~/plugins/fusion`.
On the development machine, that directory is a tracked-file export of reviewed `main` from `~/Projects/codex-fusion-plugin`.
The default personal marketplace file is `~/.agents/plugins/marketplace.json`.
Do not add the default personal marketplace explicitly with a marketplace-add command.

## Initial setup

Use the plugin-creator scaffold workflow to add the personal entry when installing on another machine.
Populate its local source from a clean tracked-file export of this checkout. Preserve existing marketplace entries.
Run `python3 scripts/model_config.py init` once. This preserves an existing valid live registry.

## Reload plugin code

1. Complete the required review and validation before pushing.
2. Confirm `main` and the marketplace source contain the intended reviewed commit with no uncommitted source changes.
3. Resolve the marketplace name with the plugin-creator helper:

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/read_marketplace_name.py"
codex plugin list --marketplace personal --available --json
```

Use the returned marketplace name if it differs from `personal`.
Update the cachebuster before the reviewed commit as described in `AGENTS.md`.
Export the reviewed commit into a fresh directory, then replace the old plugin source only after checking its ownership.
Use `git archive HEAD` to include tracked files only. Preserve the external live model registry.
Reinstall only when the source is correct:

```sh
codex plugin add fusion@personal
```

Compare the installed files and manifest version with the reviewed source.
Start a fresh task and invoke `fusion:fusion` to verify discovery after runtime changes.
Hook execution also requires Codex hook trust; review the hooks through `/hooks` as needed.
Do not claim live hook delivery from unit tests alone.

## Change models without reloading

Edit `~/.config/codex-fusion/models.json`. No cachebuster, commit, reinstall, or new task is needed for these edits.
Run `python3 scripts/model_config.py show` to validate the file and see its revision.
The lead reads it before each handoff through `fusion.py dispatch`.
Model or effort changes replace the sidekick after the current handoff finishes.
Lead settings apply to the next delegated run; the current main model remains selected by default.
