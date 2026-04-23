"""Service layer — business modules mounted on a Client.

A ``Service`` is a namespace of related endpoints (e.g. ``UserService`` groups
all ``/api/user/*`` calls). Services are mounted on a Client via the
``service()`` descriptor::

    class TajiduoClient(BaseClient):
        user: UserService = service()
        post: PostService = service()

    client = TajiduoClient(base_url="...")
    await client.user.get_user_info(uid=1)   # ← LSP sees this method natively

The descriptor lazily instantiates each Service on first access and caches it
on the Client instance.

Service-level configuration
---------------------------

Subclasses tune the engine via class attributes:

* ``signer``        — fallback Signer for endpoints that don't override.
* ``default_headers`` — static identity headers (``Origin`` / ``Referer`` /
  ``User-Agent`` overrides) merged into every endpoint before user params.
* ``base_url``      — service-specific origin (e.g. ``user.laohu.com``)
  overriding the Client's default.
* ``auth_required`` — opt into the Client's :class:`AuthProvider` injection.
* ``on_unauthorized`` — coroutine called when an endpoint sees HTTP 401.
  Returning ``True`` triggers a single retry. ``BearerAuthService`` delegates
  to ``client.auth.on_unauthorized`` so the refresh logic lives in one place.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, cast, overload

if TYPE_CHECKING:
    from .client import BaseClient
    from .signing import Signer


__all__ = ["BearerAuthService", "Service", "ServiceDescriptor", "service"]


class Service:
    """Base class for all business modules."""

    signer: ClassVar[Signer | type[Signer] | Any] = None
    """Fallback Signer applied to every endpoint that doesn't override.

    May be a Signer instance, a zero-arg Signer class, ``None``, or a callable
    ``(service_instance) -> Signer`` factory (resolved per-call).
    """

    default_headers: ClassVar[dict[str, str]] = {}
    """Static headers merged into every endpoint request as the base layer."""

    base_url: ClassVar[str] = ""
    """Service-specific base URL; empty falls back to ``client.base_url``."""

    auth_required: ClassVar[bool] = False
    """If True, the Client's AuthProvider injects auth headers automatically."""

    def __init__(self, client: BaseClient) -> None:
        self.client = client

    async def on_unauthorized(self) -> bool:
        """Hook invoked when an endpoint receives HTTP 401.

        Return ``True`` to indicate that recovery succeeded (e.g. tokens were
        refreshed) and the endpoint should retry once. Default: ``False``.
        """
        return False


class BearerAuthService(Service):
    """Mixin for services that want client-managed Authorization + auto-refresh.

    The actual refresh logic lives on ``client.auth`` (an ``AuthService``); this
    base class merely wires the 401 hook through.
    """

    auth_required: ClassVar[bool] = True

    async def on_unauthorized(self) -> bool:
        auth = getattr(self.client, "auth", None)
        if auth is None:
            return False
        return cast("bool", await auth.on_unauthorized())


class ServiceDescriptor[ServiceT: Service]:
    """Lazy, per-instance Service mount."""

    __slots__ = ("_attr_name", "_service_cls")

    def __init__(self) -> None:
        self._attr_name: str = ""
        self._service_cls: type[ServiceT] | None = None

    def __set_name__(self, owner: type[BaseClient], name: str) -> None:
        self._attr_name = name
        ann = owner.__annotations__.get(name)
        if ann is None:
            raise TypeError(
                f"{owner.__name__}.{name} must be annotated with its Service class",
            )
        if isinstance(ann, str):
            self._service_cls = None
        else:
            self._service_cls = cast("type[ServiceT]", ann)

    @overload
    def __get__(self, instance: None, owner: type[BaseClient]) -> ServiceDescriptor[ServiceT]: ...
    @overload
    def __get__(self, instance: BaseClient, owner: type[BaseClient]) -> ServiceT: ...
    def __get__(
        self,
        instance: BaseClient | None,
        owner: type[BaseClient],
    ) -> ServiceDescriptor[ServiceT] | ServiceT:
        if instance is None:
            return self
        cached = instance.__dict__.get(self._attr_name)
        if cached is not None:
            return cast("ServiceT", cached)
        cls = self._resolve(owner)
        svc = cls(instance)
        instance.__dict__[self._attr_name] = svc
        return svc

    def _resolve(self, owner: type[BaseClient]) -> type[ServiceT]:
        if self._service_cls is not None:
            return self._service_cls
        from typing import get_type_hints

        hints = get_type_hints(owner)
        ann = hints.get(self._attr_name)
        if ann is None or not isinstance(ann, type):
            raise TypeError(
                f"Cannot resolve Service class for {owner.__name__}.{self._attr_name}",
            )
        self._service_cls = cast("type[ServiceT]", ann)
        return self._service_cls


def service() -> Any:
    """Declare a lazy Service mount on a Client.

    The return type is ``Any`` so the variable annotation drives static type
    inference: ``user: UserService = service()`` makes mypy treat ``client.user``
    as ``UserService``.
    """
    return ServiceDescriptor()
