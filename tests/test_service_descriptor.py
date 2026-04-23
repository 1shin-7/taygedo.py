from __future__ import annotations

from pydantic import BaseModel

from taygedo.core import Service, endpoint, service

from ._helpers import MockClient


class Out(BaseModel):
    ok: bool


class A(Service):
    @endpoint("GET", "/a")
    async def go(self) -> Out: ...


class B(Service):
    @endpoint("GET", "/b")
    async def go(self) -> Out: ...


class Cli(MockClient):
    a: A = service()
    b: B = service()


def test_descriptor_lazily_instantiates_and_caches() -> None:
    client = Cli()
    first = client.a
    second = client.a
    assert first is second
    assert isinstance(first, A)


def test_each_service_gets_client_back_reference() -> None:
    client = Cli()
    assert client.a.client is client
    assert client.b.client is client


def test_distinct_services_are_independent() -> None:
    client = Cli()
    assert client.a is not client.b
