"""service.default_headers is merged in; per-call Header overrides win."""

from __future__ import annotations

from typing import Annotated, ClassVar

from tagedo.core import Header, Service, endpoint

from ._helpers import MockClient


class WithDefaults(Service):
    default_headers: ClassVar[dict[str, str]] = {
        "X-Origin": "default",
        "X-Carry": "carried",
    }

    @endpoint.get("/hello")
    async def hello(self) -> dict[str, object]: ...

    @endpoint.get("/with-override")
    async def with_override(
        self,
        x_origin: Annotated[str, Header(alias="X-Origin")] = "user",
    ) -> dict[str, object]: ...


async def test_default_headers_are_attached_when_no_override() -> None:
    client = MockClient()
    svc = WithDefaults(client)
    await svc.hello()
    sent = client.sent[0]
    assert sent.headers["X-Origin"] == "default"
    assert sent.headers["X-Carry"] == "carried"


async def test_endpoint_param_header_overrides_service_default() -> None:
    client = MockClient()
    svc = WithDefaults(client)
    await svc.with_override(x_origin="user-supplied")
    sent = client.sent[0]
    assert sent.headers["X-Origin"] == "user-supplied"
    assert sent.headers["X-Carry"] == "carried"


async def test_no_default_headers_means_clean_headers() -> None:
    class NoDefaults(Service):
        @endpoint.get("/x")
        async def call(self) -> dict[str, object]: ...

    client = MockClient()
    svc = NoDefaults(client)
    await svc.call()
    assert client.sent[0].headers == {}
