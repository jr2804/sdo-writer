"""Tests for the command line interface."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from sdo_writer.cli.app import app
from sdo_writer.mcp import MCP_SERVER_NAME
from sdo_writer.paths import CONFIG_FILE

runner = CliRunner()


def test_profiles_lists_all_bundled_profiles() -> None:
    result = runner.invoke(app, ["profiles"])

    assert result.exit_code == 0
    for profile_id in ("etsi", "3gpp", "itut"):
        assert profile_id in result.output


def test_init_without_profile_lists_them() -> None:
    result = runner.invoke(app, ["init"])

    assert result.exit_code == 1
    assert "Available profiles" in result.output


def test_init_with_unknown_profile() -> None:
    result = runner.invoke(app, ["init", "--profile", "nope"])

    assert result.exit_code == 1
    assert "Unknown profile" in result.output


def test_init_installs_the_agent_and_the_server(config) -> None:
    result = runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config)])

    assert result.exit_code == 0
    assert "Agent:" in result.output
    assert "Server:" in result.output
    assert (config / "agents" / "sdo-writer.md").is_file()
    server = json.loads((config / CONFIG_FILE).read_text(encoding="utf-8"))["mcp"]["servers"][MCP_SERVER_NAME]
    assert server["command"][8] == "etsi"
    assert not (config / "skills").exists()


def test_init_dry_run_writes_nothing(config) -> None:
    result = runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config), "--dry-run"])

    assert result.exit_code == 0
    assert "Would write into" in result.output
    assert "sdo-skills-mcp" in result.output
    assert not config.exists()


def test_init_passes_the_skill_roots(config, tmp_path) -> None:
    first, second = tmp_path / "a", tmp_path / "b"
    result = runner.invoke(
        app,
        ["init", "--profile", "itut", "--config", str(config), "--skills-root", str(first), "-r", str(second)],
    )

    assert result.exit_code == 0
    command = json.loads((config / CONFIG_FILE).read_text(encoding="utf-8"))["mcp"]["servers"][MCP_SERVER_NAME]["command"]
    assert command[-4].lower() == "--root"
    assert command[-3].casefold() == str(first).casefold()
    assert command[-1].casefold() == str(second).casefold()


def test_init_without_agent(config) -> None:
    result = runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config), "--no-agent"])

    assert result.exit_code == 0
    assert "Agent:" not in result.output
    assert not (config / "agents").exists()


def test_init_into_a_jsonc_file_prints_the_entry(config) -> None:
    config.mkdir(parents=True)
    jsonc = config / "opencode.jsonc"
    original = "{\n  // mine\n}\n"
    jsonc.write_text(original, encoding="utf-8")

    result = runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config)])

    assert result.exit_code == 0
    assert "add this by hand" in result.output
    assert '"type": "local"' in result.output
    assert jsonc.read_text(encoding="utf-8") == original


def test_init_reports_a_malformed_mcp_section(config) -> None:
    config.mkdir(parents=True)
    (config / CONFIG_FILE).write_text(json.dumps({"mcp": []}), encoding="utf-8")

    result = runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config)])

    assert result.exit_code == 1
    assert "'mcp' is not an object" in result.output


def test_init_reports_removed_legacy_skills(config) -> None:
    legacy = config / "skills" / "sdo-writing"
    legacy.mkdir(parents=True)
    (legacy / "SKILL.md").write_text("---\nname: sdo-writing\n---\nold\n", encoding="utf-8")
    (config / "sdo-writer.json").write_text(json.dumps({"version": 1, "skills": {"sdo-writing": "h"}}), encoding="utf-8")

    result = runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config)])

    assert result.exit_code == 0
    assert "Removed:  skills/sdo-writing" in result.output
    assert not legacy.exists()


def test_status_without_install(config) -> None:
    result = runner.invoke(app, ["status", "--config", str(config)])

    assert result.exit_code == 1
    assert "Nothing installed" in result.output


def test_status_after_install(config) -> None:
    runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config)])

    result = runner.invoke(app, ["status", "--config", str(config)])

    assert result.exit_code == 0
    assert "Profile:  etsi" in result.output
    assert f"Server:   {MCP_SERVER_NAME}" in result.output
    assert "!" not in result.output


def test_status_reports_a_problem(config) -> None:
    runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config)])
    (config / "agents" / "sdo-writer.md").unlink()

    result = runner.invoke(app, ["status", "--config", str(config)])

    assert result.exit_code == 0
    assert "! agent file missing: sdo-writer.md" in result.output
    assert "Run 'update' to restore them." in result.output


def test_status_without_agent(config) -> None:
    runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config), "--no-agent"])

    result = runner.invoke(app, ["status", "--config", str(config)])

    assert "Agent:    not installed" in result.output


def test_update_is_idempotent(config) -> None:
    runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config)])

    result = runner.invoke(app, ["update", "--profile", "etsi", "--config", str(config)])

    assert result.exit_code == 0
    assert "Server:" in result.output


def test_entry_prints_the_server_entry(tmp_path) -> None:
    root = tmp_path / "s"
    result = runner.invoke(app, ["entry", "--profile", "3gpp", "--skills-root", str(root)])

    assert result.exit_code == 0
    entry = json.loads(result.output)
    assert entry["type"] == "local"
    assert entry["command"][6:9] == ["serve", "--profile", "3gpp"]
    assert entry["command"][-2].lower() == "--root"
    assert entry["command"][-1].casefold() == str(root).casefold()


def test_entry_without_profile_lists_them() -> None:
    result = runner.invoke(app, ["entry"])

    assert result.exit_code == 1
    assert "Available profiles" in result.output


def test_entry_with_unknown_profile() -> None:
    result = runner.invoke(app, ["entry", "--profile", "nope"])

    assert result.exit_code == 1
    assert "Unknown profile" in result.output


def test_uninstall(config) -> None:
    runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config)])

    result = runner.invoke(app, ["uninstall", "--config", str(config)])

    assert result.exit_code == 0
    assert "Removed agent:" in result.output
    assert f"Removed server entry: mcp.servers.{MCP_SERVER_NAME}" in result.output
    assert not (config / "agents" / "sdo-writer.md").exists()
    assert MCP_SERVER_NAME not in json.loads((config / CONFIG_FILE).read_text(encoding="utf-8")).get("mcp", {}).get("servers", {})


def test_uninstall_without_install(config) -> None:
    result = runner.invoke(app, ["uninstall", "--config", str(config)])

    assert result.exit_code == 0
    assert "Nothing to remove" in result.output


def test_uninstall_reports_removed_legacy_skills(config) -> None:
    legacy = config / "skills" / "etsi-tools"
    legacy.mkdir(parents=True)
    (config / "sdo-writer.json").write_text(json.dumps({"version": 1, "skills": {"etsi-tools": "h"}}), encoding="utf-8")

    result = runner.invoke(app, ["uninstall", "--config", str(config)])

    assert result.exit_code == 0
    assert "Removed skill: etsi-tools" in result.output
    assert not legacy.exists()


def test_project_scope(tmp_path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    result = runner.invoke(app, ["init", "--profile", "itut", "--project", str(project)])

    assert result.exit_code == 0
    assert (project / ".opencode" / "agents" / "sdo-writer.md").is_file()
    assert (project / ".opencode" / CONFIG_FILE).is_file()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip()
