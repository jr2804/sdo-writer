"""CLI arguments, options, and flags for SDO Writer."""

from __future__ import annotations

from typing import Annotated

import typer

# Application name for environment variables
APP_NAME_UPPERCASE = "SDO_WRITER"

# Global options

OutputFile = Annotated[
    str | None,
    typer.Option(
        "--output-file",
        "-o",
        help="Path to output file",
        envvar=f"{APP_NAME_UPPERCASE}_OUTPUT_FILE",
    ),
]

# Command-specific arguments

ProfileArg = Annotated[
    str | None,
    typer.Option(
        "--profile",
        "-p",
        help="Profile to install: etsi, 3gpp or itut",
    ),
]

ConfigPath = Annotated[
    str | None,
    typer.Option(
        "--config",
        "-c",
        help="Path to an OpenCode configuration directory (defaults to the global one)",
    ),
]

ProjectPath = Annotated[
    str | None,
    typer.Option(
        "--project",
        help="Install into the .opencode directory of this project instead of the global one",
    ),
]

SkillRoots = Annotated[
    list[str] | None,
    typer.Option(
        "--skills-root",
        "-r",
        help=("Directory that holds the skill folders, passed to the skills server. Repeat for more than one; the server falls back to SDO_SKILLS_ROOTS."),
    ),
]

DryRunFlag = Annotated[
    bool,
    typer.Option(
        "--dry-run",
        help="Show what would be written without touching anything",
    ),
]

NoAgentFlag = Annotated[
    bool,
    typer.Option(
        "--no-agent",
        help="Write only the MCP server entry, not the agent file",
    ),
]
