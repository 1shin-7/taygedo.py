"""Service layer — business modules mounted on a Client.

A ``Service`` is a namespace of related endpoints (e.g. ``UserService`` groups
all ``/api/user/*`` calls). Services are mounted on a Client via the
``service()`` descriptor::

    class TaygedoClient(BaseClient):
        user: UserService = service()
        post: PostService = service()

    client = TaygedoClient(base_url="...")
    await client.user.get_user_info(uid=1)   # ← LSP sees this method natively

Subclasses tune the engine via class attributes:

* ``signer``            — fallback Signer for endpoints that don't override.
* ``default_headers``   — static identity headers merged before user params.
* ``base_url``          — service-specific origin (overrides Client default).
* ``auth_required``     — opt into AuthProvider injection.
* ``on_unauthorized``   — 401 hook; returning True triggers one retry.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, cast, overload

if TYPE_CHECKING:
    from taygedo.core.client import BaseClient
    from taygedo.core.signing import Signer


__all__ = ["BearerAuthService", "Service", "ServiceDescriptor", "service"]


class Service:
    """Base class for all business modules."""

    signer: ClassVar[Signer | type[Signer] | Any] = None
    """Instance, class, ``None``, or ``(service) -> Signer`` factory."""

    default_headers: ClassVar[dict[str, str]] = {}
    base_url: ClassVar[str] = ""
    auth_required: ClassVar[bool] = False

    def __init__(self, client: BaseClient) -> None:
        self.client = client

    async def on_unauthorized(self) -> bool:
        return False


class BearerAuthService(Service):
    """Services that want client-managed Authorization + auto-refresh.

    Refresh logic lives on ``client.auth``; this base wires the 401 hook through.
    """

    auth_required: ClassVar[bool] = True

    async def on_unauthorized(self) -> bool:
        auth = getattr(self.client, "auth", None)
        if auth is None:
            return False
        return cast("bool", await auth.on_unauthorized())


ServiceT = TypeVar("ServiceT", bound=Service)


class ServiceDescriptor(Generic[ServiceT]):
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
    def __get__(
        self, instance: None, owner: type[BaseClient],
    ) -> ServiceDescriptor[ServiceT]: ...
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

    Return type is ``Any`` so the variable annotation drives static inference:
    ``user: UserService = service()`` makes mypy treat ``client.user`` as ``UserService``.
    """
    return ServiceDescriptor()
