"""Tower of Fantasy game-record + bound-role lookup."""

from __future__ import annotations

from typing import ClassVar

from taygedo.services.ht._bind import BindRoleService
from taygedo.services.ht._meta import _Meta
from taygedo.services.ht._record import _Record
from taygedo.signers import SignDs

__all__ = ["BindRoleService", "HtService"]


class HtService(_Record, _Meta):
    signer: ClassVar[SignDs] = SignDs()

    default_headers: ClassVar[dict[str, str]] = {
        "Origin": "https://webstatic.tajiduo.com",
        "Referer": "https://webstatic.tajiduo.com/",
        "X-Requested-With": "com.pwrd.htassistant",
    }
