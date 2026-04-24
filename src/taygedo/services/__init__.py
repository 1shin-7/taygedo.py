"""Business services mounted on :class:`taygedo.client.TaygedoClient`."""

from .auth import AuthService
from .community import CommunityService, SigninRequest
from .ht import BindRoleService, HtService
from .login import LoginService
from .nte import NteService
from .nte_sign import NteSignRequest, NteSignService
from .post import PostIdRequest, PostService
from .search import SearchService
from .user import FollowRequest, UserService

__all__ = [
    "AuthService",
    "BindRoleService",
    "CommunityService",
    "FollowRequest",
    "HtService",
    "LoginService",
    "NteService",
    "NteSignRequest",
    "NteSignService",
    "PostIdRequest",
    "PostService",
    "SearchService",
    "SigninRequest",
    "UserService",
]
