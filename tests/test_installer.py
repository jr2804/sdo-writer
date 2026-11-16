"""Tests for the installer."""

from __future__ import annotations

import json

from sdo_writer.installer import install, status, uninstall
from sdo_writer.mcp import MCP_SERVER_NAME, server_entry
from sdo_writer.paths import CONFIG_FILE, CONFIG_FILE_JSONC, config_file
from sdo_writer.profile import load_profile


def test_install_writes_the_agent_the_entry_and_the_manifest(config) -> None:
    report = install(load_profile("etsi"), config)

    assert report.profile == "etsi"
    assert report.agent_path is not None
    assert report.agent_path.is_file()
    assert report.mcp_written
    assert not report.mcp_pending
    assert (config / "sdo-writer.json").is_file()

    written = json.loads((config / CONFIG_FILE).read_text(encoding="utf-8"))
    entry = written["mcp"]["servers"][MCP_SERVER_NAME]
    assert entry["type"] == "local"
    assert entry["command"][8] == "etsi"


def test_install_copies_no_skills(config) -> None:
    install(load_profile("etsi"), config)

    assert not (config / "skills").exists()


def test_install_passes_the_roots_to_the_server(config, tmp_path) -> None:
    install(load_profile("itut"), config, roots=[tmp_path / "skills"])

    written = json.loads((config / CONFIG_FILE).read_text(encoding="utf-8"))
    command = written["mcp"]["servers"][MCP_SERVER_NAME]["command"]
    assert command[-2:] == ["--root", str(tmp_path / "skills")]


def test_install_can_skip_the_agent(config) -> None:
    report = install(load_profile("etsi"), config, write_agent=False)

    assert report.agent_path is None
    assert not (config / "agents").exists()
    assert report.mcp_written
    assert json.loads((config / "sdo-writer.json").read_text(encoding="utf-8"))["agent"] is None


def test_install_keeps_other_servers(config) -> None:
    config.mkdir(parents=True)
    (config / CONFIG_FILE).write_text(json.dumps({"mcp": {"servers": {"other": {"type": "local"}}}}), encoding="utf-8")

    install(load_profile("etsi"), config)

    servers = json.loads((config / CONFIG_FILE).read_text(encoding="utf-8"))["mcp"]["servers"]
    assert set(servers) == {"other", MCP_SERVER_NAME}


def test_install_into_a_jsonc_configuration_reports_the_entry(config) -> None:
    config.mkdir(parents=True)
    jsonc = config / CONFIG_FILE_JSONC
    original = '{\n  // mine\n  "mcp": {"servers": {}}\n}\n'
    jsonc.write_text(original, encoding="utf-8")

    report = install(load_profile("etsi"), config)

    assert not report.mcp_written
    assert report.mcp_pending == server_entry("etsi", [])
    assert jsonc.read_text(encoding="utf-8") == original
    assert "sdo-skills-mcp" in report.pending_json
    assert report.config_path == jsonc


def test_config_file_falls_back_to_json(tmp_path) -> None:
    assert config_file(tmp_path).name == CONFIG_FILE


def test_install_removes_skills_left_by_an_earlier_install(config) -> None:
    vendored = config / "skills" / "sdo-writing"
    vendored.mkdir(parents=True)
    (vendored / "SKILL.md").write_text("---\nname: sdo-writing\n---\nold\n", encoding="utf-8")
    mine = config / "skills" / "mine"
    mine.mkdir(parents=True)
    manifest = {
        "version": 1,
        "profile": "etsi",
        "installed_at": "2026-01-01T00:00:00+00:00",
        "skills": {"sdo-writing": "hash"},
        "agent": "sdo-writer.md",
    }
    (config / "sdo-writer.json").write_text(json.dumps(manifest), encoding="utf-8")

    report = install(load_profile("etsi"), config)

    assert report.removed_skills == ["sdo-writing"]
    assert not vendored.exists()
    assert mine.is_dir()


def test_status_without_install(tmp_path) -> None:
    manifest, problems = status(tmp_path / "nothing")

    assert manifest is None
    assert problems == []


def test_status_after_install_is_clean(config) -> None:
    install(load_profile("etsi"), config)

    manifest, problems = status(config)

    assert manifest is not None
    assert manifest.profile == "etsi"
    assert manifest.mcp_server == MCP_SERVER_NAME
    assert manifest.mcp_config == CONFIG_FILE
    assert problems == []


def test_status_reports_a_missing_agent(config) -> None:
    install(load_profile("etsi"), config)
    (config / "agents" / "sdo-writer.md").unlink()

    _, problems = status(config)

    assert problems == ["agent file missing: sdo-writer.md"]


def test_status_reports_a_missing_server_entry(config) -> None:
    install(load_profile("etsi"), config)
    (config / CONFIG_FILE).unlink()

    _, problems = status(config)

    assert problems == [f"server entry missing: {MCP_SERVER_NAME}"]


def test_status_reports_a_configuration_it_cannot_read(config) -> None:
    install(load_profile("etsi"), config)
    (config / CONFIG_FILE).write_text("{broken", encoding="utf-8")

    _, problems = status(config)

    assert problems == ["configuration is not plain JSON; check the server entry by hand"]


def test_uninstall_removes_the_agent_the_entry_and_the_manifest(config) -> None:
    install(load_profile("etsi"), config)

    agent_path, removed_server, removed_skills = uninstall(config)

    assert agent_path is not None
    assert not agent_path.exists()
    assert removed_server
    assert removed_skills == []
    assert not (config / "sdo-writer.json").exists()
    assert MCP_SERVER_NAME not in json.loads((config / CONFIG_FILE).read_text(encoding="utf-8")).get("mcp", {}).get("servers", {})


def test_uninstall_without_install(config) -> None:
    agent_path, removed_server, removed_skills = uninstall(config)

    assert agent_path is None
    assert not removed_server
    assert removed_skills == []


def test_uninstall_tolerates_an_already_missing_agent(config) -> None:
    install(load_profile("etsi"), config)
    (config / "agents" / "sdo-writer.md").unlink()

    agent_path, removed_server, _ = uninstall(config)

    assert agent_path is None
    assert removed_server
