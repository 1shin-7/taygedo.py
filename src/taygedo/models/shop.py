"""Shop / goods list models — ``/apihub/api/shop/*``."""

from __future__ import annotations

from pydantic import Field

from ._base import BbsBase

__all__ = ["Good", "GoodsPage"]


class Good(BbsBase):
    """One merchandise entry in ``/apihub/api/shop/listGoods.goods``."""

    id: int
    name: str
    cover: str = ""
    icon: str = ""
    price: int = 0
    sale: float = 0.0
    sale_start_time: int = Field(alias="saleStartTime", default=0)
    sale_end_time: int = Field(alias="saleEndTime", default=0)
    state: int = 0
    stock: int = 0
    next_stock: int = Field(alias="nextStock", default=0)
    next_time: int = Field(alias="nextTime", default=0)
    limit: int = 0
    exchange_num: int = Field(alias="exchangeNum", default=0)
    cycle_limit: int = Field(alias="cycleLimit", default=0)
    cycle_type: int = Field(alias="cycleType", default=0)
    end_time: int = Field(alias="endTime", default=0)
    game_id: int = Field(alias="gameId", default=0)
    point_type: int = Field(alias="pointType", default=0)
    tab: str = ""


class GoodsPage(BbsBase):
    """``GET /apihub/api/shop/listGoods`` payload."""

    goods: list[Good] = Field(default_factory=list)
    has_more: bool = Field(alias="hasMore", default=False)
    page: int = 0
    version: int = 0
