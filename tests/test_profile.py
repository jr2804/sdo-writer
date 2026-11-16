"""Tests for the profiles."""

from __future__ import annotations

import pytest

import sdo_writer.profile as module
from sdo_writer.profile import ProfileError, available_profiles, load_profile


def test_bundled_profiles() -> None:
    assert available_profiles() == ["3gpp", "etsi", "itut"]


@pytest.mark.parametrize("profile_id", ["3gpp", "etsi", "itut"])
def test_load_bundled_profile(profile_id: str) -> None:
    profile = load_profile(profile_id)

    assert profile.id == profile_id
    assert profile.title
    assert profile.description
    assert profile.agent_name == "sdo-writer"
    assert profile.mode == "primary"
    assert profile.color.startswith("#")
    assert "mise *" in profile.tools_allow
    assert profile.notes.strip()


def test_unknown_profile() -> None:
    with pytest.raises(ProfileError, match="Unknown profile"):
        load_profile("nope")


def test_broken_profile(monkeypatch) -> None:
    _fake_files(monkeypatch, "title = 'x'\n")
    with pytest.raises(ProfileError, match="missing 'description'"):
        load_profile("etsi")


def test_profile_with_invalid_toml(monkeypatch) -> None:
    _fake_files(monkeypatch, "title = 'x\n")
    with pytest.raises(ProfileError, match="is not valid TOML"):
        load_profile("etsi")


def test_profile_with_a_malformed_agent_section(monkeypatch) -> None:
    _fake_files(monkeypatch, "title = 'x'\ndescription = 'y'\nagent = 'not a table'\n")
    with pytest.raises(ProfileError, match="malformed"):
        load_profile("etsi")


def test_profile_defaults() -> None:
    profile = module._build("x", {"title": "T", "description": "D"})

    assert profile.agent_name == "sdo-writer"
    assert profile.mode == "primary"
    assert profile.color == "#2f6f9f"
    assert profile.tools_allow == ()
    assert profile.notes == ""


def _fake_files(monkeypatch, content: str) -> None:
    """Make the profile package serve a fixed TOML text."""

    class FakeFile:
        def is_file(self) -> bool:
            return True

        def read_text(self, encoding: str = "utf-8") -> str:
            return content

    class FakeDir:
        def joinpath(self, name: str) -> FakeFile:
            return FakeFile()

        def iterdir(self):
            return []

    monkeypatch.setattr(module, "files", lambda package: FakeDir())
