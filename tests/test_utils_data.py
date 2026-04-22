from __future__ import annotations

import asyncio
from typing import Any

import pytest
from pydantic import BaseModel

from tagedo.utils.data import parse_with_model


class UserModel(BaseModel):
    id: int
    name: str


def test_sync_dict_returns_model_when_valid() -> None:
    @parse_with_model(UserModel)
    def fetch_user() -> dict[str, Any]:
        return {"id": 1, "name": "alice"}

    result = fetch_user()
    assert isinstance(result, UserModel)
    assert result.id == 1
    assert result.name == "alice"


def test_sync_dict_returns_original_dict_when_invalid() -> None:
    @parse_with_model(UserModel)
    def fetch_user() -> dict[str, Any]:
        return {"id": "not-an-int", "name": "alice"}

    result = fetch_user()
    assert isinstance(result, dict)
    assert result == {"id": "not-an-int", "name": "alice"}


def test_sync_non_dict_payload_raises_type_error() -> None:
    @parse_with_model(UserModel)
    def fetch_user() -> Any:
        return 123

    with pytest.raises(TypeError, match="must return a dict payload"):
        fetch_user()


def test_sync_function_returning_coroutine_raises_type_error() -> None:
    async def inner() -> dict[str, Any]:
        return {"id": 1, "name": "alice"}

    @parse_with_model(UserModel)
    def fetch_user() -> Any:
        return inner()

    with pytest.raises(TypeError, match="returned a coroutine in sync mode"):
        fetch_user()


def test_async_dict_returns_model_when_valid() -> None:
    @parse_with_model(UserModel)
    async def fetch_user() -> dict[str, Any]:
        return {"id": 2, "name": "bob"}

    result = asyncio.run(fetch_user())
    assert isinstance(result, UserModel)
    assert result.id == 2
    assert result.name == "bob"


def test_async_dict_returns_original_dict_when_invalid() -> None:
    @parse_with_model(UserModel)
    async def fetch_user() -> dict[str, Any]:
        return {"id": "bad-id", "name": "bob"}

    result = asyncio.run(fetch_user())
    assert isinstance(result, dict)
    assert result == {"id": "bad-id", "name": "bob"}


def test_async_non_dict_payload_raises_type_error() -> None:
    @parse_with_model(UserModel)
    async def fetch_user() -> Any:
        return 123

    with pytest.raises(TypeError, match="must return a dict payload"):
        asyncio.run(fetch_user())
