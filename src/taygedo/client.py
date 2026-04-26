"""User-facing client — composes BaseClient with all business Services.

Single-account: one ``TaygedoClient`` instance owns one ``SessionState``.
Token persistence is the caller's responsibility (mutate ``client.session``
or run the LoginService → AuthService flow per process).
"""

from __future__ import annotations

from dataclasses import dataclass

from taygedo.core import BaseClient, BearerProvider, service
from taygedo.device import AndroidDeviceProfile, DeviceProfile
from taygedo.services import (
    AuthService,
    BindRoleService,
    CommunityService,
    HtService,
    LoginService,
    NteService,
    NteSignService,
    PostService,
    SearchService,
    UserService,
)

__all__ = ["SessionState", "TaygedoClient"]


@dataclass(slots=True)
class SessionState:
    """Every credential the client tracks. Mutated in place by Auth/Login services."""

    access_token: str = ""
    refresh_token: str = ""
    uid: int = 0
    laohu_token: str = ""
    laohu_user_id: int = 0


class TaygedoClient(BaseClient):
    """Concrete client for ``bbs-api.tajiduo.com`` + ``user.laohu.com``."""

    login: LoginService = service()
    auth: AuthService = service()
    user: UserService = service()
    community: CommunityService = service()
    post: PostService = service()
    search: SearchService = service()
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
