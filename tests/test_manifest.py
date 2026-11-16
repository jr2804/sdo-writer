"""Tests for the manifest."""

from __future__ import annotations

import json

from sdo_writer.manifest import Manifest, load_manifest, save_manifest


def test_round_trip(tmp_path) -> None:
    path = tmp_path / "sdo-writer.json"
    manifest = Manifest(profile="etsi", agent="sdo-writer.md", mcp_server="sdo-skills", mcp_config="opencode.json")
    save_manifest(path, manifest)

    loaded = load_manifest(path)
    assert loaded is not None
    assert loaded.profile == "etsi"
    assert loaded.agent == "sdo-writer.md"
    assert loaded.mcp_server == "sdo-skills"
    assert loaded.mcp_config == "opencode.json"
    assert loaded.skills == {}
    assert loaded.installed_at


def test_install_timestamp_is_filled_in(tmp_path) -> None:
    path = tmp_path / "sdo-writer.json"
    save_manifest(path, Manifest(profile="itut"))

    assert json.loads(path.read_text(encoding="utf-8"))["installed_at"]


def test_missing_manifest(tmp_path) -> None:
    assert load_manifest(tmp_path / "nope.json") is None


def test_broken_manifest(tmp_path) -> None:
    path = tmp_path / "sdo-writer.json"
    path.write_text("{not json", encoding="utf-8")

    assert load_manifest(path) is None


def test_manifest_with_wrong_types(tmp_path) -> None:
    path = tmp_path / "sdo-writer.json"
    path.write_text(
        json.dumps({"skills": "not a dict", "agent": 5, "mcp_server": 7, "mcp_config": None}),
        encoding="utf-8",
    )
    manifest = load_manifest(path)

    assert manifest is not None
    assert manifest.skills == {}
    assert manifest.agent is None
    assert manifest.mcp_server == ""
    assert manifest.mcp_config == ""


def test_manifest_that_is_not_an_object(tmp_path) -> None:
    path = tmp_path / "sdo-writer.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    assert load_manifest(path) is None


def test_legacy_manifest_keeps_its_skills(tmp_path) -> None:
    path = tmp_path / "sdo-writer.json"
    path.write_text(
        json.dumps({"version": 1, "profile": "etsi", "source": "vendored:/x", "skills": {"a": "hash"}}),
        encoding="utf-8",
    )
    manifest = load_manifest(path)

    assert manifest is not None
    assert manifest.installed_skills == ["a"]
    assert manifest.mcp_server == ""
