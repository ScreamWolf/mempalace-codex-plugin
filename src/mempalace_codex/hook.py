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
    config = MempalaceConfig()
    original_extract = official._extract_recent_messages
    try:
        official._extract_recent_messages = _current_diary_messages
        result = official._save_diary_direct(transcript_path, session_id, wing="sessions", toast=config.hook_desktop_toast, agent_name=official._diary_agent_for_harness("codex"))
    finally:
        official._extract_recent_messages = original_extract
    _spawn_official_style_mine(transcript_path, "sessions")
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
        _spawn_official_style_mine(parsed["transcript_path"], "sessions")
    official._mine_sync()
    official._output({})


HANDLERS = {"SessionStart": hook_session_start, "Stop": hook_stop, "PreCompact": hook_precompact}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in HANDLERS:
        return 2
    output: dict[object, object] = {}
    original_output = None
    try:
        payload = json.load(sys.stdin)
        if isinstance(payload, dict):
            # Upstream hook helpers write their response directly to stdout.  A
            # Codex command hook must instead emit exactly one JSON document, so
            # capture that response and serialize it once after the handler.
            import mempalace.hooks_cli as official

            original_output = official._output

            def capture_output(data: dict[object, object]) -> None:
                nonlocal output
                output = data

            official._output = capture_output
            try:
                HANDLERS[sys.argv[1]](payload)
            finally:
                official._output = original_output
    except Exception:
        pass  # Hooks are deliberately fail-open; queued work is retried later.
    # Use the upstream writer after restoring it.  MemPalace's save path may
    # import ``mempalace.mcp_server``, which redirects fd 1 to stderr while
    # retaining the original hook response fd.  The upstream writer knows how
    # to recover that fd; a regular ``print`` here can therefore put the only
    # response on stderr and leave Codex with no JSON response.
    if original_output is None:
        print(json.dumps(output, ensure_ascii=False))
    else:
        original_output(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
