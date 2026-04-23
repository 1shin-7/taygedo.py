"""Shared test fixtures: a transport-mocking BaseClient subclass."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from taygedo.core import (
    AuthProvider,
    BaseClient,
    PreparedRequest,
    Response,
    Service,
)


class MockClient(BaseClient):
    """Records every PreparedRequest and returns scripted responses.

    Honours the AuthProvider/auth_required protocol so tests can exercise the
    real production codepath without hitting the network.
    """

    def __init__(
        self,
        responder: Callable[[PreparedRequest], Response | dict[str, Any]] | None = None,
        *,
        base_url: str = "https://example.test",
        auth_provider: AuthProvider | None = None,
    ) -> None:
        super().__init__(base_url=base_url, auth_provider=auth_provider)
        self.sent: list[PreparedRequest] = []
        self._responder = responder or (lambda _req: {})

    async def __aenter__(self) -> MockClient:  # type: ignore[override]
        return self

    async def __aexit__(self, *exc: object) -> None:
        return None

    async def send(  # type: ignore[override]
        self,
        prepared: PreparedRequest,
        *,
        service: Service | None = None,
    ) -> Response:
        if (
            service is not None
            and getattr(type(service), "auth_required", False)
            and self._auth_provider is not None
        ):
            prepared = self._auth_provider.apply(prepared)
        self.sent.append(prepared)
        result = self._responder(prepared)
        if isinstance(result, Response):
            return result
        return Response(
            status_code=200,
            headers={"content-type": "application/json"},
            content=json.dumps(result).encode("utf-8"),
        )
