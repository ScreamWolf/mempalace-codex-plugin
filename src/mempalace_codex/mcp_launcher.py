"""Configuration-aware launcher for the upstream MemPalace MCP server."""

from __future__ import annotations

import os
import sys

from .config import load_archive_settings


UPSTREAM_MCP_COMMAND = "mempalace-mcp"
UPSTREAM_PEER_WRITER_ENV = "MEMPALACE_MCP_ALLOW_PEER_WRITER"


def main() -> None:
    """Apply private plugin settings, then replace this process with upstream MCP."""
    if load_archive_settings().allow_peer_writer:
        os.environ[UPSTREAM_PEER_WRITER_ENV] = "1"
    os.execvp(UPSTREAM_MCP_COMMAND, [UPSTREAM_MCP_COMMAND, *sys.argv[1:]])
