"""Shared test fixtures: a transport-mocking BaseClient subclass."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from tagedo.core import BaseClient, PreparedRequest, Response


class MockClient(BaseClient):
    """Records every PreparedRequest and returns scripted responses."""

    def __init__(
        self,
        responder: Callable[[PreparedRequest], Response | dict[str, Any]] | None = None,
        *,
        base_url: str = "https://example.test",
    ) -> None:
        super().__init__(base_url=base_url)
        self.sent: list[PreparedRequest] = []
        self._responder = responder or (lambda _req: {})

    async def __aenter__(self) -> MockClient:  # type: ignore[override]
        return self

    async def __aexit__(self, *exc: object) -> None:
        return None

    async def send(self, prepared: PreparedRequest) -> Response:
        self.sent.append(prepared)
        result = self._responder(prepared)
        if isinstance(result, Response):
            return result
        return Response(
            status_code=200,
            headers={"content-type": "application/json"},
            content=json.dumps(result).encode("utf-8"),
        )
