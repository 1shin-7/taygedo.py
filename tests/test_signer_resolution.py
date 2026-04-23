from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel

from taygedo.core import PreparedRequest, Service, endpoint, service

from ._helpers import MockClient


class Out(BaseModel):
    ok: bool


@dataclass(slots=True)
class TaggingSigner:
    tag: str

    def sign(self, req: PreparedRequest) -> PreparedRequest:
        out = req.copy()
        out.headers["X-Sign"] = self.tag
        return out


SERVICE_DEFAULT = TaggingSigner("svc")
ENDPOINT_OVERRIDE = TaggingSigner("ep")


class Svc(Service):
    signer = SERVICE_DEFAULT

    @endpoint("GET", "/inherits")
    async def inherits(self) -> Out: ...

    @endpoint("GET", "/overrides", sign=ENDPOINT_OVERRIDE)
    async def overrides(self) -> Out: ...


class Plain(Service):
    @endpoint("GET", "/plain")
    async def plain(self) -> Out: ...


class Cli(MockClient):
    s: Svc = service()
    p: Plain = service()


async def test_service_default_signer_applied() -> None:
    client = Cli(responder=lambda _: {"ok": True})
    await client.s.inherits()
    assert client.sent[0].headers["X-Sign"] == "svc"


async def test_endpoint_sign_overrides_service_default() -> None:
    client = Cli(responder=lambda _: {"ok": True})
    await client.s.overrides()
    assert client.sent[0].headers["X-Sign"] == "ep"


async def test_no_signer_means_null_signer() -> None:
    client = Cli(responder=lambda _: {"ok": True})
    await client.p.plain()
    assert "X-Sign" not in client.sent[0].headers
