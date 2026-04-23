"""Business services mounted on :class:`tagedo.client.TajiduoClient`."""

from .auth import AuthService
from .community import CommunityService
from .ht import BindRoleService, HtService
from .login import LoginService
from .nte import NteService
from .nte_sign import NteSignRequest, NteSignService
from .user import UserService

__all__ = [
    "AuthService",
    "BindRoleService",
    "CommunityService",
    "HtService",
    "LoginService",
    "NteService",
    "NteSignRequest",
    "NteSignService",
    "UserService",
]
