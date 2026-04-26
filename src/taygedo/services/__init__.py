"""Business services mounted on :class:`taygedo.client.TaygedoClient`."""

from taygedo.services.auth import AuthService
from taygedo.services.community import CommunityService, SigninRequest
from taygedo.services.ht import BindRoleService, HtService
from taygedo.services.login import LoginService
from taygedo.services.nte import NteService
from taygedo.services.nte_sign import NteSignRequest, NteSignService
from taygedo.services.post import PostIdRequest, PostService
from taygedo.services.search import SearchService
from taygedo.services.user import FollowRequest, UpdateUserInfoRequest, UserService

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
    "UpdateUserInfoRequest",
    "UserService",
]
