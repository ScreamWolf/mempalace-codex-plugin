import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
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

    def test_main_emits_one_json_document_for_every_lifecycle_hook(self) -> None:
        script = textwrap.dedent(
            """
            import sys
            import mempalace.hooks_cli as official
            from mempalace_codex import hook

            event = sys.argv[1]

            def emitting_handler(_):
                official._output({"systemMessage": "archived"})

            hook.HANDLERS[event] = emitting_handler
            sys.argv = ["mempalace-codex-hook", event]
            raise SystemExit(hook.main())
            """
        )

        for event in HANDLERS:
            with self.subTest(event=event):
                completed = subprocess.run(
                    [sys.executable, "-c", script, event],
                    input="{}",
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(completed.returncode, 0, completed.stderr)
                decoded, end = json.JSONDecoder().raw_decode(completed.stdout)
                self.assertEqual(decoded, {"systemMessage": "archived"})
                self.assertFalse(completed.stdout[end:].strip())
                self.assertEqual(completed.stderr, "")

    def test_main_uses_original_stdout_after_mempalace_redirects_fd_one(self) -> None:
        script = textwrap.dedent(
            """
            import sys
            import mempalace.hooks_cli as official
            from mempalace_codex import hook

            def redirecting_handler(_):
                import mempalace.mcp_server
                official._output({"systemMessage": "archived"})

            hook.HANDLERS["Stop"] = redirecting_handler
            sys.argv = ["mempalace-codex-hook", "Stop"]
            raise SystemExit(hook.main())
            """
        )
        completed = subprocess.run(
            [sys.executable, "-c", script],
            input="{}",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        decoded, end = json.JSONDecoder().raw_decode(completed.stdout)
        self.assertEqual(decoded, {"systemMessage": "archived"})
        self.assertFalse(completed.stdout[end:].strip())
        self.assertEqual(completed.stderr, "")

    def test_main_fails_open_with_one_json_document_for_invalid_payloads(self) -> None:
        for payload in ("{", "[]", "null"):
            with self.subTest(payload=payload):
                completed = subprocess.run(
                    [sys.executable, "-m", "mempalace_codex.hook", "Stop"],
                    input=payload,
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(completed.returncode, 0, completed.stderr)
                decoded, end = json.JSONDecoder().raw_decode(completed.stdout)
                self.assertEqual(decoded, {})
                self.assertFalse(completed.stdout[end:].strip())
                self.assertEqual(completed.stderr, "")
