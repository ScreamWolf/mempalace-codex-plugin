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
| Automatic archive location | Raw sessions always go to the `sessions` wing; automatic diary checkpoints use that wing's `diary` room. |

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
command -v mempalace-codex-mcp
```

If your system does not add uv's tool directory to `PATH`, fix that environment setting before installing the plugin.

### 3. Install the plugin in Codex

Add this repository as a marketplace, then install the plugin:

```bash
codex plugin marketplace add ScreamWolf/mempalace-codex-plugin
codex plugin add mempalace-codex-plugin@mempalace-codex-plugin
```

You can also install it from this marketplace in the Codex Desktop Plugins directory. At first enablement, Codex will ask you to review and trust the plugin Hooks; this is an expected security boundary. After installation or an upgrade, start a new task so MCP and skills load from the new plugin copy.

## Upgrade

The Codex plugin copy and the Hook runner installed as a `uv tool` are separate
installations. Reinstalling only the Codex plugin does not refresh the runner;
update both when upgrading:

```bash
uv tool install --force --refresh "git+https://github.com/ScreamWolf/mempalace-codex-plugin.git@main"
codex plugin add mempalace-codex-plugin@mempalace-codex-plugin
```

Then start a new task to verify `SessionStart` and load the updated MCP, skills,
and Hooks.

## Configuration

Optional configuration lives at `~/.config/mempalace-codex/config.toml`:

```toml
[archive]
# Number of user turns accumulated after Stop before archiving; defaults to 15.
interval_user_turns = 15

[mcp]
# Enable only when MemPalace uses a service backend that coordinates concurrent
# writers, such as Qdrant or pgvector. The upstream MCP still enforces one
# writer for local Chroma-style backends.
allow_peer_writer = false
```

The Hook does not infer a project from the working directory, Codex Project, or Git worktree. Raw sessions always go to the `sessions` wing, and automatic diary checkpoints use that wing's `diary` room. Explicit checkpoints still go to the wing / room you specify through the MemPalace MCP and are not constrained by the automatic archive location. MemPalace's separate daily-summary file ingestion is not part of this Hook and is unchanged.

Temporarily override the archive interval with an environment variable:

```bash
MEMPALACE_CODEX_ARCHIVE_INTERVAL=5
```

When multiple Codex projects share one Qdrant / pgvector palace, set
`[mcp].allow_peer_writer` to `true`. The plugin injects the corresponding
upstream environment variable only when it launches `mempalace-mcp`; the
default remains `false`, preserving official single-writer behavior.

## License

MIT
