---
name: mempalace-codex
description: Use the configured MemPalace MCP integration for scoped recall, explicit project checkpoints, and raw-session archive-aware work in Codex.
user-invocable: false
---

# MemPalace for Codex

Use this skill only for the Codex-specific integration behavior. The copied
upstream MemPalace skills remain the source of truth for the individual MCP
tools.

## Recall

- Treat current user instructions, current project files, and project instructions as more authoritative than recalled memory.
- When historical context matters, search the current project's curated wing before relying on prior work.
- If the user has a private `[projects]` mapping for the current working directory, use the mapped project name to search the matching raw archive wing: `sessions_<project-name>`.
- If no mapping applies, preserve upstream behavior and use the raw `sessions` wing.
- Raw archives are for tracing source conversations. Verify any recalled claim against current files before acting.

## Writing and archive boundaries

- Write curated memory only at meaningful task boundaries through an explicit MemPalace checkpoint.
- The automatic archive hook keeps verbatim conversation material; it does not decide which project facts or decisions become curated memory.
- The adapter follows MemPalace's upstream lifecycle model: `SessionStart`, `Stop`, and `PreCompact`. Do not rely on `SessionEnd` to save memory.
- Automatic diary checkpoints use the current curated project wing when a mapping applies; otherwise they keep upstream's default wing behavior.

## Judgment

- Never treat a proposal, brainstorm, or model inference as a confirmed fact.
- Never write secrets, credentials, or runtime configuration into curated memory.
- Do not invent project mappings, wings, rooms, or a project taxonomy. These are private user configuration and project instructions.
