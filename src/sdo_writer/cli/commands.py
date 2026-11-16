"""CLI command implementations for SDO Writer."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from sdo_writer import installer
from sdo_writer.cli import args
from sdo_writer.mcp import MCP_SERVER_NAME, McpError, entry_json, server_entry
from sdo_writer.paths import CONFIG_FILE, global_config_dir, project_config_dir
from sdo_writer.profile import ProfileError, available_profiles, load_profile


def update(
    profile: args.ProfileArg = None,
    config: args.ConfigPath = None,
    project: args.ProjectPath = None,
    roots: args.SkillRoots = None,
    no_agent: args.NoAgentFlag = False,
) -> None:
    """Re-install a profile: rewrite the agent and the server entry."""
    init(profile=profile, config=config, project=project, roots=roots, no_agent=no_agent)


def init(
    profile: args.ProfileArg = None,
    config: args.ConfigPath = None,
    project: args.ProjectPath = None,
    roots: args.SkillRoots = None,
    dry_run: args.DryRunFlag = False,
    no_agent: args.NoAgentFlag = False,
) -> None:
    """Install a writer profile: the `sdo-writer` agent and the skills server."""
    known = available_profiles()
    if profile is None:
        typer.echo("No profile given. Available profiles:")
        profiles()
        raise typer.Exit(code=1)
    if profile not in known:
        typer.echo(f"Unknown profile '{profile}'. Available profiles: {', '.join(known)}")
        raise typer.Exit(code=1)

    try:
        loaded = load_profile(profile)
    except ProfileError as err:
        typer.echo(f"Error: {err}")
        raise typer.Exit(code=1) from err

    config_dir = _config_dir(config, project)
    skill_roots = [Path(root).expanduser().resolve() for root in roots or []]

    if dry_run:
        entry = server_entry(loaded.id, skill_roots)
        typer.echo(f"Would write into {config_dir}:")
        typer.echo(f"  agents/{loaded.agent_name}.md")
        typer.echo(f"  {CONFIG_FILE} -> mcp.servers.{MCP_SERVER_NAME}")
        typer.echo("")
        typer.echo(entry_json(entry))
        return

    try:
        report = installer.install(loaded, config_dir, roots=skill_roots, write_agent=not no_agent)
    except McpError as err:
        typer.echo(f"Error: {config_dir / CONFIG_FILE}: {err}")
        raise typer.Exit(code=1) from err

    _echo_report(report)


def _echo_report(report: installer.InstallReport) -> None:
    """Print an install report."""
    typer.echo(f"Profile:  {report.profile}")
    typer.echo(f"Config:   {report.config_dir}")
    if report.agent_path:
        typer.echo(f"Agent:    {report.agent_path}")
    if report.mcp_written:
        typer.echo(f"Server:   mcp.servers.{MCP_SERVER_NAME} in {report.config_path}")
    if report.mcp_pending:
        typer.echo("")
        typer.echo(f"{report.config_path} could not be rewritten, so add this by hand:")
        typer.echo("")
        typer.echo(report.pending_json)
    for skill_id in report.removed_skills:
        typer.echo(f"Removed:  skills/{skill_id} (copied by an earlier install)")


def profiles() -> None:
    """List the available writer profiles."""
    for profile_id in available_profiles():
        profile = load_profile(profile_id)
        typer.echo(f"{profile.id:<8} {profile.title} - {profile.description}")


def status(
    config: args.ConfigPath = None,
    project: args.ProjectPath = None,
) -> None:
    """Show what is currently installed."""
    config_dir = _config_dir(config, project)
    manifest, problems = installer.status(config_dir)
    if manifest is None:
        typer.echo(f"Nothing installed in {config_dir}")
        raise typer.Exit(code=1)

    typer.echo(f"Profile:  {manifest.profile}")
    typer.echo(f"Updated:  {manifest.installed_at}")
    typer.echo(f"Agent:    {manifest.agent or 'not installed'}")
    typer.echo(f"Server:   {manifest.mcp_server or MCP_SERVER_NAME} ({manifest.mcp_config or CONFIG_FILE})")
    for problem in problems:
        typer.echo(f"! {problem}")
    if problems:
        typer.echo("")
        typer.echo("Run 'update' to restore them.")


def entry(
    profile: args.ProfileArg = None,
    roots: args.SkillRoots = None,
) -> None:
    """Print the MCP server entry of a profile, without writing anything."""
    known = available_profiles()
    if profile is None:
        typer.echo(f"Available profiles: {', '.join(known)}")
        raise typer.Exit(code=1)
    if profile not in known:
        typer.echo(f"Unknown profile '{profile}'. Available profiles: {', '.join(known)}")
        raise typer.Exit(code=1)

    skill_roots = [Path(root).expanduser().resolve() for root in roots or []]
    typer.echo(json.dumps(server_entry(profile, skill_roots), indent=2))


def uninstall(
    config: args.ConfigPath = None,
    project: args.ProjectPath = None,
) -> None:
    """Remove the agent, the server entry and the manifest."""
    config_dir = _config_dir(config, project)
    agent_path, removed_server, removed_skills = installer.uninstall(config_dir)
    if agent_path is None and not removed_server and not removed_skills:
        typer.echo(f"Nothing to remove in {config_dir}")
        return
    if agent_path:
        typer.echo(f"Removed agent: {agent_path}")
    if removed_server:
        typer.echo(f"Removed server entry: mcp.servers.{MCP_SERVER_NAME}")
    for skill_id in removed_skills:
        typer.echo(f"Removed skill: {skill_id}")


def _config_dir(config: str | None, project: str | None) -> Path:
    """Return the OpenCode configuration directory to work in."""
    if project:
        return project_config_dir(Path(project).expanduser().resolve())
    if config:
        return Path(config).expanduser().resolve()
    return global_config_dir()
