"""BearerProvider reads token at call time and never overwrites."""

from __future__ import annotations

from dataclasses import dataclass

from tagedo.core import BearerProvider, PreparedRequest


@dataclass
class Holder:
    access_token: str = ""


def test_empty_token_does_not_inject() -> None:
    p = BearerProvider(Holder())
    req = PreparedRequest(method="GET", url="/x")
    out = p.apply(req)
    assert "Authorization" not in out.headers
    # When no mutation happens we return the same object instance.
    assert out is req


def test_non_empty_token_injects_authorization() -> None:
    h = Holder(access_token="tok-abc")
    p = BearerProvider(h)
    req = PreparedRequest(method="GET", url="/x")
    out = p.apply(req)
    assert out.headers["Authorization"] == "tok-abc"
    # Original request is left untouched (deep-copied).
    assert "Authorization" not in req.headers


def test_does_not_overwrite_existing_authorization() -> None:
    h = Holder(access_token="auto")
    p = BearerProvider(h)
    req = PreparedRequest(method="GET", url="/x", headers={"Authorization": "manual"})
    out = p.apply(req)
    assert out.headers["Authorization"] == "manual"


def test_token_is_re_read_on_each_call() -> None:
    h = Holder(access_token="t1")
    p = BearerProvider(h)
    out1 = p.apply(PreparedRequest(method="GET", url="/x"))
    h.access_token = "t2"
    out2 = p.apply(PreparedRequest(method="GET", url="/x"))
    assert out1.headers["Authorization"] == "t1"
    assert out2.headers["Authorization"] == "t2"
