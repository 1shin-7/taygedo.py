from __future__ import annotations

from typing import Annotated

import pytest
from pydantic import BaseModel

from tagedo.core import Body, Header, Path, Query, Service, endpoint, service

from ._helpers import MockClient


class Item(BaseModel):
    name: str


class Out(BaseModel):
    ok: bool


class Svc(Service):
    @endpoint("GET", "/items/{item_id}")
    async def get(
        self,
        item_id: int,
        page: int = 1,
        token: Annotated[str | None, Header("X-Token")] = None,
    ) -> Out: ...

    @endpoint("POST", "/items")
    async def create(self, body: Item) -> Out: ...

    @endpoint("PUT", "/items/{item_id}/explicit")
    async def explicit(
        self,
        item_id: Annotated[int, Path()],
        flag: Annotated[bool, Query("f")],
        body: Annotated[Item, Body()],
    ) -> Out: ...


class Cli(MockClient):
    s: Svc = service()


async def test_get_path_query_header_inference() -> None:
    client = Cli(responder=lambda _: {"ok": True})
    out = await client.s.get(item_id=42, page=3, token="abc")
    assert out == Out(ok=True)
    sent = client.sent[0]
    assert sent.method == "GET"
    assert sent.url == "/items/42"
    assert sent.params == {"page": 3}
    assert sent.headers == {"X-Token": "abc"}


async def test_post_body_inferred_from_basemodel() -> None:
    client = Cli(responder=lambda _: {"ok": True})
    await client.s.create(body=Item(name="foo"))
    sent = client.sent[0]
    assert sent.method == "POST"
    assert sent.json_body == {"name": "foo"}
    assert sent.params == {}


async def test_explicit_annotated_markers() -> None:
    client = Cli(responder=lambda _: {"ok": True})
    await client.s.explicit(item_id=7, flag=True, body=Item(name="x"))
    sent = client.sent[0]
    assert sent.url == "/items/7/explicit"
    assert sent.params == {"f": True}
    assert sent.json_body == {"name": "x"}


def test_unannotated_parameter_rejected_at_decoration() -> None:
    with pytest.raises(TypeError, match="must be annotated"):

        class Bad(Service):
            @endpoint("GET", "/x")
            async def go(self, what) -> Out: ...  # type: ignore[no-untyped-def]


def test_unmatched_path_var_rejected() -> None:
    with pytest.raises(TypeError, match="have no matching parameter"):

        class Bad(Service):
            @endpoint("GET", "/x/{missing}")
            async def go(self, present: int) -> Out: ...
