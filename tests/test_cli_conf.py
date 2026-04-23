"""tagedo conf show / set / path / edit."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from tagedo.cli import app
from tagedo.cli._storage import Storage

from ._cli_fixtures import isolated_storage  # noqa: F401


def test_conf_show_creates_default_skeleton_then_prints(
    isolated_storage: Path,  # noqa: F811
) -> None:
    # Trigger creation by reading once.
    Storage(config_dir=isolated_storage).load_config()
    result = CliRunner().invoke(app, ["conf", "show"])
    assert result.exit_code == 0
    assert "[output]" in result.output
    assert 'format = "table"' in result.output


def test_conf_set_persists(isolated_storage: Path) -> None:  # noqa: F811
    result = CliRunner().invoke(app, ["conf", "set", "output.format", "json"])
    assert result.exit_code == 0
    assert Storage(config_dir=isolated_storage).get_config("output.format") == "json"


def test_conf_set_coerces_bool(isolated_storage: Path) -> None:  # noqa: F811
    CliRunner().invoke(app, ["conf", "set", "feat.flag", "true"])
    assert Storage(config_dir=isolated_storage).get_config("feat.flag") is True


def test_conf_set_coerces_int(isolated_storage: Path) -> None:  # noqa: F811
    CliRunner().invoke(app, ["conf", "set", "network.timeout", "60"])
    assert Storage(config_dir=isolated_storage).get_config("network.timeout") == 60


def test_conf_path_prints_both_paths(isolated_storage: Path) -> None:  # noqa: F811
    result = CliRunner().invoke(app, ["conf", "path"])
    assert result.exit_code == 0
    assert "data.json" in result.output
    assert "config.toml" in result.output


def test_conf_edit_invokes_editor(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[list[str]] = []
    monkeypatch.setattr(
        "tagedo.cli.conf.subprocess.call",
        lambda argv: (captured.append(argv) or 0),
    )
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.setenv("EDITOR", "true")
    result = CliRunner().invoke(app, ["conf", "edit"])
    assert result.exit_code == 0
    assert captured and captured[0][0] == "true"
    assert captured[0][1].endswith("config.toml")
