"""Shared CLI test fixtures.

Two pieces of infrastructure are reused across every CLI test:

1. ``isolated_storage`` — point ``taygedo.cli._storage.CONFIG_DIR``
   (and the cached ``_shared.storage`` singleton) at a tmp_path so tests
   never touch the user's real ``~/.config/taygedo``.
2. ``ScriptedClient`` — a TaygedoClient subclass whose ``send`` returns
   pre-canned responses, so CLI commands run their full async path without
   network I/O.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import orjson
import pytest

from taygedo.cli import _shared, _storage
from taygedo.client import SessionState, TaygedoClient
from taygedo.core import PreparedRequest, Response, Service


@pytest.fixture
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Redirect storage I/O at ``tmp_path``."""
    monkeypatch.setattr(_storage, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(_storage, "DATA_FILE", tmp_path / "data.json")
    monkeypatch.setattr(_storage, "CONFIG_FILE", tmp_path / "config.toml")
    _shared.storage.cache_clear()
    monkeypatch.setattr(_shared, "storage", lambda: _storage.Storage(config_dir=tmp_path))
    yield tmp_path


def _make_response(payload: dict[str, Any] | bytes, status: int = 200) -> Response:
    body = payload if isinstance(payload, bytes) else orjson.dumps(payload)
    return Response(
        status_code=status,
        headers={"content-type": "application/json"},
        content=body,
    )


class ScriptedClient(TaygedoClient):
    """TaygedoClient with a programmable transport.

    Responder is a callable ``(prepared) -> Response | dict``. Dicts are
    auto-JSON-encoded and given a 200 status. Each call appends its
    ``PreparedRequest`` to ``self.sent`` for later inspection.
    """

    def __init__(
        self,
        responder: Callable[[PreparedRequest], Response | dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.sent: list[PreparedRequest] = []
        self._responder = responder or (lambda _req: {})

    async def __aenter__(self) -> ScriptedClient:  # type: ignore[override]
        return self

    async def __aexit__(self, *exc: object) -> None:
        return None

    async def send(  # type: ignore[override]
        self,
        prepared: PreparedRequest,
        *,
        service: Service | None = None,
    ) -> Response:
        if (
            service is not None
            and getattr(type(service), "auth_required", False)
            and self._auth_provider is not None
        ):
            prepared = self._auth_provider.apply(prepared)
        self.sent.append(prepared)
        result = self._responder(prepared)
        if isinstance(result, Response):
            return result
        return _make_response(result)


def install_scripted_client(
    monkeypatch: pytest.MonkeyPatch,
    responder: Callable[[PreparedRequest], Response | dict[str, Any]],
    *,
    seed_session: SessionState | None = None,
) -> list[ScriptedClient]:
    """Make the CLI use a ScriptedClient instead of the real TaygedoClient.

    Returns a list that grows as each command instantiates a fresh client;
    inspect e.g. ``clients[0].sent`` to assert against requests issued.
    """
    instances: list[ScriptedClient] = []

    def factory(*args: Any, **kwargs: Any) -> ScriptedClient:
        c = ScriptedClient(responder=responder, **kwargs)
        if seed_session is not None:
            for fld in ("access_token", "refresh_token", "uid", "laohu_token", "laohu_user_id"):
                setattr(c.session_state, fld, getattr(seed_session, fld))
        instances.append(c)
        return c

    monkeypatch.setattr("taygedo.cli.auth.TaygedoClient", factory)
    monkeypatch.setattr("taygedo.cli._shared.TaygedoClient", factory)
    return instances
