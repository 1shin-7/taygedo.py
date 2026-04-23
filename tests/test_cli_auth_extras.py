"""auth logout / info / switch / list."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from taygedo.cli import app
from taygedo.cli._storage import Storage, StoredAccount
from taygedo.core import PreparedRequest, Response

from ._cli_fixtures import install_scripted_client, isolated_storage  # noqa: F401


def _read_storage(tmp_path: Path) -> Storage:
    """Open a *fresh* Storage so we see post-CLI on-disk state."""
    return Storage(config_dir=tmp_path)


def _seed(tmp_path: Path) -> None:
    s = Storage(config_dir=tmp_path)
    s.upsert_account(
        StoredAccount(uid=1, nickname="A", cellphone_masked="138****0001"),
        set_active=True,
    )
    s.upsert_account(
        StoredAccount(uid=2, nickname="B", cellphone_masked="138****0002"),
        set_active=False,
    )


def test_logout_default_removes_active(isolated_storage: Path) -> None:  # noqa: F811
    _seed(isolated_storage)
    result = CliRunner().invoke(app, ["auth", "logout"])
    assert result.exit_code == 0
    s = _read_storage(isolated_storage)
    assert s.get_account(1) is None
    assert s.get_account(2) is not None


def test_logout_uid_targeted(isolated_storage: Path) -> None:  # noqa: F811
    _seed(isolated_storage)
    result = CliRunner().invoke(app, ["auth", "logout", "--uid", "2"])
    assert result.exit_code == 0
    s = _read_storage(isolated_storage)
    assert s.get_account(1) is not None
    assert s.get_account(2) is None


def test_logout_all_clears_everything(isolated_storage: Path) -> None:  # noqa: F811
    _seed(isolated_storage)
    result = CliRunner().invoke(app, ["auth", "logout", "--all"])
    assert result.exit_code == 0
    s = _read_storage(isolated_storage)
    assert s.list_accounts() == []
    assert s.active_uid() is None


def test_logout_all_and_uid_mutually_exclusive(isolated_storage: Path) -> None:  # noqa: F811
    _seed(isolated_storage)
    result = CliRunner().invoke(app, ["auth", "logout", "--all", "--uid", "1"])
    assert result.exit_code != 0


def test_logout_with_no_account_errors(isolated_storage: Path) -> None:  # noqa: F811
    result = CliRunner().invoke(app, ["auth", "logout"])
    assert result.exit_code != 0


def test_switch_changes_active(isolated_storage: Path) -> None:  # noqa: F811
    _seed(isolated_storage)
    result = CliRunner().invoke(app, ["auth", "switch", "2"])
    assert result.exit_code == 0
    assert _read_storage(isolated_storage).active_uid() == 2


def test_switch_unknown_uid_errors(isolated_storage: Path) -> None:  # noqa: F811
    _seed(isolated_storage)
    result = CliRunner().invoke(app, ["auth", "switch", "999"])
    assert result.exit_code != 0


def test_list_renders_accounts(isolated_storage: Path) -> None:  # noqa: F811
    _seed(isolated_storage)
    result = CliRunner().invoke(app, ["auth", "list"])
    assert result.exit_code == 0
    # uid + nickname appear in the table output.
    assert "1" in result.output and "A" in result.output
    assert "2" in result.output and "B" in result.output


def test_list_json(isolated_storage: Path) -> None:  # noqa: F811
    _seed(isolated_storage)
    result = CliRunner().invoke(app, ["auth", "list", "--json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert {a["uid"] for a in parsed} == {1, 2}


def test_list_when_empty(isolated_storage: Path) -> None:  # noqa: F811
    result = CliRunner().invoke(app, ["auth", "list"])
    assert result.exit_code == 0
    assert "尚未登录" in result.output


def test_info_with_no_account_errors(isolated_storage: Path) -> None:  # noqa: F811
    result = CliRunner().invoke(app, ["auth", "info"])
    assert result.exit_code != 0


def _user_full_info_responder() -> Any:
    def respond(req: PreparedRequest) -> Response:
        if req.url.endswith("/usercenter/api/getUserFullInfo"):
            return Response(
                status_code=200,
                headers={"content-type": "application/json"},
                content=json.dumps(
                    {
                        "code": 0,
                        "ok": True,
                        "data": {
                            "user": {
                                "uid": 1,
                                "account": "x",
                                "nickname": "AliveServer",
                                "avatar": "",
                                "createTime": 0,
                                "updateTime": 0,
                                "gender": -1,
                            },
                            "userStat": {"uid": 1, "createTime": 0, "updateTime": 0},
                            "privacySetting": {
                                "uid": 1, "privacyCollect": True,
                                "createTime": 0, "updateTime": 0,
                            },
                            "auths": [],
                            "audit": {},
                            "certification": {},
                            "inBlackList": False,
                        },
                    },
                ).encode("utf-8"),
            )
        return Response(
            status_code=200,
            headers={"content-type": "application/json"},
            content=b'{"code":0,"ok":true,"data":{}}',
        )

    return respond


def test_info_calls_get_user_full_info(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _user_full_info_responder())
    result = CliRunner().invoke(app, ["auth", "info"])
    assert result.exit_code == 0, result.output
    assert "AliveServer" in result.output
