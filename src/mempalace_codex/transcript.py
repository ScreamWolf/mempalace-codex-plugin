"""Normalization for the current Codex JSONL transcript format.

This module deliberately accepts only user messages and final assistant
answers.  Tool traffic, commentary, reasoning, and system/developer messages
are transport detail, not the verbatim conversation archive.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


# Current Codex writes these runtime-generated messages as role="user" inside
# response_item records.  They are not user-authored conversation and upstream
# MemPalace intentionally excluded the whole response_item stream for this
# reason.  Keep this list deliberately narrow: third-party or unrecognized
# content remains verbatim rather than being guessed away.
_CODEX_INJECTED_USER_PREFIXES = ("<recommended_plugins>", "<skill>")


@dataclass(frozen=True)
class TranscriptEntry:
    """One canonical, verbatim conversation record."""

    record_id: str
    offset: int
    end_offset: int
    role: str
    content: str


def _text_content(parts: object, expected_type: str) -> str | None:
    if not isinstance(parts, list):
        return None
    values = [part.get("text") for part in parts if isinstance(part, dict) and part.get("type") == expected_type]
    text = "\n".join(value for value in values if isinstance(value, str))
    return text or None


def _is_codex_injected_user_message(content: str) -> bool:
    return content.lstrip().startswith(_CODEX_INJECTED_USER_PREFIXES)


def entries_from_jsonl(path: Path, *, session_id: str, offset: int = 0) -> tuple[list[TranscriptEntry], int]:
    """Read canonical entries after ``offset`` and return the new byte cursor.

    A record identity includes the immutable source byte offset.  Repeated
    identical prompts remain distinct, while job retries stay idempotent.
    """
    entries: list[TranscriptEntry] = []
    with path.open("rb") as handle:
        handle.seek(offset)
        while raw_line := handle.readline():
            line_offset = handle.tell() - len(raw_line)
            end_offset = handle.tell()
            try:
                record = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            payload = record.get("payload")
            if record.get("type") != "response_item" or not isinstance(payload, dict) or payload.get("type") != "message":
                continue
            role = payload.get("role")
            if role == "user":
                content = _text_content(payload.get("content"), "input_text")
            elif role == "assistant" and payload.get("phase") == "final_answer":
                content = _text_content(payload.get("content"), "output_text")
            else:
                continue
            if content is None:
                continue
            if role == "user" and _is_codex_injected_user_message(content):
                continue
            digest = hashlib.sha256(f"{session_id}:{line_offset}:".encode() + raw_line).hexdigest()
            entries.append(TranscriptEntry(digest, line_offset, end_offset, role, content))
        return entries, handle.tell()
