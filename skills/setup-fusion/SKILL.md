---
name: setup-fusion
description: Initialize or inspect Fusion's live model settings when the user asks to set up Fusion, configure Fusion, or invokes $setup-fusion. Preserve existing settings unless the user requests changes.
---

# Set up Fusion

Resolve the installed plugin root as two directories above this skill directory.
Use that absolute root for helper commands; do not assume the user's working directory contains the plugin source.

When upgrading from the old `~/.config/codex-fusion/models.json` location, preserve the existing choices using [the migration steps](../../docs/installation.md#existing-settings) before initialization.

Run `python3 <plugin-root>/scripts/model_config.py init`.
This initializes a missing registry from shipped defaults and validates an existing registry without overwriting it.
Honor `FUSION_MODELS_FILE` when set. Otherwise the registry is `$CODEX_HOME/plugins/fusion/models.json`.
Use `~/.codex` when `CODEX_HOME` is unset or empty. This registry is outside the versioned plugin cache.
If the registry is invalid, report the specific error. Preserve the file until the user authorizes a repair.
If the sandbox blocks the selected directory, use the normal approval path. Do not relocate settings or change permissions to bypass it.
If access remains blocked, provide the exact initialization command with the installed absolute helper path.

If the user supplied model choices, apply only those requested fields to the live registry.
Validate the candidate with the helper's `validate` function before replacing the file atomically.
Preserve other fields and do not write local choices into the plugin, its cache, or shipped defaults.
Do not substitute another model identifier or claim runtime support from schema validation alone.

Run `python3 <plugin-root>/scripts/model_config.py show` to confirm the resulting file and settings.
Explain that the current conversation keeps its model by default; the configured lead applies to delegated Fusion runs.
Sidekick changes take effect at the next handoff without reinstalling the plugin.
Report the registry path, effective configured roles, and whether setup created or preserved the file.
Only claim a file was newly created if its absence was observed before initialization; otherwise report that it is ready.

Tell the user to invoke `$fusion` for a coding task. Setup itself does not activate Fusion or start agents.
Hooks are optional advisory reminders. If the user wants them, direct them to review the plugin hooks through `/hooks`.
Do not enable or bypass hook trust, reinstall plugins, change global model defaults, or launch model probes as part of setup.
