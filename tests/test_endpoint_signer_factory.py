"""sign= callable factory is invoked with the service instance."""

from __future__ import annotations

from dataclasses import dataclass

from taygedo.core import PreparedRequest, Service, endpoint

from ._helpers import MockClient


@dataclass
class TaggingSigner:
    tag: str

    def sign(self, req: PreparedRequest) -> PreparedRequest:
        out = req.copy()
        out.headers["X-Signed-By"] = self.tag
        return out


def _factory(svc: Service) -> TaggingSigner:
    return TaggingSigner(tag=svc.__class__.__name__)


class FactSigned(Service):
    @endpoint.get("/x", sign=_factory)
    async def call(self) -> dict[str, object]: ...


async def test_factory_called_with_service_instance() -> None:
    client = MockClient()
    svc = FactSigned(client)
    await svc.call()
    assert client.sent[0].headers["X-Signed-By"] == "FactSigned"


async def test_factory_runs_per_call_not_once() -> None:
    counter = {"n": 0}

    def f(_svc: Service) -> TaggingSigner:
        counter["n"] += 1
        return TaggingSigner(tag=str(counter["n"]))

    class Per(Service):
        @endpoint.get("/y", sign=f)
        async def go(self) -> dict[str, object]: ...

    client = MockClient()
    svc = Per(client)
    await svc.go()
    await svc.go()
    assert client.sent[0].headers["X-Signed-By"] == "1"
    assert client.sent[1].headers["X-Signed-By"] == "2"
