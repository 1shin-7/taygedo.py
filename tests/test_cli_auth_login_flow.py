"""auth login covers the four flag-mode permutations."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import pytest
from click.testing import CliRunner

from taygedo.cli import app
from taygedo.cli._storage import Storage
from taygedo.core import PreparedRequest, Response

from ._cli_fixtures import install_scripted_client, isolated_storage  # noqa: F401


def _ok(payload: dict[str, Any], status: int = 200) -> Response:
    return Response(
        status_code=status,
        headers={"content-type": "application/json"},
        content=json.dumps(payload).encode("utf-8"),
    )


def _login_responder() -> Callable[[PreparedRequest], Response]:
    """Map URL paths → mocked envelopes for the full login chain."""

    def respond(req: PreparedRequest) -> Response:
        if req.url.endswith("/sendPhoneCaptchaWithOutLogin"):
            return _ok({"code": 0, "message": "OK"})
        if req.url.endswith("/sms/new/login"):
            return _ok(
                {
                    "code": 0,
                    "message": "ok",
                    "result": {
                        "userId": 9911,
                        "username": "u",
                        "nickname": "alice",
                        "token": "laohu-tok",
                    },
                },
            )
        if req.url.endswith("/usercenter/api/login"):
            return _ok(
                {
                    "code": 0,
                    "ok": True,
                    "data": {
                        "accessToken": "bbs-at",
                        "refreshToken": "bbs-rt",
                        "uid": 5555,
                    },
                },
            )
        if req.url.endswith("/usercenter/api/getUserFullInfo"):
            return _ok(
                {
                    "code": 0,
                    "ok": True,
                    "data": {
                        "user": {
                            "uid": 5555,
                            "account": "x",
                            "nickname": "AliceServer",
                            "avatar": "",
                            "createTime": 0,
                            "updateTime": 0,
                            "gender": -1,
                        },
                        "userStat": {"uid": 5555, "createTime": 0, "updateTime": 0},
                        "privacySetting": {"uid": 5555, "privacyCollect": True,
                                           "createTime": 0, "updateTime": 0},
                        "auths": [],
                        "audit": {},
                        "certification": {},
                        "inBlackList": False,
                    },
                },
            )
        return _ok({"code": 0, "ok": True})

    return respond


def test_login_fully_non_interactive_persists_account(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_scripted_client(monkeypatch, _login_responder())
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["auth", "login", "--cellphone", "13800138000", "--captcha", "123456"],
    )
    assert result.exit_code == 0, result.output
    assert "登录成功" in result.output

    s = Storage(config_dir=isolated_storage)
    accounts = s.list_accounts()
    assert len(accounts) == 1
    a = accounts[0]
    assert a.uid == 5555
    assert a.nickname == "AliceServer"
    assert a.cellphone_masked == "138****8000"
    assert a.access_token == "bbs-at"
    assert a.refresh_token == "bbs-rt"
    assert a.laohu_token == "laohu-tok"
    assert a.laohu_user_id == 9911
    assert s.active_uid() == 5555


def test_login_captcha_without_cellphone_rejected(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_scripted_client(monkeypatch, _login_responder())
    runner = CliRunner()
    result = runner.invoke(app, ["auth", "login", "--captcha", "123456"])
    assert result.exit_code != 0
    assert "--cellphone" in result.output


def test_login_half_interactive_prompts_for_captcha(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_scripted_client(monkeypatch, _login_responder())

    async def _captcha() -> str:
        return "654321"

    monkeypatch.setattr("taygedo.cli.auth.prompt_captcha", _captcha)
    runner = CliRunner()
    result = runner.invoke(app, ["auth", "login", "--cellphone", "13800138000"])
    assert result.exit_code == 0, result.output
    assert "验证码已发送" in result.output
    assert "登录成功" in result.output


def test_login_fully_interactive(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_scripted_client(monkeypatch, _login_responder())

    async def _cell() -> str:
        return "13800138000"

    async def _cap() -> str:
        return "123456"

    monkeypatch.setattr("taygedo.cli.auth.prompt_cellphone", _cell)
    monkeypatch.setattr("taygedo.cli.auth.prompt_captcha", _cap)
    runner = CliRunner()
    result = runner.invoke(app, ["auth", "login"])
    assert result.exit_code == 0, result.output
    assert "登录成功" in result.output


def test_login_form_body_is_signed(
    isolated_storage: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sanity: SignLaohu actually fires; ``sign`` field is present in the body."""
    seen: list[PreparedRequest] = []

    def respond(req: PreparedRequest) -> Response:
        seen.append(req)
        return _login_responder()(req)

    install_scripted_client(monkeypatch, respond)

    async def _cap() -> str:
        return "123456"

    monkeypatch.setattr("taygedo.cli.auth.prompt_captcha", _cap)
    runner = CliRunner()
    runner.invoke(app, ["auth", "login", "--cellphone", "13800138000"])

    captcha_req = next(r for r in seen if r.url.endswith("/sendPhoneCaptchaWithOutLogin"))
    assert captcha_req.form is True
    assert "sign" in captcha_req.params
    assert captcha_req.params["cellphone"] == "13800138000"
    sms_req = next(r for r in seen if r.url.endswith("/sms/new/login"))
    assert "sign" in sms_req.params
    assert sms_req.params["cellphone"] != "13800138000"
    body = parse_qs("&".join(f"{k}={v}" for k, v in sms_req.params.items()))
    assert "captcha" in body
