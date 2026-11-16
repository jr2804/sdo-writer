"""Installing, updating and removing the writer.

An install writes three things and nothing else: the agent file, one
``mcp.servers`` entry in the OpenCode configuration, and the manifest. Skill
content is served by ``sdo-skills-mcp`` and never lands on disk, so there are
no skill directories to copy, hash, conflict or drift.

A manifest from an earlier version, which did install skills, is honoured on
the way out: the skill directories it lists are removed once.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .agent import render_agent
from .manifest import Manifest, load_manifest, save_manifest
from .mcp import (
    MCP_SERVER_NAME,
    entry_json,
    has_server,
    read_config,
    remove_server,
    server_entry,
    write_server,
)
from .paths import agents_dir, config_file, manifest_path, skills_dir
from .profile import Profile


@dataclass
class InstallReport:
    """What an install or update did.

    Attributes:
        profile: Identifier of the profile that was installed.
        config_dir: OpenCode configuration directory that was written to.
        agent_path: Path of the installed agent file.
        agent_written: Whether the agent file changed.
        mcp_written: Whether the server entry was written to the configuration.
        mcp_pending: The entry the user has to add by hand, when the
            configuration is JSONC or otherwise not writable.
        removed_skills: Skill directories of an earlier, vendoring install
            that were removed.
        config_path: Path of the OpenCode configuration file.
    """

    profile: str
    config_dir: Path
    agent_path: Path | None = None
    agent_written: bool = False
    mcp_written: bool = False
    mcp_pending: dict | None = None
    removed_skills: list[str] = field(default_factory=list)

    @property
    def config_path(self) -> Path:
        """Return the OpenCode configuration file of the target."""
        return config_file(self.config_dir)

    @property
    def pending_json(self) -> str:
        """Return the entry that could not be written, as JSON."""
        return entry_json(self.mcp_pending or {})


def install(
    profile: Profile,
    config_dir: Path,
    *,
    roots: list[Path] | None = None,
    write_agent: bool = True,
) -> InstallReport:
    """Install a profile into an OpenCode configuration directory.

    Args:
        profile: The profile to install.
        config_dir: The OpenCode configuration directory to write to.
        roots: Skill roots passed to the server; the server falls back to
            ``SDO_SKILLS_ROOTS`` when this is empty.
        write_agent: Whether to write the agent file.

    Returns:
        A report of what was done.

    Raises:
        McpError: If the existing configuration has a malformed ``mcp`` section.
    """
    report = InstallReport(profile=profile.id, config_dir=config_dir)
    previous = load_manifest(manifest_path(config_dir))
    report.removed_skills = _remove_legacy_skills(config_dir, previous)

    if write_agent:
        report.agent_path = _write_agent(profile, config_dir)
        report.agent_written = True

    entry = server_entry(profile.id, list(roots or []))
    pending = write_server(config_file(config_dir), MCP_SERVER_NAME, entry)
    report.mcp_written = pending is None
    report.mcp_pending = pending

    manifest = Manifest(
        profile=profile.id,
        installed_at=datetime.now(UTC).isoformat(timespec="seconds"),
        agent=f"{profile.agent_name}.md" if write_agent else None,
        mcp_server=MCP_SERVER_NAME,
        mcp_config=config_file(config_dir).name,
    )
    save_manifest(manifest_path(config_dir), manifest)
    return report


def _write_agent(profile: Profile, config_dir: Path) -> Path:
    """Render the agent file, returning its path."""
    agent_path = agents_dir(config_dir) / f"{profile.agent_name}.md"
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    agent_path.write_text(render_agent(profile), encoding="utf-8")
    return agent_path


def status(config_dir: Path) -> tuple[Manifest | None, list[str]]:
    """Return the manifest and everything that no longer matches it.

    Returns:
        The manifest, or ``None`` when nothing is installed, and a list of
        problems: a missing agent file, a missing server entry, a
        configuration that cannot be read.
    """
    manifest = load_manifest(manifest_path(config_dir))
    if manifest is None:
        return None, []

    problems: list[str] = []
    if manifest.agent and not (agents_dir(config_dir) / manifest.agent).is_file():
        problems.append(f"agent file missing: {manifest.agent}")

    present = has_server(read_config(config_file(config_dir)), manifest.mcp_server or MCP_SERVER_NAME)
    if present is None:
        problems.append("configuration is not plain JSON; check the server entry by hand")
    elif not present:
        problems.append(f"server entry missing: {manifest.mcp_server or MCP_SERVER_NAME}")
    return manifest, problems


def uninstall(config_dir: Path) -> tuple[Path | None, bool, list[str]]:
    """Remove everything a previous install put on disk.

    Returns:
        The path of the removed agent file, whether the server entry was
        removed, and the skill directories of an earlier install that were
        removed.
    """
    manifest = load_manifest(manifest_path(config_dir))
    if manifest is None:
        return None, False, []

    agent_path: Path | None = None
    if manifest.agent:
        candidate = agents_dir(config_dir) / manifest.agent
        if candidate.is_file():
            candidate.unlink()
            agent_path = candidate

    removed_server = remove_server(config_file(config_dir), manifest.mcp_server or MCP_SERVER_NAME)
    removed_skills = _remove_legacy_skills(config_dir, manifest)

    manifest_path(config_dir).unlink(missing_ok=True)
    return agent_path, removed_server, removed_skills


def _remove_legacy_skills(config_dir: Path, manifest: Manifest | None) -> list[str]:
    """Remove the skill directories a vendoring install left behind."""
    if manifest is None or not manifest.skills:
        return []
    root = skills_dir(config_dir)
    removed: list[str] = []
    for skill_id in manifest.skills:
        target = root / skill_id
        if target.is_dir():
            shutil.rmtree(target)
            removed.append(skill_id)
    return removed
