"""401 → on_unauthorized → retry-once middleware."""

from __future__ import annotations

from typing import Any

import orjson

from taygedo.core import BearerAuthService, PreparedRequest, Response, Service, endpoint

from ._helpers import MockClient


def _make_responder(*statuses: int) -> Any:
    """Return a responder that yields given status codes in order."""
    seq = list(statuses)

    def responder(_req: PreparedRequest) -> Response:
        status = seq.pop(0) if seq else 200
        return Response(
            status_code=status,
            headers={"content-type": "application/json"},
            content=orjson.dumps({"code": 0, "ok": True}),
        )

    return responder


class _Refreshable(Service):
    """Custom Service exercising the retry hook directly (no AuthService)."""

    refresh_calls: int = 0
    refresh_returns: bool = True
    auth_required = False

    async def on_unauthorized(self) -> bool:
        self.refresh_calls += 1
        return self.refresh_returns

    @endpoint.get("/x")
    async def call(self) -> dict[str, object]: ...


async def test_401_then_200_succeeds_after_one_retry() -> None:
    client = MockClient(_make_responder(401, 200))
    svc = _Refreshable(client)
    svc.refresh_returns = True
    result = await svc.call()
    assert result == {"code": 0, "ok": True}
    assert svc.refresh_calls == 1
    assert len(client.sent) == 2


async def test_401_with_failed_refresh_propagates_error() -> None:
    import pytest

    from taygedo.core import ApiError

    client = MockClient(_make_responder(401))
    svc = _Refreshable(client)
    svc.refresh_returns = False
    with pytest.raises(ApiError) as exc:
        await svc.call()
    assert exc.value.status_code == 401
    assert svc.refresh_calls == 1
    assert len(client.sent) == 1


async def test_401_then_401_only_retries_once() -> None:
    import pytest

    from taygedo.core import ApiError

    client = MockClient(_make_responder(401, 401))
    svc = _Refreshable(client)
    svc.refresh_returns = True
    with pytest.raises(ApiError) as exc:
        await svc.call()
    assert exc.value.status_code == 401
    assert svc.refresh_calls == 1
    assert len(client.sent) == 2


async def test_bearer_auth_service_delegates_to_client_auth() -> None:
    """``BearerAuthService.on_unauthorized`` calls ``client.auth.on_unauthorized``."""

    class FakeAuth:
        calls = 0

        async def on_unauthorized(self) -> bool:
            type(self).calls += 1
            return True

    class WithAuth(BearerAuthService):
        auth_required = False  # avoid needing a provider for this test

        @endpoint.get("/y")
        async def call(self) -> dict[str, object]: ...

    client = MockClient(_make_responder(401, 200))
    client.auth = FakeAuth()  # type: ignore[attr-defined]
    svc = WithAuth(client)
    result = await svc.call()
    assert result == {"code": 0, "ok": True}
    assert FakeAuth.calls == 1
