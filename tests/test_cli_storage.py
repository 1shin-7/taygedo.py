"""Storage round-trips, atomic write, accounts CRUD, dotted config."""

from __future__ import annotations

import os
from pathlib import Path

from taygedo.cli._storage import Storage, StoredAccount


def _storage(tmp_path: Path) -> Storage:
    return Storage(config_dir=tmp_path)


def _make_account(uid: int, **overrides: object) -> StoredAccount:
    base = {
        "uid": uid,
        "nickname": f"user-{uid}",
        "cellphone_masked": "138****8000",
        "access_token": "at",
        "refresh_token": "rt",
        "laohu_token": "lt",
        "laohu_user_id": 999,
        "device_id": "dev",
    }
    base.update(overrides)
    return StoredAccount(**base)  # type: ignore[arg-type]


def test_load_data_returns_empty_default_when_missing(tmp_path: Path) -> None:
    s = _storage(tmp_path)
    data = s.load_data()
    assert data == {"active_uid": None, "accounts": {}}
    # Pure read should NOT create the file.
    assert not (tmp_path / "data.json").exists()


def test_upsert_save_load_roundtrip(tmp_path: Path) -> None:
    s = _storage(tmp_path)
    a = _make_account(uid=42, nickname="zhang")
    s.upsert_account(a, set_active=True)

    s2 = Storage(config_dir=tmp_path)
    accounts = s2.list_accounts()
    assert len(accounts) == 1
    assert accounts[0].uid == 42
    assert accounts[0].nickname == "zhang"
    assert s2.active_uid() == 42


def test_data_file_mode_is_0600(tmp_path: Path) -> None:
    s = _storage(tmp_path)
    s.upsert_account(_make_account(uid=1), set_active=True)
    mode = os.stat(tmp_path / "data.json").st_mode & 0o777
    assert mode == 0o600


def test_remove_account_falls_back_to_remaining_active(tmp_path: Path) -> None:
    s = _storage(tmp_path)
    s.upsert_account(_make_account(uid=1), set_active=True)
    s.upsert_account(_make_account(uid=2), set_active=False)
    s.remove_account(1)
    assert s.active_uid() == 2


def test_remove_account_no_remaining_resets_active(tmp_path: Path) -> None:
    s = _storage(tmp_path)
    s.upsert_account(_make_account(uid=1), set_active=True)
    s.remove_account(1)
    assert s.active_uid() is None


def test_clear_accounts(tmp_path: Path) -> None:
    s = _storage(tmp_path)
    s.upsert_account(_make_account(uid=1), set_active=True)
    s.upsert_account(_make_account(uid=2), set_active=False)
    s.clear_accounts()
    assert s.list_accounts() == []
    assert s.active_uid() is None


def test_set_active_unknown_uid_raises(tmp_path: Path) -> None:
    import pytest

    s = _storage(tmp_path)
    with pytest.raises(KeyError):
        s.set_active(999)


def test_config_get_default_when_unset(tmp_path: Path) -> None:
    s = _storage(tmp_path)
    assert s.get_config("missing.path", default="fallback") == "fallback"
    # Touching load_config writes the default skeleton — that's fine.


def test_config_set_creates_intermediate_tables(tmp_path: Path) -> None:
    s = _storage(tmp_path)
    s.set_config("output.format", "json")
    assert s.get_config("output.format") == "json"

    s2 = Storage(config_dir=tmp_path)
    assert s2.get_config("output.format") == "json"


def test_config_default_skeleton_has_output_format_table(tmp_path: Path) -> None:
    s = _storage(tmp_path)
    s.load_config()
    assert s.get_config("output.format") == "table"


def test_stored_account_from_dict_ignores_unknown_keys(tmp_path: Path) -> None:
    a = StoredAccount.from_dict(
        {
            "uid": 1,
            "nickname": "x",
            "future_field_we_dont_know": "ignored",
        },
    )
    assert a.uid == 1
