import os
from pathlib import Path
import tempfile
import unittest

from mempalace_codex.config import DEFAULT_ARCHIVE_INTERVAL, ENV_ARCHIVE_INTERVAL, load_archive_settings


class ArchiveSettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous_env = os.environ.pop(ENV_ARCHIVE_INTERVAL, None)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config = Path(self.temp_dir.name) / "config.toml"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        if self.previous_env is not None:
            os.environ[ENV_ARCHIVE_INTERVAL] = self.previous_env

    def test_missing_config_uses_default(self) -> None:
        self.assertEqual(load_archive_settings(self.config).interval_user_turns, DEFAULT_ARCHIVE_INTERVAL)

    def test_config_allows_custom_interval(self) -> None:
        self.config.write_text("[archive]\ninterval_user_turns = 6\n", encoding="utf-8")
        self.assertEqual(load_archive_settings(self.config).interval_user_turns, 6)

    def test_environment_overrides_config(self) -> None:
        self.config.write_text("[archive]\ninterval_user_turns = 6\n", encoding="utf-8")
        os.environ[ENV_ARCHIVE_INTERVAL] = "3"
        self.assertEqual(load_archive_settings(self.config).interval_user_turns, 3)

    def test_peer_writer_requires_explicit_true(self) -> None:
        self.config.write_text(
            "[mcp]\nallow_peer_writer = true\n", encoding="utf-8"
        )
        self.assertTrue(load_archive_settings(self.config).allow_peer_writer)

        self.config.write_text(
            "[mcp]\nallow_peer_writer = false\n", encoding="utf-8"
        )
        self.assertFalse(load_archive_settings(self.config).allow_peer_writer)
