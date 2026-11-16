"""Rendering the OpenCode agent file.

The agent is a Markdown file with a YAML frontmatter block, placed in
``<config>/agents/<name>.md``. OpenCode turns the file name into the agent
name and reads the frontmatter for the description, mode, colour and
permission rules.

The agent carries no skill content: the skills are read from the
``sdo-skills-mcp`` server at run time. The permissions therefore deny local
skills outright, so that a stray copy on disk can never shadow the server.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from .mcp import MCP_SERVER_NAME
from .profile import Profile

TEMPLATE_PACKAGE = "sdo_writer.templates"
FRONTMATTER_TEMPLATE = "sdo-writer.md"
BODY_TEMPLATE = "sdo-writer-body.md"

#: Tools of the skills server that the agent may call without asking.
MCP_TOOLS = ("sdo_list_skills", "sdo_read_skill")


def render_agent(profile: Profile) -> str:
    """Render the agent file for a profile.

    Args:
        profile: The profile to render.

    Returns:
        The complete agent file, frontmatter and prompt.
    """
    frontmatter = _read_template(FRONTMATTER_TEMPLATE)
    replacements = {
        "{{description}}": _yaml_string(profile.description),
        "{{mode}}": profile.mode,
        "{{color}}": _yaml_string(profile.color),
        "{{shell_permissions}}": _rules("shell", profile.tools_allow),
        "{{mcp_permissions}}": _mcp_rules(),
    }
    for marker, value in replacements.items():
        frontmatter = frontmatter.replace(marker, value)

    body = _read_template(BODY_TEMPLATE).rstrip("\n")
    notes = profile.notes.strip()
    body = f"{body}\n\n{notes}\n" if notes else f"{body}\n"

    return f"{frontmatter}\n{body}"


def _rules(action: str, resources: tuple[str, ...]) -> str:
    """Render ``allow`` rules for one action."""
    return "".join(f'  - action: {action}\n    resource: "{resource}"\n    effect: allow\n' for resource in resources)


def _mcp_rules() -> str:
    """Render the rules that let the agent read the skills server.

    An MCP tool is matched by its normalized ``<server>_<tool>`` name as the
    action, with ``*`` as the resource. Resources are matched by
    ``opencode_read_mcp_resource`` with ``<server>:<uri>``.
    """
    tools = "".join(f'  - action: {MCP_SERVER_NAME}_{tool}\n    resource: "*"\n    effect: allow\n' for tool in MCP_TOOLS)
    resources = f'  - action: opencode_read_mcp_resource\n    resource: "{MCP_SERVER_NAME}:*"\n    effect: allow\n'
    return tools + resources


def _read_template(name: str) -> str:
    """Read a template from the package."""
    resource = files(TEMPLATE_PACKAGE).joinpath(name)
    return Path(str(resource)).read_text(encoding="utf-8")


def _yaml_string(value: str) -> str:
    """Quote a string for YAML when it needs it."""
    if value and not any(char in value for char in ":#{}[]&*!|>%@`\"'\n"):
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{escaped}"'
