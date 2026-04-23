"""SessionState defaults + mutability."""

from __future__ import annotations

from taygedo.client import SessionState


def test_default_is_logged_out() -> None:
    s = SessionState()
    assert s.access_token == ""
    assert s.refresh_token == ""
    assert s.uid == 0
    assert s.laohu_token == ""
    assert s.laohu_user_id == 0


def test_fields_are_mutable() -> None:
    s = SessionState()
    s.access_token = "tok"
    s.uid = 42
    assert s.access_token == "tok"
    assert s.uid == 42
