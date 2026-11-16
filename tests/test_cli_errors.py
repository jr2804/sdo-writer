"""Tests for the failure paths of the command line interface."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from sdo_writer.cli import app as app_module, commands as commands_module
from sdo_writer.cli.app import app
from sdo_writer.profile import ProfileError

runner = CliRunner()


def test_broken_profile_is_reported(monkeypatch, config) -> None:
    def boom(profile_id: str):
        msg = "profile is broken"
        raise ProfileError(msg)

    monkeypatch.setattr(commands_module, "load_profile", boom)

    result = runner.invoke(app, ["init", "--profile", "etsi", "--config", str(config)])

    assert result.exit_code == 1
    assert "profile is broken" in result.output


def test_init_without_a_config_option_uses_the_global_directory(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    result = runner.invoke(app, ["init", "--profile", "etsi", "--dry-run"])

    assert result.exit_code == 0
    assert str(tmp_path / "opencode") in result.output


def test_status_uses_the_global_directory(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    result = runner.invoke(app, ["status"])

    assert result.exit_code == 1
    assert str(tmp_path / "opencode") in result.output


def test_version_falls_back_when_the_package_is_not_installed(monkeypatch) -> None:
    def boom(name: str) -> str:
        msg = "not installed"
        raise RuntimeError(msg)

    monkeypatch.setattr(app_module, "version", boom)

    assert app_module._get_version() == "0.0.0"


def test_main_entry_point(monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["sdo-writer", "--version"])

    with pytest.raises(SystemExit):
        app_module.main()
