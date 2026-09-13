# Install Fusion

Use a Codex version with plugin and subagent support. Python 3.10 or newer must be available as `python3`.
Git must be able to read the repository. Private repositories require Git authentication and repository access.

## Install from GitHub

```sh
codex plugin marketplace add nahuelb/codex-fusion-plugin
codex plugin add fusion@fusion-marketplace
```

The first command registers the repository's marketplace. The second installs Fusion from that marketplace.
Start a fresh Codex task after installation. Then send:

```text
Use $setup-fusion to set up Fusion.
```

You can also ask Codex to “set up Fusion.” The `fusion:setup-fusion` skill initializes the external model registry.
It preserves an existing valid configuration. Setup does not activate the coding workflow or start agents.
After setup, send `Use $fusion to implement <task>`.

The default sidekick is Luna at xhigh. Direct invocation keeps the current main model.
The configured Astra lead is used when another agent delegates a Fusion run.
Configured models must be available in your Codex runtime. Setup validates configuration, not model access.

## Update

```sh
codex plugin marketplace upgrade fusion-marketplace
codex plugin add fusion@fusion-marketplace
```

Start a fresh task to load updated plugin code. Model settings remain in the external registry.
Do not run setup again unless you want to inspect or change those settings.

## Install a local checkout

```sh
git clone https://github.com/nahuelb/codex-fusion-plugin.git
cd codex-fusion-plugin
codex plugin marketplace add .
codex plugin add fusion@fusion-marketplace
```

Choose either the GitHub source or the local source for `fusion-marketplace`.
If that marketplace name is already registered, inspect `codex plugin marketplace list` before switching its source.
A local source reads the checkout. Reinstall after pulling reviewed changes; marketplace upgrade is for Git sources.

## Models and hooks

`$setup-fusion` uses `$CODEX_HOME/plugins/fusion/models.json`, or `FUSION_MODELS_FILE` when set on the Codex host.
When `CODEX_HOME` is unset or empty, it defaults to `~/.codex`. The registry stays outside the versioned plugin cache.
Edit that file or ask setup to change specific model fields. Existing unrelated settings are preserved.
No cachebuster, reinstall, or new task is needed for model edits.
The lead reads the file before each handoff. Model or effort changes replace the sidekick after its current handoff finishes.
Lead changes apply to the next delegated run.

Hooks require Codex hook trust. Review the plugin hooks through `/hooks` if you want the advisory reminders.
The core skill works without hooks. Setup does not enable hook trust automatically.

## Existing settings

Earlier versions used `~/.config/codex-fusion/models.json`.
When upgrading, validate that file before setup and copy it to the new registry path only if the destination is absent.
Preserve the original as a backup. Never overwrite an existing destination or silently replace an invalid source with defaults.
An explicit `FUSION_MODELS_FILE` continues to select its own file; do not migrate it automatically.
For an intentionally separate `CODEX_HOME`, initialize separate settings unless the user requests importing the old choices.

## Maintainer reloads

Complete review and checks before publishing. Update the plugin cachebuster before the final reviewed commit, as described in `AGENTS.md`.
Use the installation's existing marketplace instead of changing its source to conceal unmerged changes.

For a personal development installation, resolve the actual marketplace name and source:

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/read_marketplace_name.py"
codex plugin list --marketplace personal --available --json
```

The default personal marketplace is discovered implicitly. Do not register it through marketplace-add.
Refresh its plugin source from a clean tracked-file export of reviewed `main`, using `git archive HEAD`.
Preserve the external registry. Then run `codex plugin add fusion@personal`, substituting the resolved marketplace name when needed.
Compare installed files and the manifest version with that reviewed source.
Verify the skill in a fresh task. An existing task or a registry listing does not prove the update loaded.

The underlying initialization command remains available for automation:
`python3 <installed-plugin-root>/scripts/model_config.py init`.
Normal interactive setup uses `$setup-fusion`.

See [official Codex plugin guidance](https://learn.chatgpt.com/docs/plugins) for the plugin lifecycle.
