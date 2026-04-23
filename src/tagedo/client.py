"""User-facing client — composes BaseClient with all business Services.

Single-account model: one ``TajiduoClient`` instance owns one ``SessionState``
(the bbs/laohu tokens for one user). Token persistence is the caller's
responsibility — restore by mutating ``client.session`` directly, or by
running the LoginService → AuthService flow on each fresh process.

Service mounts are declared as class-level annotations; the descriptor lazily
instantiates each Service on first access. mypy / IDE see them as instances
of the declared Service class so ``client.nte.get_role_home(...)`` is fully
typed.
"""

from __future__ import annotations

from dataclasses import dataclass

from .core import BaseClient, BearerProvider, service
from .device import AndroidDeviceProfile, DeviceProfile
from .services import (
    AuthService,
    BindRoleService,
    CommunityService,
    HtService,
    LoginService,
    NteService,
    NteSignService,
    UserService,
)

__all__ = ["SessionState", "TajiduoClient"]


@dataclass(slots=True)
class SessionState:
    """Mutable holder of every credential the client cares about.

    All fields default to empty so a freshly-constructed client is in the
    "logged out" state. The Auth/Login services mutate this in place so
    every Service that reads from it sees the latest values without any
    explicit propagation.
    """

    access_token: str = ""
    refresh_token: str = ""
    uid: int = 0
    laohu_token: str = ""
    laohu_user_id: int = 0


class TajiduoClient(BaseClient):
    """Concrete client for ``bbs-api.tajiduo.com`` + ``user.laohu.com``."""

    login: LoginService = service()
    auth: AuthService = service()
    user: UserService = service()
    community: CommunityService = service()
    bind_role: BindRoleService = service()
    ht: HtService = service()
    nte: NteService = service()
    nte_sign: NteSignService = service()

    def __init__(
        self,
        *,
        device: DeviceProfile | None = None,
        bbs_base_url: str = "https://bbs-api.tajiduo.com",
        impersonate: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.device: DeviceProfile = device or AndroidDeviceProfile.for_htassistant()
        self.session_state = SessionState()
        super().__init__(
            base_url=bbs_base_url,
            impersonate=impersonate,
            timeout=timeout,
            auth_provider=BearerProvider(self.session_state),
        )
