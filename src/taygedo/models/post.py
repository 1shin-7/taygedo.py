"""Post / Reply / Comment models — the dominant payload shape across the BBS endpoints."""

from __future__ import annotations

from typing import Any

import orjson
from pydantic import Field, field_validator

from taygedo.models._base import BbsBase
from taygedo.models.common import Image, Vod
from taygedo.models.user import User

__all__ = [
    "AddCommentRequest",
    "Comment",
    "CommentPage",
    "CommentStat",
    "CommentSubmitResult",
    "CreatePostRequest",
    "CreatePostResult",
    "FollowRel",
    "Post",
    "PostCover",
    "PostFull",
    "PostStat",
    "PostType",
    "Reply",
    "SelfOperation",
]


class PostType:
    """Mnemonic constants for ``Post.type`` (kept as plain ints — server may add)."""

    TEXT_OR_IMAGE = 1
    VIDEO = 3


class PostStat(BbsBase):
    """Engagement counters on a post."""

    post_id: int = Field(alias="postId")
    like_num: int = Field(alias="likeNum", default=0)
    comment_num: int = Field(alias="commentNum", default=0)
    collect_num: int = Field(alias="collectNum", default=0)


class SelfOperation(BbsBase):
    """The current user's own state with respect to this post."""

    liked: bool = False


class PostCover(BbsBase):
    """Decoded ``Post.cover`` (which arrives as a JSON-encoded string)."""

    url: str
    crop_rect: dict[str, int] = Field(alias="cropRect", default_factory=dict)


class Post(BbsBase):
    """Full post object — covers text, image, and video posts."""

    post_id: int = Field(alias="postId")
    uid: int
    community_id: int = Field(alias="communityId")
    column_id: int = Field(alias="columnId")
    subject: str
    content: str
    type: int
    """See :class:`PostType` for known values."""

    structured_content: str = Field(alias="structuredContent", default="")
    """Rich-text representation as a JSON-encoded string. Decode lazily — the
    schema is ``[{"txt": "..."} | {"image": "...", "attributes": {...}} | ...]``.
    """

    images: list[Image] = Field(default_factory=list)
    vods: list[Vod] = Field(default_factory=list)
    cover: PostCover | None = None
    """Present on video posts. Stored as a JSON string in the wire format;
    :meth:`_decode_cover` parses it transparently."""

    topic_ids: list[int] = Field(alias="topicIds", default_factory=list)
    mentions: list[Any] = Field(default_factory=list)

    post_stat: PostStat = Field(alias="postStat")
    self_operation: SelfOperation = Field(
        alias="selfOperation", default_factory=SelfOperation,
    )

    region: str = ""
    create_time: int = Field(alias="createTime", default=0)
    send_time: int = Field(alias="sendTime", default=0)
    update_time: int = Field(alias="updateTime", default=0)
    last_edit_time: int = Field(alias="lastEditTime", default=0)
    delete_time: int = Field(alias="deleteTime", default=0)
    draft_id: int = Field(alias="draftId", default=0)
    schedule_time: int = Field(alias="scheduleTime", default=0)

    is_delete: bool = Field(alias="isDelete", default=False)
    showing_missing: bool = Field(alias="showingMissing", default=False)
    prime: bool = False
    user_stick: bool = Field(alias="userStick", default=False)
    column_top: bool = Field(alias="columnTop", default=False)
    version: int = 0

    @field_validator("cover", mode="before")
    @classmethod
    def _decode_cover(cls, v: object) -> object:
        """Cover arrives as ``"{...}"`` (JSON string) — parse it transparently."""
        if isinstance(v, str) and v:
            try:
                return orjson.loads(v)
            except orjson.JSONDecodeError:
                return None
        return v

    def parsed_structured_content(self) -> list[dict[str, Any]]:
        """Decode ``structured_content`` on demand. Returns empty list on failure."""
        if not self.structured_content:
            return []
        try:
            decoded = orjson.loads(self.structured_content)
        except orjson.JSONDecodeError:
            return []
        if isinstance(decoded, list):
            return [d for d in decoded if isinstance(d, dict)]
        return []


class Reply(BbsBase):
    """Reply feed item.

    Schema unverified (HAR sample was empty); fields are intentionally permissive.
    Subclass / extend once a populated sample becomes available.
    """

    post_id: int | None = Field(alias="postId", default=None)
    reply_id: int | None = Field(alias="replyId", default=None)
    uid: int | None = None
    content: str = ""
    create_time: int = Field(alias="createTime", default=0)


# ---------- comments (on posts) ---------------------------------------------


class CommentStat(BbsBase):
    """Engagement counters on a comment."""

    comment_id: int = Field(alias="commentId")
    post_id: int = Field(alias="postId")
    like_num: int = Field(alias="likeNum", default=0)
    reply_num: int = Field(alias="replyNum", default=0)
    create_time: int = Field(alias="createTime", default=0)
    update_time: int = Field(alias="updateTime", default=0)


class Comment(BbsBase):
    """A single comment (or reply) on a post."""

    id: int
    post_id: int = Field(alias="postId")
    uid: int
    parent_id: int = Field(alias="parentId", default=0)
    reply_uid: int = Field(alias="replyUid", default=0)
    content: str = ""
    structured_content: str = Field(alias="structuredContent", default="")
    images: list[Image] = Field(default_factory=list)
    mentions: list[Any] = Field(default_factory=list)
    create_time: int = Field(alias="createTime", default=0)
    update_time: int = Field(alias="updateTime", default=0)
    is_delete: bool = Field(alias="isDelete", default=False)
    showing_missing: bool = Field(alias="showingMissing", default=False)
    comment_stat: CommentStat | None = Field(alias="commentStat", default=None)
    self_operation: SelfOperation = Field(
        alias="selfOperation", default_factory=SelfOperation,
    )


class CommentPage(BbsBase):
    """``GET /bbs/api/getComments`` payload."""

    comments: list[Comment] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)
    has_more: bool = Field(alias="hasMore", default=False)
    page: int = 0
    version: int = 0


# ---------- follow relation -------------------------------------------------


class FollowRel(BbsBase):
    """Follow-relation block embedded in ``PostFull.fr`` or ``User.fr``."""

    fid: int = 0
    followed: bool = False
    following: bool = False
    time: int = 0


# ---------- PostFull (GET /bbs/api/getPostFull) -----------------------------


class PostFull(BbsBase):
    """``GET /bbs/api/getPostFull`` payload — a Post plus adjacent metadata."""

    post: Post
    users: list[User] = Field(default_factory=list)
    topics: list[Any] = Field(default_factory=list)
    hot: bool = False
    fr: FollowRel | None = None
    draft_id: int = Field(alias="draftId", default=0)


# ---------- comment submission ---------------------------------------------


class AddCommentRequest(BbsBase):
    """``POST /bbs/api/comment`` JSON body."""

    post_id: int = Field(alias="postId")
    content: str
    parent_id: int = Field(alias="parentId", default=0)
    reply_uid: int = Field(alias="replyUid", default=0)
    structured_content: str = Field(alias="structuredContent", default="")
    mentions: list[Any] = Field(default_factory=list)
    images: list[Image] = Field(default_factory=list)


class CommentSubmitResult(BbsBase):
    """``POST /bbs/api/comment`` response data."""

    comment: Comment
    users: list[User] = Field(default_factory=list)


# ---------- post creation --------------------------------------------------


class CreatePostRequest(BbsBase):
    """``POST /bbs/api/post`` JSON body.

    ``content`` is a Quill-generated HTML string with embedded image / divider /
    mention nodes. ``type`` follows :class:`PostType` (1 = text/image, 3 = video).
    ``topic_ids`` may be empty.
    """

    type: int = PostType.TEXT_OR_IMAGE
    community_id: int = Field(alias="communityId")
    column_id: int = Field(alias="columnId")
    subject: str
    content: str
    topic_ids: list[int] = Field(alias="topicIds", default_factory=list)


class CreatePostResult(BbsBase):
    """``POST /bbs/api/post`` response data — only the new ``post_id``."""

    post_id: int = Field(alias="postId")
