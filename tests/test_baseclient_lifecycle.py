from __future__ import annotations

import pytest

from tagedo.core import BaseClient


async def test_session_unset_before_aenter() -> None:
    client = BaseClient(base_url="https://example.test")
    with pytest.raises(RuntimeError, match="Session not initialised"):
        _ = client.session


async def test_aenter_creates_session_and_aexit_closes_it() -> None:
    client = BaseClient(base_url="https://example.test")
    async with client as opened:
        assert opened is client
        assert client.session is not None
    with pytest.raises(RuntimeError):
        _ = client.session


async def test_external_session_is_not_owned(monkeypatch: pytest.MonkeyPatch) -> None:
    closed = []

    class FakeSession:
        async def close(self) -> None:
            closed.append(True)

    fake = FakeSession()
    client = BaseClient(base_url="https://example.test", session=fake)  # type: ignore[arg-type]
    async with client:
        assert client.session is fake
    assert not closed  # external session must not be closed by the client
