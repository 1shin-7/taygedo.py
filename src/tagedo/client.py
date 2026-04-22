"""User-facing client — composes BaseClient with all business Services.

Service mounts are declared as class-level annotations::

    user: UserService = service()
    posts: PostsService = service()

mypy / IDE see them as instances of the declared Service class; the descriptor
lazily instantiates each on first access.
"""

from __future__ import annotations

from .core import BaseClient

__all__ = ["TajiduoClient"]


class TajiduoClient(BaseClient):
    """Concrete client for ``bbs-api.tajiduo.com``.

    Service mounts will be added as new ``services/*.py`` modules land.
    """

    def __init__(
        self,
        *,
        base_url: str = "https://bbs-api.tajiduo.com",
        impersonate: str = "chrome",
        timeout: float = 30.0,
    ) -> None:
        super().__init__(base_url=base_url, impersonate=impersonate, timeout=timeout)
