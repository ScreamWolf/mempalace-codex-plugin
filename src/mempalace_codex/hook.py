"""Codex lifecycle adapter preserving MemPalace v3.8.0 hook semantics."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from .config import load_archive_settings
from .transcript import entries_from_jsonl

def _current_user_count(transcript_path: str, session_id: str) -> int:
    try:
        entries, _ = entries_from_jsonl(Path(transcript_path), session_id=session_id)
    except OSError:
        return 0
    return sum(entry.role == "user" for entry in entries)


def _current_diary_messages(transcript_path: str, count: int = 30) -> list[str]:
    try:
        entries, _ = entries_from_jsonl(Path(transcript_path), session_id="diary")
    except OSError:
        return []
    return [entry.content.strip()[:200] for entry in entries if entry.role == "user" and entry.content.strip()][-count:]


def _spawn_official_style_mine(transcript_path: str, wing: str) -> None:
    from mempalace.hooks_cli import _spawn_mine

    _spawn_mine([sys.executable, "-m", "mempalace_codex.ingest", "mine", transcript_path, wing])


def _wing_from_payload(data: dict[str, object], transcript_path: str) -> str:
    """Use Codex's canonical Hook cwd before the upstream transcript fallback."""
    cwd = data.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        from mempalace.config import normalize_wing_name

        return normalize_wing_name(Path(cwd).name)
    from mempalace.hooks_cli import _wing_from_transcript_path

    return _wing_from_transcript_path(transcript_path)


def _archive_wing(data: dict[str, object]) -> tuple[str, str | None]:
    cwd = data.get("cwd")
    if not isinstance(cwd, str) or not cwd.strip():
        return "sessions", None
    project = load_archive_settings().project_wing_for_cwd(cwd)
    return (f"sessions_{project}", project) if project else ("sessions", None)


def hook_session_start(data: dict[str, object]) -> None:
    from mempalace.hooks_cli import hook_session_start as official_session_start

    official_session_start(data, "codex")


def hook_stop(data: dict[str, object]) -> None:
    """Official Stop flow with only current-Codex parsing substituted."""
    from mempalace.config import MempalaceConfig
    import mempalace.hooks_cli as official

    if not official._palace_root_exists() or not MempalaceConfig().hooks_auto_save:
        official._output({})
        return
    parsed = official._parse_harness_input(data, "codex")
    session_id, transcript_path = parsed["session_id"], parsed["transcript_path"]
    if str(parsed["stop_hook_active"]).lower() in ("true", "1", "yes") and not MempalaceConfig().hook_silent_save:
        official._output({})
        return
    exchange_count = _current_user_count(transcript_path, session_id)
    official.STATE_DIR.mkdir(parents=True, exist_ok=True)
    marker = official.STATE_DIR / f"{session_id}_last_save"
    try:
        last_save = int(marker.read_text().strip())
    except (OSError, ValueError):
        last_save = 0
    if exchange_count - last_save < load_archive_settings().interval_user_turns or exchange_count == 0:
        official._output({})
        return
    archive_wing, configured_project_wing = _archive_wing(data)
    config = MempalaceConfig()
    wing = configured_project_wing or _wing_from_payload(data, transcript_path)
    original_extract = official._extract_recent_messages
    try:
        official._extract_recent_messages = _current_diary_messages
        result = official._save_diary_direct(transcript_path, session_id, wing=wing, toast=config.hook_desktop_toast, agent_name=official._diary_agent_for_harness("codex"))
    finally:
        official._extract_recent_messages = original_extract
    _spawn_official_style_mine(transcript_path, archive_wing)
    if result.get("count", 0) > 0:
        marker.write_text(str(exchange_count), encoding="utf-8")
    official._output({})


def hook_precompact(data: dict[str, object]) -> None:
    """Official PreCompact behavior: launch the same transcript mine."""
    from mempalace.config import MempalaceConfig
    import mempalace.hooks_cli as official

    if not official._palace_root_exists() or not MempalaceConfig().hooks_auto_save:
        official._output({})
        return
    parsed = official._parse_harness_input(data, "codex")
    if parsed["transcript_path"]:
        archive_wing, _ = _archive_wing(data)
        _spawn_official_style_mine(parsed["transcript_path"], archive_wing)
    official._mine_sync()
    official._output({})


HANDLERS = {"SessionStart": hook_session_start, "Stop": hook_stop, "PreCompact": hook_precompact}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in HANDLERS:
        return 2
    try:
        payload = json.load(sys.stdin)
        if isinstance(payload, dict):
            HANDLERS[sys.argv[1]](payload)
    except Exception:
        pass  # Hooks are deliberately fail-open; queued work is retried later.
    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
