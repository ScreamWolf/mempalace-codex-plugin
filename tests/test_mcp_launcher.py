import os
import unittest
from unittest.mock import patch

from mempalace_codex import mcp_launcher


class McpLauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous_env = os.environ.pop(mcp_launcher.UPSTREAM_PEER_WRITER_ENV, None)

    def tearDown(self) -> None:
        if self.previous_env is not None:
            os.environ[mcp_launcher.UPSTREAM_PEER_WRITER_ENV] = self.previous_env
        else:
            os.environ.pop(mcp_launcher.UPSTREAM_PEER_WRITER_ENV, None)

    @patch("mempalace_codex.mcp_launcher.os.execvp")
    @patch("mempalace_codex.mcp_launcher.load_archive_settings")
    def test_enables_upstream_override_when_configured(self, load_settings, execvp) -> None:
        load_settings.return_value.allow_peer_writer = True

        with patch.object(mcp_launcher.sys, "argv", ["mempalace-codex-mcp"]):
            mcp_launcher.main()

        self.assertEqual(os.environ[mcp_launcher.UPSTREAM_PEER_WRITER_ENV], "1")
        execvp.assert_called_once_with("mempalace-mcp", ["mempalace-mcp"])

    @patch("mempalace_codex.mcp_launcher.os.execvp")
    @patch("mempalace_codex.mcp_launcher.load_archive_settings")
    def test_preserves_official_default_when_unconfigured(self, load_settings, execvp) -> None:
        load_settings.return_value.allow_peer_writer = False

        with patch.object(mcp_launcher.sys, "argv", ["mempalace-codex-mcp"]):
            mcp_launcher.main()

        self.assertNotIn(mcp_launcher.UPSTREAM_PEER_WRITER_ENV, os.environ)
        execvp.assert_called_once_with("mempalace-mcp", ["mempalace-mcp"])
