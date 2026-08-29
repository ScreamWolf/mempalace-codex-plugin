import json
from pathlib import Path
import tempfile
import unittest
from mempalace_codex.hook import HANDLERS, _current_diary_messages, _current_user_count


class HookTests(unittest.TestCase):
    def test_only_officially_selected_lifecycle_events_are_registered(self) -> None:
        self.assertEqual(set(HANDLERS), {"SessionStart", "Stop", "PreCompact"})

    def test_current_codex_user_count_and_diary_source(self) -> None:
        records = [
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "第一条"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "assistant", "phase": "final_answer", "content": [{"type": "output_text", "text": "回答"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "第二条"}]}},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            transcript = Path(temporary) / "session.jsonl"
            transcript.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records), encoding="utf-8")
            self.assertEqual(_current_user_count(str(transcript), "session"), 2)
            self.assertEqual(_current_diary_messages(str(transcript)), ["第一条", "第二条"])
