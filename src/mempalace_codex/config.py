"""Private runtime configuration for the Codex archive adapter."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tomllib


DEFAULT_CONFIG_PATH = Path.home() / ".config" / "mempalace-codex" / "config.toml"
DEFAULT_ARCHIVE_INTERVAL = 15
ENV_ARCHIVE_INTERVAL = "MEMPALACE_CODEX_ARCHIVE_INTERVAL"


@dataclass(frozen=True)
class ArchiveSettings:
    """Private settings used by the Codex integration."""

    interval_user_turns: int = DEFAULT_ARCHIVE_INTERVAL
    allow_peer_writer: bool = False


def _positive_integer(value: object) -> int | None:
    return value if isinstance(value, int) and value > 0 else None


def _allow_peer_writer(raw: dict[str, object]) -> bool:
    mcp = raw.get("mcp", {})
    return isinstance(mcp, dict) and mcp.get("allow_peer_writer") is True


def load_archive_settings(path: Path = DEFAULT_CONFIG_PATH) -> ArchiveSettings:
    """Load archive cadence from an environment override or private TOML config.

    Precedence: ``MEMPALACE_CODEX_ARCHIVE_INTERVAL`` > config file > default.
    Invalid values are ignored so a malformed local preference never breaks a
    Codex Hook invocation.
    """

    try:
        env_value = _positive_integer(int(os.environ.get(ENV_ARCHIVE_INTERVAL, "")))
    except ValueError:
        env_value = None
    if env_value is not None:
        try:
            raw = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            raw = {}
        return ArchiveSettings(
            interval_user_turns=env_value,
            allow_peer_writer=_allow_peer_writer(raw),
        )

    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
        config_value = _positive_integer(raw.get("archive", {}).get("interval_user_turns"))
        if config_value is not None:
            return ArchiveSettings(
                interval_user_turns=config_value,
                allow_peer_writer=_allow_peer_writer(raw),
            )
        return ArchiveSettings(allow_peer_writer=_allow_peer_writer(raw))
    except (OSError, tomllib.TOMLDecodeError, AttributeError):
        pass
    return ArchiveSettings()
