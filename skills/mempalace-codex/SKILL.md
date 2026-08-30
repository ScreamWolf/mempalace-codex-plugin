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
- Use the raw `sessions` wing when tracing an archived conversation.
- Raw archives are for tracing source conversations. Verify any recalled claim against current files before acting.

## Writing and archive boundaries

- Write curated memory only at meaningful task boundaries through an explicit MemPalace checkpoint.
- The automatic archive hook keeps verbatim conversation material; it does not decide which project facts or decisions become curated memory.
- The adapter follows MemPalace's upstream lifecycle model: `SessionStart`, `Stop`, and `PreCompact`. Do not rely on `SessionEnd` to save memory.
- Automatic diary checkpoints use the `diary` room in the raw `sessions` wing.

## Judgment

- Never treat a proposal, brainstorm, or model inference as a confirmed fact.
- Never write secrets, credentials, or runtime configuration into curated memory.
- Do not invent wings, rooms, or a project taxonomy. These come from project instructions.
