"""Writer profiles.

A profile is the small amount of configuration that differs between the ETSI,
3GPP and ITU-T writers: the agent's description, its colour, the commands it
may run without asking, and the notes appended to its prompt. Which skills the
profile can use is decided by the ``sdo-skills-mcp`` server, whose own catalog
maps a profile identifier to a set of skills.

Profiles are TOML files in the package, so they are readable, commentable and
need no parser beyond the standard library.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from importlib.resources import files
from typing import Any

PROFILE_PACKAGE = "sdo_writer.profiles"

AGENT_NAME = "sdo-writer"


@dataclass(frozen=True)
class Profile:
    """One writer profile.

    Attributes:
        id: Short identifier used on the command line (``etsi``).
        title: Human readable name.
        description: One line describing what the profile is for.
        agent_name: File name of the installed agent, without extension.
        mode: OpenCode agent mode (``primary`` or ``subagent``).
        color: Agent colour in the OpenCode user interface.
        tools_allow: Shell commands the agent may run without asking.
        notes: Markdown appended to the agent prompt, specific to the SDO.
    """

    id: str
    title: str
    description: str
    agent_name: str = AGENT_NAME
    mode: str = "primary"
    color: str = "#2f6f9f"
    tools_allow: tuple[str, ...] = ()
    notes: str = ""


class ProfileError(Exception):
    """Raised when a profile cannot be loaded or is invalid."""


def load_profile(profile_id: str) -> Profile:
    """Load a profile by identifier.

    Args:
        profile_id: Identifier of the profile, for example ``etsi``.

    Returns:
        The parsed profile.

    Raises:
        ProfileError: If the profile does not exist or is malformed.
    """
    resource = files(PROFILE_PACKAGE).joinpath(f"{profile_id}.toml")
    if not resource.is_file():
        known = ", ".join(available_profiles())
        msg = f"Unknown profile '{profile_id}'. Available profiles: {known}"
        raise ProfileError(msg)

    try:
        data = tomllib.loads(resource.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as err:
        msg = f"Profile '{profile_id}' is not valid TOML: {err}"
        raise ProfileError(msg) from err

    return _build(profile_id, data)


def available_profiles() -> list[str]:
    """Return the identifiers of all bundled profiles, sorted."""
    directory = files(PROFILE_PACKAGE)
    names = [entry.name[:-5] for entry in directory.iterdir() if entry.name.endswith(".toml")]
    return sorted(names)


def _build(profile_id: str, data: dict[str, Any]) -> Profile:
    """Turn parsed TOML into a :class:`Profile`."""
    for key in ("title", "description"):
        if key not in data:
            msg = f"Profile '{profile_id}' is missing '{key}'"
            raise ProfileError(msg)

    agent = data.get("agent", {})
    tools = data.get("tools", {})
    notes = data.get("notes", {})

    if not isinstance(agent, dict):
        msg = f"Profile '{profile_id}' has a malformed [agent] section"
        raise ProfileError(msg)

    return Profile(
        id=profile_id,
        title=str(data["title"]),
        description=str(data["description"]),
        agent_name=str(agent.get("name", AGENT_NAME)),
        mode=str(agent.get("mode", "primary")),
        color=str(agent.get("color", "#2f6f9f")),
        tools_allow=tuple(str(tool) for tool in tools.get("allow", [])),
        notes=str(notes.get("body", "")),
    )
