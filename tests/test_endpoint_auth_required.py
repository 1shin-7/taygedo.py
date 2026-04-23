"""End-to-end test of auth_required + AuthProvider injection."""

from __future__ import annotations

from dataclasses import dataclass

from tagedo.core import BearerAuthService, BearerProvider, Service, endpoint

from ._helpers import MockClient


@dataclass
class _Holder:
    access_token: str = ""


class _Anon(Service):
    auth_required = False

    @endpoint.get("/anon")
    async def call(self) -> dict[str, object]: ...


class _Authed(BearerAuthService):
    @endpoint.get("/authed")
    async def call(self) -> dict[str, object]: ...


async def test_auth_required_false_no_authorization_injected() -> None:
    holder = _Holder(access_token="should-not-appear")
    client = MockClient(auth_provider=BearerProvider(holder))
    svc = _Anon(client)
    await svc.call()
    assert "Authorization" not in client.sent[0].headers


async def test_auth_required_true_injects_token() -> None:
    holder = _Holder(access_token="bearer-xyz")
    client = MockClient(auth_provider=BearerProvider(holder))
    svc = _Authed(client)
    await svc.call()
    assert client.sent[0].headers["Authorization"] == "bearer-xyz"


async def test_auth_required_true_no_provider_skips_silently() -> None:
    client = MockClient(auth_provider=None)
    svc = _Authed(client)
    await svc.call()
    assert "Authorization" not in client.sent[0].headers
