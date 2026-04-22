"""Transport layer — HTTP primitive on top of curl_cffi.

``BaseClient`` is intentionally minimal: it owns the ``AsyncSession`` lifecycle
and exposes a single ``send`` coroutine that takes a framework-internal
``PreparedRequest`` and returns a framework-internal ``Response``.

The endpoint engine talks to ``BaseClient.send`` only — it does not import
curl_cffi. This keeps the upper layers transport-agnostic and unit-testable
(see ``tests/test_baseclient_lifecycle.py``).
"""

from __future__ import annotations

from dataclasses import dataclass
from types import TracebackType
from typing import Any, Self

from curl_cffi.requests import AsyncSession

from .signing import PreparedRequest

__all__ = ["BaseClient", "Response"]


@dataclass(slots=True)
class Response:
    """Transport-agnostic response value object."""

    status_code: int
    headers: dict[str, str]
    content: bytes

    def json(self) -> Any:
        import json

        return json.loads(self.content.decode("utf-8"))

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


class BaseClient:
    """Owns the HTTP session and exposes the ``send`` primitive."""

    def __init__(
        self,
        *,
        base_url: str,
        impersonate: str = "chrome",
        timeout: float = 30.0,
        session: AsyncSession | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._impersonate = impersonate
        self._timeout = timeout
        self._session = session
        self._owns_session = session is None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError(
                "Session not initialised. Use 'async with client:' or pass session=...",
            )
        return self._session

    async def __aenter__(self) -> Self:
        if self._session is None:
            self._session = AsyncSession(
                impersonate=self._impersonate,  # type: ignore[arg-type]
                timeout=self._timeout,
            )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def send(self, prepared: PreparedRequest) -> Response:
        """Dispatch a PreparedRequest and return a transport-agnostic Response.

        Subclasses or tests may override this to inject mocks without touching
        the network.
        """
        url = prepared.url if prepared.url.startswith("http") else f"{self.base_url}{prepared.url}"
        kwargs: dict[str, Any] = {
            "headers": prepared.headers or None,
            "params": prepared.params or None,
        }
        if prepared.json_body is not None:
            kwargs["json"] = prepared.json_body
        elif prepared.data is not None:
            kwargs["data"] = prepared.data

        raw = await self.session.request(prepared.method, url, **kwargs)  # type: ignore[arg-type]
        return Response(
            status_code=raw.status_code,
            headers={k: v for k, v in raw.headers.items() if v is not None},
            content=raw.content,
        )
