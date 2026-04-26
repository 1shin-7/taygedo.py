"""Post viewing, comments, engagement, creation — composed service."""

from taygedo.services.post._actions import PostIdRequest, _Actions
from taygedo.services.post._create import _Create
from taygedo.services.post._read import _Read

__all__ = ["PostIdRequest", "PostService"]


class PostService(_Read, _Actions, _Create):
    """All post-related endpoints reachable from one client mount."""
