"""Tests for the MCP server entry."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sdo_writer.mcp import (
    MCP_SERVER_NAME,
    SERVER_PYTHON,
    McpError,
    entry_json,
    has_server,
    read_config,
    remove_server,
    server_command,
    server_entry,
    with_server,
    without_server,
    write_server,
)
from sdo_writer.paths import CONFIG_FILE, CONFIG_FILE_JSONC


def test_server_command_carries_the_profile() -> None:
    command = server_command("etsi", [])

    assert command[:5] == ["uvx", "--python", SERVER_PYTHON, "--from", "git+https://github.com/jr2804/sdo-skills-mcp"]
    assert command[5:8] == ["sdo-skills-mcp", "serve", "--profile"]
    assert command[8] == "etsi"
    assert "--root" not in command


def test_server_command_passes_every_root(tmp_path) -> None:
    first, second = tmp_path / "a", tmp_path / "b"
    command = server_command("itut", [first, second])

    assert command[-4:] == ["--root", str(first), "--root", str(second)]


def test_server_entry_is_a_local_server() -> None:
    entry = server_entry("3gpp", [])

    assert entry["type"] == "local"
    assert entry["command"][8] == "3gpp"


def test_with_server_keeps_other_servers() -> None:
    existing = _config_with({"other": {"type": "local", "command": ["x"]}})
    merged = with_server(existing, MCP_SERVER_NAME, server_entry("etsi", []))

    assert set(merged["mcp"]["servers"]) == {"other", MCP_SERVER_NAME}
    assert existing["mcp"]["servers"] == {"other": {"type": "local", "command": ["x"]}}


def test_with_server_creates_the_section() -> None:
    merged = with_server({}, MCP_SERVER_NAME, server_entry("etsi", []))

    assert merged["mcp"]["servers"][MCP_SERVER_NAME]["type"] == "local"


def test_with_server_rejects_a_malformed_mcp_section() -> None:
    with pytest.raises(McpError, match="'mcp' is not an object"):
        with_server({"mcp": []}, MCP_SERVER_NAME, {})


def test_with_server_rejects_a_malformed_servers_section() -> None:
    with pytest.raises(McpError, match="'mcp.servers' is not an object"):
        with_server(_config_with([]), MCP_SERVER_NAME, {})


def test_without_server_removes_only_the_entry() -> None:
    existing = _config_with({"other": {}, MCP_SERVER_NAME: {}})
    stripped = without_server(existing, MCP_SERVER_NAME)

    assert stripped["mcp"]["servers"] == {"other": {}}
    assert MCP_SERVER_NAME in existing["mcp"]["servers"]


def test_without_server_tolerates_a_missing_section() -> None:
    assert without_server({}, MCP_SERVER_NAME) == {}
    assert without_server({"mcp": []}, MCP_SERVER_NAME) == {"mcp": []}


def test_entry_json_is_indented() -> None:
    assert "\n  " in entry_json(server_entry("etsi", []))


def test_read_config_of_a_missing_file_is_empty() -> None:
    assert read_config(Path("does-not-exist.json")) == {}


def test_read_config_of_a_broken_file_is_unknown(tmp_path) -> None:
    path = tmp_path / "opencode.json"
    path.write_text("{broken", encoding="utf-8")

    assert read_config(path) is None


def test_read_config_of_a_jsonc_file_is_unknown(tmp_path) -> None:
    path = tmp_path / "opencode.jsonc"
    path.write_text('{\n  // a comment\n  "mcp": {}\n}\n', encoding="utf-8")

    assert read_config(path) is None


def test_read_config_of_a_non_object_is_unknown(tmp_path) -> None:
    path = tmp_path / "opencode.json"
    path.write_text("[1, 2]", encoding="utf-8")

    assert read_config(path) is None


def test_has_server() -> None:
    config = _config_with({MCP_SERVER_NAME: {}})

    assert has_server(config, MCP_SERVER_NAME) is True
    assert has_server(config, "other") is False
    assert has_server(None, MCP_SERVER_NAME) is None
    assert has_server({"mcp": []}, MCP_SERVER_NAME) is False


def _config_with(servers: object) -> dict:
    return {"mcp": {"servers": servers}}


def test_write_server_adds_the_schema_and_the_entry(tmp_path) -> None:
    path = tmp_path / CONFIG_FILE
    assert write_server(path, MCP_SERVER_NAME, server_entry("etsi", [])) is None

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["$schema"] == "https://opencode.ai/config.json"
    assert written["mcp"]["servers"][MCP_SERVER_NAME]["type"] == "local"
    assert path.read_text(encoding="utf-8").endswith("\n")
    assert list(written) == ["$schema", "mcp"]
    assert list(path.read_text(encoding="utf-8").splitlines())[1] == '  "$schema": "https://opencode.ai/config.json",'


def test_write_server_keeps_an_existing_schema(tmp_path) -> None:
    path = tmp_path / CONFIG_FILE
    path.write_text(json.dumps({"$schema": "custom", "theme": "dark"}), encoding="utf-8")
    write_server(path, MCP_SERVER_NAME, server_entry("etsi", []))

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["$schema"] == "custom"
    assert written["theme"] == "dark"


def test_write_server_leaves_a_jsonc_file_alone(tmp_path) -> None:
    path = tmp_path / CONFIG_FILE_JSONC
    original = '{\n  // keep me\n  "mcp": {}\n}\n'
    path.write_text(original, encoding="utf-8")

    pending = write_server(path, MCP_SERVER_NAME, server_entry("etsi", []))

    assert pending is not None
    assert pending["type"] == "local"
    assert path.read_text(encoding="utf-8") == original


def test_remove_server(tmp_path) -> None:
    path = tmp_path / CONFIG_FILE
    write_server(path, MCP_SERVER_NAME, server_entry("etsi", []))

    assert remove_server(path, MCP_SERVER_NAME) is True
    assert MCP_SERVER_NAME not in json.loads(path.read_text(encoding="utf-8"))["mcp"]["servers"]


def test_remove_server_from_a_jsonc_file_does_nothing(tmp_path) -> None:
    path = tmp_path / CONFIG_FILE_JSONC
    path.write_text("{ // comment\n}\n", encoding="utf-8")

    assert remove_server(path, MCP_SERVER_NAME) is False
    assert "// comment" in path.read_text(encoding="utf-8")
