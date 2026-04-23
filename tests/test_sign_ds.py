"""Validate SignDs against HAR2 ground-truth ``ds`` headers.

The captured App 1.2.2 fires ``ds`` on every bbs-api request:
``ds = "{ts},{r},{md5(ts + r + appVersion + salt)}"``.

We can't reproduce the exact ``ds`` value (``r`` and ``ts`` are random per
call) but we can replay the algorithm against captured triples and confirm
the digest matches.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tagedo.core import PreparedRequest
from tagedo.signers import HTASSISTANT_DS_SALT, DsConfig, SignDs

HAR_PATH = (
    Path(__file__).parent.parent
    / "_dev_data"
    / "webstatic.tajiduo.com_2026_04_23_08_25_44.har"
)


def _captured_ds_triples() -> list[tuple[str, str, str]]:
    with HAR_PATH.open(encoding="utf-8") as f:
        entries = json.load(f)["log"]["entries"]
    out: list[tuple[str, str, str]] = []
    for e in entries:
        for h in e["request"]["headers"]:
            if h["name"].lower() == "ds":
                ts, r, sign = h["value"].split(",")
                out.append((ts, r, sign))
                break
    return out


@pytest.mark.parametrize("ts_r_sign", _captured_ds_triples())
def test_algorithm_matches_every_captured_ds(ts_r_sign: tuple[str, str, str]) -> None:
    ts, r, expected = ts_r_sign
    plaintext = ts + r + "1.2.2" + HTASSISTANT_DS_SALT
    assert hashlib.md5(plaintext.encode()).hexdigest() == expected


def test_sign_ds_writes_header_with_correct_shape() -> None:
    s = SignDs()
    out = s.sign(PreparedRequest(method="GET", url="/x"))
    ds = out.headers["ds"]
    ts, r, digest = ds.split(",")
    assert ts.isdigit() and len(ts) == 10
    assert len(r) == 8 and r.isalnum()
    assert len(digest) == 32 and all(c in "0123456789abcdef" for c in digest)
    # And the digest is consistent with what we just wrote.
    expected = hashlib.md5((ts + r + "1.2.2" + HTASSISTANT_DS_SALT).encode()).hexdigest()
    assert digest == expected


def test_sign_ds_does_not_touch_authorization() -> None:
    """DS is orthogonal to bearer auth — the two compose, they don't collide."""
    s = SignDs()
    req = PreparedRequest(
        method="GET", url="/x", headers={"Authorization": "preset"},
    )
    out = s.sign(req)
    assert out.headers["Authorization"] == "preset"
    assert "ds" in out.headers


def test_custom_salt_changes_digest() -> None:
    s1 = SignDs(DsConfig(salt="A" * 10))
    s2 = SignDs(DsConfig(salt="B" * 10))
    out1 = s1.sign(PreparedRequest(method="GET", url="/x"))
    out2 = s2.sign(PreparedRequest(method="GET", url="/x"))
    assert out1.headers["ds"].split(",")[2] != out2.headers["ds"].split(",")[2]
