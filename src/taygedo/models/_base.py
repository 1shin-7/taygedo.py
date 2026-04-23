"""Common pydantic configuration shared by every model in this package.

Two model bases are exported:

* ``BbsBase`` — for ``bbs-api.tajiduo.com`` payloads. Tolerant of unknown fields
  (the API frequently adds new keys).
* ``LaohuBase`` — for ``user.laohu.com`` payloads. Same policy.

Both enable ``populate_by_name`` so fields declared with ``Field(alias=...)`` are
addressable by their Pythonic name at construction time.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BbsBase(BaseModel):
    """Base for every model representing a ``bbs-api.tajiduo.com`` payload."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=False,
    )


class LaohuBase(BaseModel):
    """Base for every model representing a ``user.laohu.com`` payload."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=False,
    )
