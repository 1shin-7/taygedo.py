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
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, cast, overload

if TYPE_CHECKING:
    from .client import BaseClient
    from .signing import Signer


__all__ = ["Service", "ServiceDescriptor", "service"]


class Service:
    """Base class for all business modules.

    Subclasses may set ``signer`` as a class attribute to provide a default
    signing strategy for every endpoint declared on them. The endpoint-level
    ``sign=`` argument always takes precedence.
    """

    signer: ClassVar[Signer | type[Signer] | None] = None

    def __init__(self, client: BaseClient) -> None:
        self.client = client


class ServiceDescriptor[ServiceT: Service]:
    """Lazy, per-instance Service mount.

    The descriptor stashes the Service factory and resolves the concrete class
    from the owner's annotation at first access. Each Client instance gets its
    own Service instance, cached in ``client.__dict__``.
    """

    __slots__ = ("_attr_name", "_service_cls")

    def __init__(self) -> None:
        self._attr_name: str = ""
        self._service_cls: type[ServiceT] | None = None

    def __set_name__(self, owner: type[BaseClient], name: str) -> None:
        self._attr_name = name
        # Resolve the service class from the variable annotation eagerly so
        # mistakes surface at class-definition time rather than first access.
        ann = owner.__annotations__.get(name)
        if ann is None:
            raise TypeError(
                f"{owner.__name__}.{name} must be annotated with its Service class",
            )
        if isinstance(ann, str):
            # Annotation is a forward reference — defer until first access.
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
