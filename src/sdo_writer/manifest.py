"""The installer manifest.

The manifest records what a previous install put on disk, so that a status
check can look for exactly those files and an uninstall can remove exactly
those files, without touching anything the user added themselves.

It is written as JSON into the OpenCode configuration directory. The ``skills``
mapping is kept for compatibility: an install from before the skills moved to
the ``sdo-skills-mcp`` server lists the skill directories it copied, and those
are removed on the next install or uninstall.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

MANIFEST_VERSION = 2


@dataclass
class Manifest:
    """State of an installation.

    Attributes:
        version: Schema version of the manifest.
        profile: Identifier of the profile that was installed.
        installed_at: Timestamp of the last install, in ISO 8601 format.
        agent: File name of the installed agent, or ``None``.
        mcp_server: Name of the MCP server entry in the OpenCode configuration.
        mcp_config: File name of the OpenCode configuration that holds it.
        skills: Skill directories left by an install that copied them; empty
            for an install that serves the skills from the server.
    """

    version: int = MANIFEST_VERSION
    profile: str = ""
    installed_at: str = ""
    agent: str | None = None
    mcp_server: str = ""
    mcp_config: str = ""
    skills: dict[str, str] = field(default_factory=dict)

    @property
    def installed_skills(self) -> list[str]:
        """Return the identifiers of the copied skills, sorted."""
        return sorted(self.skills)


def load_manifest(path: Path) -> Manifest | None:
    """Load a manifest, returning ``None`` when it does not exist or is unreadable."""
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    skills = data.get("skills")
    agent = data.get("agent")
    return Manifest(
        version=int(data.get("version", MANIFEST_VERSION)),
        profile=str(data.get("profile", "")),
        installed_at=str(data.get("installed_at", "")),
        agent=agent if isinstance(agent, str) and agent else None,
        mcp_server=_text(data.get("mcp_server")),
        mcp_config=_text(data.get("mcp_config")),
        skills={str(k): str(v) for k, v in skills.items()} if isinstance(skills, dict) else {},
    )


def save_manifest(path: Path, manifest: Manifest) -> None:
    """Write a manifest to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": manifest.version,
        "profile": manifest.profile,
        "installed_at": manifest.installed_at or datetime.now(UTC).isoformat(timespec="seconds"),
        "agent": manifest.agent,
        "mcp_server": manifest.mcp_server,
        "mcp_config": manifest.mcp_config,
        "skills": dict(sorted(manifest.skills.items())),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _text(value: object) -> str:
    """Return a manifest field as text, empty when it is not a string."""
    return value if isinstance(value, str) else ""
