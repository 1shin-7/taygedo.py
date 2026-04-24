"""ht (& tof alias) subcommands + role_id caching via BindRoleService."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import orjson
import pytest
from click.testing import CliRunner

from taygedo.cli import app
from taygedo.cli._storage import Storage, StoredAccount
from taygedo.core import PreparedRequest, Response

from ._cli_fixtures import install_scripted_client, isolated_storage  # noqa: F401


def _ok(payload: dict[str, Any]) -> Response:
    return Response(
        status_code=200,
        headers={"content-type": "application/json"},
        content=orjson.dumps(payload),
    )


_RECORD_PAYLOAD = {
    "code": 0, "ok": True,
    "data": {
        "roleid": "1000000000001",
        "rolename": "Cloud",
        "userid": "u",
        "lev": 100,
        "shengelev": "11_3",
        "maxgs": 269447,
        "imitationCount": 86,
        "achievementpointall": "7201",
        "weaponinfo": [
            {
                "ID": 6960, "IDStr": "Paradox_fire", "name": "EP-7000",
                "Star": 6, "Color": 4, "Lev": 200,
                "MatrixInfoList": [],
            },
        ],
        "imitationlist": [{"name": "TestImitation", "ID": "imitation_4"}],
        "mountlist": [{"name": "TestMount", "ID": "Mount1"}],
        "dressfashionlist": [{"name": "TestFashion", "ID": "fashion_dress_13"}],
    },
}


def _seed(tmp_path: Path, *, ht_role_id: int = 1000000000001) -> None:
    Storage(config_dir=tmp_path).upsert_account(
        StoredAccount(
            uid=10000001,
            nickname="z",
            cellphone_masked="138****0000",
            access_token="at",
            refresh_token="rt",
            laohu_token="lt",
            laohu_user_id=999,
            device_id="dev",
            ht_role_id=ht_role_id,
        ),
        set_active=True,
    )


def _record_responder() -> Callable[[PreparedRequest], Response]:
    def respond(req: PreparedRequest) -> Response:
        if req.url.endswith("/ht/getRoleGameRecord"):
            return _ok(_RECORD_PAYLOAD)
        if req.url.endswith("/getGameBindRole"):
            return _ok(
                {
                    "code": 0, "ok": True,
                    "data": {
                        "gameId": 1256,
                        "roleId": 1000000000001,
                        "roleName": "Cloud",
                        "serverId": 14508,
                        "serverName": "x",
                        "account": "u",
                        "lev": 100,
                    },
                },
            )
        return _ok({"code": 0, "ok": True})

    return respond


@pytest.mark.parametrize(
    ("subcommand", "needle"),
    [
        ("info", "Cloud"),
        ("record", "EP-7000"),
        ("weapon", "EP-7000"),
        ("imitation", "TestImitation"),
        ("mount", "TestMount"),
        ("fashion", "TestFashion"),
    ],
)
def test_ht_subcommand(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
    subcommand: str,
    needle: str,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _record_responder())
    result = CliRunner().invoke(app, ["ht", subcommand])
    assert result.exit_code == 0, result.output
    assert needle in result.output


def test_tof_alias_dispatches_to_ht(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    install_scripted_client(monkeypatch, _record_responder())
    result = CliRunner().invoke(app, ["tof", "weapon"])
    assert result.exit_code == 0, result.output
    assert "EP-7000" in result.output


def test_role_id_resolved_via_bind_role_when_uncached(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage, ht_role_id=0)
    seen: list[str] = []

    def respond(req: PreparedRequest) -> Response:
        seen.append(req.url)
        return _record_responder()(req)

    install_scripted_client(monkeypatch, respond)
    result = CliRunner().invoke(app, ["ht", "info"])
    assert result.exit_code == 0, result.output
    # Both endpoints were hit on the cold path.
    assert any("getGameBindRole" in u for u in seen)
    assert any("getRoleGameRecord" in u for u in seen)
    # And the result was cached back to storage.
    cached = Storage(config_dir=isolated_storage).get_account(10000001)
    assert cached is not None
    assert cached.ht_role_id == 1000000000001


def test_role_id_cached_skips_bind_role_lookup(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(isolated_storage)
    seen: list[str] = []

    def respond(req: PreparedRequest) -> Response:
        seen.append(req.url)
        return _record_responder()(req)

    install_scripted_client(monkeypatch, respond)
    result = CliRunner().invoke(app, ["ht", "info"])
    assert result.exit_code == 0
    assert not any("getGameBindRole" in u for u in seen)
