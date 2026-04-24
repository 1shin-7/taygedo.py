"""Pydantic bases for the two upstream APIs.

``extra="allow"`` because both APIs add fields without notice;
``populate_by_name=True`` so ``Field(alias=...)`` fields accept Pythonic names.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BbsBase(BaseModel):
    """Base for ``bbs-api.tajiduo.com`` payloads."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=False,
    )


class LaohuBase(BaseModel):
    """Base for ``user.laohu.com`` payloads."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=False,
    )
