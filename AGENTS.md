# MemPalace Codex Plugin

This repository is the Codex-specific integration layer for MemPalace. It replaces the upstream MemPalace Codex plugin when installed; never enable both for the same Codex profile.

## Compatibility baseline

- Track the latest official **stable release** of MemPalace, not its `develop` branch.
- The adapter is currently tested against `v3.8.0`; this is a test baseline, not a package-version constraint.
- Keep `.mcp.json` and the copied upstream skills behaviorally aligned with the tested release, and re-test after upstream upgrades.
- Record each intentional divergence from upstream in the README and tests.

## Curated memory rooms

For this project's MemPalace wing, use only these rooms:

- `architecture` — confirmed plugin boundaries, integration decisions, and configuration contracts.
- `compatibility` — verified upstream/Codex versions, compatibility findings, and intentional divergences.
- `diary` — automatic verbatim session archives for traceability; do not use it as curated project guidance.

Create curated memories only for durable, confirmed facts. Current repository files and explicit user instructions take precedence over recalled memory.

## Responsibilities

- The MemPalace CLI/MCP owns storage, search, checkpoints, and knowledge-graph behavior.
- This plugin owns Codex MCP registration, plugin-provided lifecycle wiring, raw-session archive adaptation, installation, and Codex-specific guidance.
- Custom hooks adapt current Codex transcripts and archive only verbatim user and final assistant messages. With a private project mapping they use `sessions_<project>`; without one they preserve the upstream `sessions` wing. They do not create curated project memory.

## Public-repository boundaries

- Never commit user paths, project mappings, tokens, API keys, transcript content, hook state, or generated user configuration.
- Keep examples generic and use placeholders.
- Do not modify or copy upstream's Codex hook implementation without an explicit, tested compatibility reason.

## Hook requirements

- Treat Codex hook payloads and transcripts as versioned, untrusted input.
- Do not assume a payload contains `transcript_path`; validate against real fixtures.
- Preserve the upstream lifecycle semantics: `SessionStart` initializes routing, `Stop` applies the configured threshold and invokes the upstream-style diary/archive path, and `PreCompact` starts an upstream-style archive pass.
- Keep the three lifecycle registrations in `hooks/hooks.json`; do not add `SessionEnd`, a user-level hook registration, a private queue, or a private cursor unless a demonstrated upstream incompatibility requires it.
- Hook failures must not block or alter the Codex conversation.

## Quality bar

- Add synthetic fixtures and tests before supporting a new Codex transcript shape. Do not retain real conversation payloads in the repository.
- Validate the plugin manifest after changes with the bundled plugin validator.
- Keep the Chinese README authoritative and update `README.en.md` whenever its public behavior changes.
