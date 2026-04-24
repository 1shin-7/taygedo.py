"""Transport layer — HTTP primitive on top of curl_cffi.

``BaseClient`` owns the ``AsyncSession`` lifecycle and exposes a single
``send`` coroutine that takes a framework-internal ``PreparedRequest`` and
returns a framework-internal ``Response``.

Authorization injection is performed here (not in Signers) so that Services
remain ignorant of token state — see ``core.auth_provider``.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import TracebackType
from typing import TYPE_CHECKING, Any

from curl_cffi.requests import AsyncSession

from .auth_provider import AuthProvider
from .signing import PreparedRequest

if TYPE_CHECKING:
    from .service import Service

__all__ = ["BaseClient", "Response"]


@dataclass(slots=True)
class Response:
    """Transport-agnostic response value object."""

    status_code: int
    headers: dict[str, str]
    content: bytes

    def json(self) -> Any:
        import orjson

        return orjson.loads(self.content)

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


class BaseClient:
    """Owns the HTTP session and exposes the ``send`` primitive."""

    def __init__(
        self,
        *,
        base_url: str,
        impersonate: str | None = None,
        timeout: float = 30.0,
        session: AsyncSession | None = None,  # type: ignore[type-arg]
        auth_provider: AuthProvider | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._impersonate = impersonate
        self._timeout = timeout
        self._session = session
        self._owns_session = session is None
        self._auth_provider = auth_provider

    @property
    def session(self) -> AsyncSession:  # type: ignore[type-arg]
        if self._session is None:
            raise RuntimeError(
                "Session not initialised. Use 'async with client:' or pass session=...",
            )
        return self._session

    async def __aenter__(self) -> BaseClient:
        if self._session is None:
            kwargs: dict[str, Any] = {"timeout": self._timeout}
            if self._impersonate:
                kwargs["impersonate"] = self._impersonate
            self._session = AsyncSession(**kwargs)
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

    async def send(
        self,
        prepared: PreparedRequest,
        *,
        service: Service | None = None,
    ) -> Response:
        """Dispatch a PreparedRequest and return a transport-agnostic Response.

        If ``service`` is given and ``service.auth_required`` is True, the
        Client's :class:`AuthProvider` is invoked to inject auth headers
        immediately before transport.
        """
        if (
            service is not None
            and getattr(type(service), "auth_required", False)
            and self._auth_provider is not None
        ):
            prepared = self._auth_provider.apply(prepared)

        # Resolve URL: absolute > service.base_url > client.base_url
        if prepared.url.startswith("http"):
            url = prepared.url
        else:
            origin = ""
            if service is not None:
                origin = getattr(type(service), "base_url", "") or ""
            if not origin:
                origin = self.base_url
            url = f"{origin.rstrip('/')}{prepared.url}"

        kwargs: dict[str, Any] = {
            "headers": prepared.headers or None,
        }
        if prepared.form and prepared.method != "GET":
            from urllib.parse import urlencode

            if prepared.params:
                kwargs["data"] = urlencode(prepared.params)
            kwargs.setdefault("headers", {}) or kwargs["headers"]
            # Ensure Content-Type is set for form posts.
            if kwargs["headers"] is None:
                kwargs["headers"] = {}
            kwargs["headers"].setdefault(
                "Content-Type", "application/x-www-form-urlencoded",
            )
        else:
            kwargs["params"] = prepared.params or None
            if prepared.json_body is not None:
                kwargs["json"] = prepared.json_body
            elif prepared.data is not None:
                kwargs["data"] = prepared.data

        raw = await self.session.request(prepared.method, url, **kwargs)  # type: ignore[arg-type]
        response = Response(
            status_code=raw.status_code,
            headers={k: v for k, v in raw.headers.items() if v is not None},
            content=raw.content,
        )
        _debug_log(prepared, url, kwargs, response)
        return response


def _debug_log(
    prepared: PreparedRequest,
    url: str,
    kwargs: dict[str, Any],
    response: Response,
) -> None:
    """Print full request/response to stderr when ``TAGEDO_DEBUG`` is set."""
    import os
    import sys

    if not os.environ.get("TAGEDO_DEBUG"):
        return
    body_preview: object
    if "json" in kwargs:
        body_preview = kwargs["json"]
    elif "data" in kwargs:
        body_preview = kwargs["data"]
    else:
        body_preview = None
    print(
        f"--> {prepared.method} {url}\n"
        f"    headers: {prepared.headers}\n"
        f"    params : {prepared.params}\n"
        f"    body   : {body_preview!r}\n"
        f"<-- {response.status_code} ({len(response.content)} bytes)\n"
        f"    {response.text[:1500]}",
        file=sys.stderr,
        flush=True,
    )
