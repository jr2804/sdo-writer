"""Tests for the agent renderer."""

from __future__ import annotations

import dataclasses

import yaml

from sdo_writer.agent import render_agent
from sdo_writer.mcp import MCP_SERVER_NAME
from sdo_writer.profile import load_profile


def test_render_agent_has_valid_v2_frontmatter() -> None:
    profile = load_profile("etsi")
    data = _frontmatter(render_agent(profile))

    assert data["description"] == profile.description
    assert data["mode"] == "primary"
    assert data["color"] == profile.color


def test_the_file_starts_with_the_frontmatter() -> None:
    rendered = render_agent(load_profile("etsi"))

    assert rendered.startswith("---\n")
    assert rendered.count("\n---\n") == 1
    assert '"""' not in rendered
    assert "FRONTMATTER" not in rendered


def test_no_deprecated_v1_fields() -> None:
    data = _frontmatter(render_agent(load_profile("etsi")))

    for deprecated in ("temperature", "top_p", "prompt", "permission", "tools", "disable", "maxSteps"):
        assert deprecated not in data


def test_local_skills_are_denied() -> None:
    rules = _rules(render_agent(load_profile("etsi")))

    assert {"action": "skill", "resource": "*", "effect": "deny"} in rules


def test_shell_asks_by_default_and_allows_the_profile_tools() -> None:
    rules = _rules(render_agent(load_profile("etsi")))

    assert {"action": "shell", "resource": "*", "effect": "ask"} in rules
    assert {"action": "shell", "resource": "mise *", "effect": "allow"} in rules
    assert {"action": "shell", "resource": "git diff*", "effect": "allow"} in rules


def test_the_skills_server_tools_are_allowed() -> None:
    rules = _rules(render_agent(load_profile("etsi")))

    assert {"action": f"{MCP_SERVER_NAME}_sdo_list_skills", "resource": "*", "effect": "allow"} in rules
    assert {"action": f"{MCP_SERVER_NAME}_sdo_read_skill", "resource": "*", "effect": "allow"} in rules
    assert {
        "action": "opencode_read_mcp_resource",
        "resource": f"{MCP_SERVER_NAME}:*",
        "effect": "allow",
    } in rules


def test_body_contains_the_shared_prompt_and_the_profile_notes() -> None:
    profile = load_profile("itut")
    rendered = render_agent(profile)

    assert "You are a standards writer." in rendered
    assert "Skill routing" in rendered
    assert "sdo_list_skills" in rendered
    assert profile.notes.strip().splitlines()[0] in rendered


def test_agent_without_notes_has_no_extra_section() -> None:
    profile = dataclasses.replace(load_profile("etsi"), notes="")
    rendered = render_agent(profile)

    assert "ETSI specifics" not in rendered
    assert rendered.endswith("is a good revision.\n")


def test_description_is_quoted_when_it_needs_it() -> None:
    profile = dataclasses.replace(
        load_profile("etsi"),
        description='ETSI: the "institute"',
    )
    data = _frontmatter(render_agent(profile))

    assert data["description"] == 'ETSI: the "institute"'


def test_plain_description_is_not_quoted() -> None:
    profile = dataclasses.replace(load_profile("etsi"), description="A plain line")
    rendered = render_agent(profile)

    assert "description: A plain line\n" in rendered


def _rules(rendered: str) -> list[dict]:
    return _frontmatter(rendered)["permissions"]


def _frontmatter(rendered: str) -> dict:
    _, _, body = rendered.partition("---")
    frontmatter, _, _ = body.partition("---")
    return yaml.safe_load(frontmatter)
