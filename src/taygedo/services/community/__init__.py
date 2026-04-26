"""BBS community service — composed of vertical-slice mixins.

Each ``_*`` module owns one domain (bootstrap, feeds, signin, tasks, shop).
``CommunityService`` glues them via MRO so the public API stays single-class.
"""

from taygedo.services.community._bootstrap import _Bootstrap
from taygedo.services.community._feeds import _Feeds
from taygedo.services.community._shop import _Shop
from taygedo.services.community._signin import SigninRequest, _Signin
from taygedo.services.community._tasks import _Tasks

__all__ = ["CommunityService", "SigninRequest"]


class CommunityService(_Bootstrap, _Feeds, _Signin, _Tasks, _Shop):
    """All BBS community endpoints reachable from one client mount."""
