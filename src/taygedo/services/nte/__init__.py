"""异环 (NTE, gameId=1289) game-data queries — composed service.

All endpoints under ``/apihub/awapi/yh/`` (and one ``/bbs/awapi/recommendPosts``)
are server-side authenticated by Bearer alone — there is no DS or per-request
sign, and ``roleId`` is freely queryable. The static identity headers below
mirror what the in-app WebView sends.
"""

from __future__ import annotations

from typing import ClassVar

from taygedo.services.nte._assets import _Assets
from taygedo.services.nte._meta import _Meta
from taygedo.services.nte._role import _Role
from taygedo.signers import SignDs

__all__ = ["NteService"]


class NteService(_Role, _Assets, _Meta):
    signer: ClassVar[SignDs] = SignDs()

    default_headers: ClassVar[dict[str, str]] = {
        "Origin": "https://webstatic.tajiduo.com",
        "Referer": "https://webstatic.tajiduo.com/",
        "X-Requested-With": "com.pwrd.htassistant",
    }
