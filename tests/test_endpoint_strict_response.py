from __future__ import annotations

import orjson
import pytest
from pydantic import BaseModel

from taygedo.core import (
    ApiError,
    Response,
    ResponseValidationError,
    Service,
    endpoint,
    service,
)

from ._helpers import MockClient


class User(BaseModel):
    id: int
    name: str


class Svc(Service):
    @endpoint("GET", "/u")
    async def fetch(self) -> User: ...


class Cli(MockClient):
    s: Svc = service()


async def test_strict_returns_model_on_valid_payload() -> None:
    client = Cli(responder=lambda _: {"id": 1, "name": "alice"})
    user = await client.s.fetch()
    assert isinstance(user, User)
    assert user.id == 1


async def test_strict_raises_on_invalid_payload() -> None:
    client = Cli(responder=lambda _: {"id": "nope", "name": "alice"})
    with pytest.raises(ResponseValidationError) as info:
        await client.s.fetch()
    assert info.value.raw_data == {"id": "nope", "name": "alice"}
    assert info.value.validation_error.error_count() >= 1


async def test_4xx_raises_api_error() -> None:
    def responder(_: object) -> Response:
        return Response(
            status_code=404,
            headers={},
            content=orjson.dumps({"error": "not found"}),
        )

    client = Cli(responder=responder)
    with pytest.raises(ApiError) as info:
        await client.s.fetch()
    assert info.value.status_code == 404
    assert info.value.body == {"error": "not found"}
