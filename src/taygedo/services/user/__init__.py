"""User profile, feeds, follow, profile-update — composed service."""

from taygedo.services.user._exp import _Exp
from taygedo.services.user._feeds import _Feeds
from taygedo.services.user._profile import UpdateUserInfoRequest, _Profile
from taygedo.services.user._social import FollowRequest, _Social

__all__ = ["FollowRequest", "UpdateUserInfoRequest", "UserService"]


class UserService(_Profile, _Feeds, _Social, _Exp):
    """All user-centric endpoints reachable from one client mount."""
