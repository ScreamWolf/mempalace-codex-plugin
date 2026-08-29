import json
from pathlib import Path
import tempfile
import unittest

from mempalace_codex.transcript import entries_from_jsonl


class TranscriptTests(unittest.TestCase):
    def test_keeps_only_user_and_final_assistant_messages(self) -> None:
        records = [
            {
                "type": "response_item",
                "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "你好"}]},
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "phase": "commentary",
                    "content": [{"type": "output_text", "text": "进度"}],
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "phase": "final_answer",
                    "content": [{"type": "output_text", "text": "完成"}],
                },
            },
            {"type": "event_msg", "payload": {"type": "item_completed"}},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "session.jsonl"
            path.write_bytes(b"".join(json.dumps(record, ensure_ascii=False).encode() + b"\n" for record in records))
            entries, offset = entries_from_jsonl(path, session_id="session")
        self.assertEqual([(entry.role, entry.content) for entry in entries], [("user", "你好"), ("assistant", "完成")])
        self.assertGreater(offset, 0)
        self.assertNotEqual(entries[0].record_id, entries[1].record_id)

    def test_offset_only_reads_appended_records(self) -> None:
        first = {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "一"}]}}
        second = {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "二"}]}}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "session.jsonl"
            path.write_bytes(json.dumps(first, ensure_ascii=False).encode() + b"\n")
            _, offset = entries_from_jsonl(path, session_id="session")
            with path.open("ab") as handle:
                handle.write(json.dumps(second, ensure_ascii=False).encode() + b"\n")
            entries, _ = entries_from_jsonl(path, session_id="session", offset=offset)
        self.assertEqual([entry.content for entry in entries], ["二"])

    def test_excludes_only_known_codex_injected_user_messages(self) -> None:
        records = [
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "<recommended_plugins>generated list</recommended_plugins>"}],
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "<skill>generated instructions</skill>"}],
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "请处理第三方工具提供的 <context>内容</context>"}],
                },
            },
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "session.jsonl"
            path.write_bytes(b"".join(json.dumps(record, ensure_ascii=False).encode() + b"\n" for record in records))
            entries, _ = entries_from_jsonl(path, session_id="session")
        self.assertEqual([entry.content for entry in entries], ["请处理第三方工具提供的 <context>内容</context>"])
