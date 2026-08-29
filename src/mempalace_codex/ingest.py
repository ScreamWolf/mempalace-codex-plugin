"""Bridge the current Codex JSONL schema into MemPalace's official miner."""

from __future__ import annotations

from pathlib import Path
import sys

from .transcript import entries_from_jsonl


def normalize_current_codex(filepath: str) -> list[str]:
    """Return the official transcript representation for current Codex JSONL."""
    entries, _ = entries_from_jsonl(Path(filepath), session_id="normalizer", offset=0)
    messages = [(entry.role, entry.content) for entry in entries]
    if len(messages) < 2:
        return []
    from mempalace.normalize import _messages_to_transcript

    return [_messages_to_transcript(messages)]


def mine_transcript(transcript_path: str, wing: str = "sessions") -> None:
    """Run MemPalace's own conversation miner with only its parser replaced."""
    from mempalace.config import MempalaceConfig
    import mempalace.convo_miner as convo_miner

    original_normalizer = convo_miner.normalize_conversations
    try:
        convo_miner.normalize_conversations = normalize_current_codex
        convo_miner.mine_convos(transcript_path, palace_path=MempalaceConfig().palace_path, wing=wing, agent="mempalace")
    finally:
        convo_miner.normalize_conversations = original_normalizer
        from mempalace.miner import _cleanup_mine_pid_file

        _cleanup_mine_pid_file()


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] != "mine":
        return 2
    try:
        mine_transcript(sys.argv[2], sys.argv[3])
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
