# MemPalace Codex Plugin

This repository is the Codex-specific integration layer for MemPalace. It replaces the upstream MemPalace Codex plugin when installed; never enable both for the same Codex profile.

## Compatibility maintenance

- Track the latest official **stable release** of MemPalace, not its `develop` branch.
- Keep `.mcp.json` and copied upstream skills behaviorally aligned with the chosen upstream release, and re-test after upstream upgrades.
- Record each intentional divergence from upstream in the README and tests.
- Store the currently verified upstream version and other changeable compatibility facts in the project knowledge graph, with test evidence in the `compatibility` drawer.

## Curated memory rooms

This project's current MemPalace wing is `mempalace_codex_plugin`. The KG room registry at `project:mempalace_codex_plugin:memory` is authoritative for curated-memory rooms and their purposes.

Historical automatic diary entries may exist under the project wing, but they are traceability only. New Hook checkpoints are not curated project guidance.

Create curated memories only for durable, confirmed facts. Current repository files and explicit user instructions take precedence over recalled memory.

## Responsibilities

- The MemPalace CLI/MCP owns storage, search, checkpoints, and knowledge-graph behavior.
- This plugin owns Codex MCP registration, plugin-provided lifecycle wiring, raw-session archive adaptation, installation, and Codex-specific guidance.
- Custom hooks adapt Codex transcripts for upstream-style raw-session archiving. Automatic checkpoints do not create curated project memory.

## Public-repository boundaries

- Never commit user paths, tokens, API keys, transcript content, hook state, or generated user configuration.
- Keep examples generic and use placeholders.
- Do not modify or copy upstream's Codex hook implementation without an explicit, tested compatibility reason.

## Hook requirements

- Treat Codex hook payloads and transcripts as versioned, untrusted input.
- Do not assume a payload contains `transcript_path`; validate against real fixtures.
- Preserve upstream lifecycle semantics, including routing initialization, threshold-based archival, and archival before compaction.
- Change lifecycle registration or introduce private archival state only for a demonstrated upstream incompatibility, with focused compatibility tests.
- Hook failures must not block or alter the Codex conversation.

## Quality bar

- Add synthetic fixtures and tests before supporting a new Codex transcript shape. Do not retain real conversation payloads in the repository.
- Validate the plugin manifest after changes with the bundled plugin validator.
- Keep the Chinese README authoritative and update `README.en.md` whenever its public behavior changes.
