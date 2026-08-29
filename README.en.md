<div align="center">

# MemPalace Codex Plugin

[简体中文](README.md) | English

</div>

An independent Codex adapter for [MemPalace](https://github.com/MemPalace/mempalace). MemPalace is responsible for storage, search, checkpoints, and the knowledge graph; this project provides only Codex MCP registration, session archiving, and usage guidance.

It has been tested with MemPalace `v3.8.0`. It replaces the upstream Codex plugin; enable only one of them in the same Codex profile.

## Scope

- Registers the upstream `mempalace-mcp` without modifying its MCP tools or MemPalace CLI behavior.
- Provides `SessionStart`, `Stop`, and `PreCompact` Hooks through the plugin itself.
- Archives verbatim user messages and final assistant replies from the current Codex JSONL format; skips system messages, tool protocol, and confirmed Codex-injected content (`<recommended_plugins>` and `<skill>`).
- Archives on normal `Stop` every 15 user turns by default; `PreCompact` always starts an archive pass.
- Keeps the five upstream skills—`help`, `init`, `mine`, `search`, and `status`—and adds `mempalace-codex` to explain project-scoped recall, explicit checkpoints, and the boundary around raw-session archives.

## Differences from the upstream plugin

| Area | This plugin |
| --- | --- |
| MCP and generic skills | Reuses MemPalace MCP and generic skills; tested with `v3.8.0`. |
| Hook registration | Uses the plugin's `hooks/hooks.json`; does not use user-level Hooks. |
| Lifecycle | Handles `SessionStart`, `Stop`, and `PreCompact` only; does not handle `SessionEnd`. |
| Transcript parsing | Supports the current Codex JSONL format, saves only user and final assistant text, and filters two confirmed Codex injection markers. |
| Stop cadence | Every 15 user turns by default; configurable through plugin settings or an environment variable. |
| Project isolation | An optional `[projects]` mapping routes raw archives to `sessions_<project-name>`; without it, archives remain in upstream `sessions`. |

## Install

### 1. Deploy and configure MemPalace

Follow the [MemPalace installation and configuration guide](https://mempalaceofficial.com/guide/configuration.html) to configure the backend, palace path, and embedding provider. Then confirm this command works:

```bash
mempalace status
```

Install the MemPalace CLI:

```bash
uv tool install mempalace
```

### 2. Install the Hook runner

It must be on Codex's `PATH` so the plugin Hooks can start it:

```bash
uv tool install "git+https://github.com/ScreamWolf/mempalace-codex-plugin.git@main"
```

Confirm both commands resolve:

```bash
command -v mempalace-mcp
command -v mempalace-codex-hook
```

If your system does not add uv's tool directory to `PATH`, fix that environment setting before installing the plugin.

### 3. Install the plugin in Codex

Add this repository as a marketplace, then install the plugin:

```bash
codex plugin marketplace add ScreamWolf/mempalace-codex-plugin
codex plugin add mempalace-codex-plugin@mempalace-codex-plugin
```

You can also install it from this marketplace in the Codex Desktop Plugins directory. At first enablement, Codex will ask you to review and trust the plugin Hooks; this is an expected security boundary. After installation or an upgrade, start a new task so MCP and skills load from the new plugin copy.

## Configuration

Optional configuration lives at `~/.config/mempalace-codex/config.toml`:

```toml
[archive]
# Number of user turns accumulated after Stop before archiving; defaults to 15.
interval_user_turns = 15

[projects]
# A match for this directory or one of its children archives raw sessions to sessions_my-app.
"/Users/you/apps/my-app" = "my-app"
```

Project mappings use the longest matching directory prefix. When one matches:

- Raw sessions are written to `sessions_<project-name>`.
- The automatic diary checkpoint is written to that project wing.

Without a mapping, for projectless sessions, or when no working directory is available, raw sessions retain the upstream default `sessions` wing. Explicit checkpoints still go to the wing / room you specify through the MemPalace MCP and are not constrained by this mapping.

Temporarily override the archive interval with an environment variable:

```bash
MEMPALACE_CODEX_ARCHIVE_INTERVAL=5
```

## License

MIT
