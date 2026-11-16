"""Filesystem locations used by the installer.

OpenCode keeps two kinds of configuration:

* the **global** configuration in ``~/.config/opencode`` (or
  ``$XDG_CONFIG_HOME/opencode``), which every project sees, and
* the **project** configuration in ``<project>/.opencode``.

Both hold an ``agents/`` directory and an ``opencode.json``; the installer
writes the agent there and the MCP server entry into that file. The
``skills/`` directory is only read, to clean up after an install that still
copied skill files onto disk.
"""

from __future__ import annotations

import os
from pathlib import Path

GLOBAL_CONFIG_ENV = "XDG_CONFIG_HOME"

#: Name of the OpenCode configuration file, in either spelling.
CONFIG_FILE = "opencode.json"
CONFIG_FILE_JSONC = "opencode.jsonc"


def global_config_dir() -> Path:
    """Return the OpenCode global configuration directory.

    ``XDG_CONFIG_HOME`` wins when it is set, otherwise ``~/.config`` is used.
    """
    xdg = os.environ.get(GLOBAL_CONFIG_ENV)
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "opencode"


def project_config_dir(project: Path | None = None) -> Path:
    """Return the OpenCode configuration directory of a project."""
    root = project if project is not None else Path.cwd()
    return root / ".opencode"


def config_file(config_dir: Path) -> Path:
    """Return the configuration file the installer writes.

    An existing ``opencode.jsonc`` is returned as is: the installer refuses to
    rewrite it, and printing the entry next to the file it belongs in is more
    useful than printing it next to a file that does not exist.
    """
    jsonc = config_dir / CONFIG_FILE_JSONC
    return jsonc if jsonc.is_file() else config_dir / CONFIG_FILE


def skills_dir(config_dir: Path) -> Path:
    """Return the skills directory inside an OpenCode configuration directory."""
    return config_dir / "skills"


def agents_dir(config_dir: Path) -> Path:
    """Return the agents directory inside an OpenCode configuration directory."""
    return config_dir / "agents"


def manifest_path(config_dir: Path) -> Path:
    """Return the path of the installer manifest inside a configuration directory."""
    return config_dir / "sdo-writer.json"
