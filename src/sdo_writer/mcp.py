"""The MCP server entry this package installs.

The skills are served by ``sdo-skills-mcp``; the installer only adds one
``mcp.servers`` entry to the OpenCode configuration. An ``opencode.json`` is
rewritten; an ``opencode.jsonc`` is never touched, because rewriting a file
that carries comments would lose them. In that case the caller prints the
entry and the user pastes it in.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

SERVER_PACKAGE = "git+https://github.com/jr2804/sdo-skills-mcp"
SCHEMA_URL = "https://opencode.ai/config.json"

#: Interpreter the server is started with.
#:
#: The pin is deliberate. ``fastmcp`` pulls ``pywin32`` on Windows, which has
#: no free-threading wheel, so the server must run on the regular CPython
#: build. ``--python 3.14`` selects the default (GIL-enabled) 3.14: when a
#: machine only has an old-style free-threaded 3.14 registered, ``uvx``
#: downloads the regular build instead of landing on the incompatible one.
SERVER_PYTHON = "3.14"

#: Name of the ``mcp.servers`` entry this package writes.
MCP_SERVER_NAME = "sdo-skills"


class McpError(Exception):
    """Raised when the MCP configuration cannot be written."""


def server_entry(profile_id: str, roots: list[Path]) -> dict[str, Any]:
    """Return the ``mcp.servers`` entry for a profile."""
    return {"type": "local", "command": server_command(profile_id, roots)}


def server_command(profile_id: str, roots: list[Path]) -> list[str]:
    """Return the command that starts the skills server for a profile."""
    command = ["uvx", "--python", SERVER_PYTHON, "--from", SERVER_PACKAGE, "sdo-skills-mcp", "serve", "--profile", profile_id]
    for root in roots:
        command.extend(["--root", str(root)])
    return command


def entry_json(entry: dict[str, Any]) -> str:
    """Return the entry as an indented JSON snippet."""
    return json.dumps(entry, indent=2)


def has_server(config: dict[str, Any] | None, name: str) -> bool | None:
    """Return whether the entry is present, or ``None`` when unknown."""
    if config is None:
        return None
    servers = config.get("mcp", {}).get("servers") if isinstance(config.get("mcp"), dict) else None
    return isinstance(servers, dict) and name in servers


def write_server(path: Path, name: str, entry: dict[str, Any]) -> dict[str, Any] | None:
    """Add the server entry to ``path``.

    Returns:
        ``None`` when the entry was written, otherwise the entry the caller
        has to add by hand.
    """
    existing = read_config(path)
    if existing is None:
        return entry
    config = with_server(existing, name, entry)
    if "$schema" not in config:
        config = {"$schema": SCHEMA_URL, **config}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return None


def with_server(config: dict[str, Any], name: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``config`` with the server entry set.

    Raises:
        McpError: If the ``mcp`` or ``mcp.servers`` section has the wrong type.
    """
    merged = copy.deepcopy(config)
    mcp = merged.setdefault("mcp", {})
    if not isinstance(mcp, dict):
        msg = "'mcp' is not an object"
        raise McpError(msg)
    servers = mcp.setdefault("servers", {})
    if not isinstance(servers, dict):
        msg = "'mcp.servers' is not an object"
        raise McpError(msg)
    servers[name] = copy.deepcopy(entry)
    return merged


def remove_server(path: Path, name: str) -> bool:
    """Remove the server entry from ``path``, returning whether it was written."""
    existing = read_config(path)
    if existing is None:
        return False
    path.write_text(json.dumps(without_server(existing, name), indent=2) + "\n", encoding="utf-8")
    return True


def without_server(config: dict[str, Any], name: str) -> dict[str, Any]:
    """Return a copy of ``config`` with the server entry removed."""
    stripped = copy.deepcopy(config)
    servers = stripped.get("mcp", {}).get("servers") if isinstance(stripped.get("mcp"), dict) else None
    if isinstance(servers, dict):
        servers.pop(name, None)
    return stripped


def read_config(path: Path) -> dict[str, Any] | None:
    """Return the parsed configuration, or ``None`` when it is not plain JSON.

    A JSONC file, a broken file or a file that is not an object all return
    ``None``: the caller then reports the entry instead of rewriting it.
    """
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None
