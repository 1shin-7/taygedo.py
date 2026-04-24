"""On-disk storage for the CLI: multi-account session data + TOML config.

Two files live under ``~/.config/taygedo/``:

* ``data.json`` — one record per logged-in account, keyed by uid (string).
  Holds the bbs/laohu tokens plus device_id (so the same device fingerprint
  is reused across runs) plus cached identifiers like ``ht_role_id``. Written
  with mode ``0o600`` and replaced atomically.
* ``config.toml`` — CLI preferences. Edited in place with ``tomlkit`` so
  user-added comments and key ordering are preserved.

Both files are created lazily; missing values fall back to documented defaults.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

import orjson
import tomlkit
from tomlkit.toml_document import TOMLDocument

__all__ = [
    "CONFIG_DIR",
    "CONFIG_FILE",
    "DATA_FILE",
    "Storage",
    "StoredAccount",
    "default_config_doc",
]


CONFIG_DIR = Path.home() / ".config" / "taygedo"
DATA_FILE = CONFIG_DIR / "data.json"
CONFIG_FILE = CONFIG_DIR / "config.toml"

_DEFAULT_CONFIG_TOML = """\
# taygedo CLI configuration

[output]
# table | json
format = "table"

[device]
# Override the per-account stored device_id.
# device_id = ""

[network]
# bbs_base_url = "https://bbs-api.tajiduo.com"
# timeout = 30
"""


@dataclass(slots=True)
class StoredAccount:
    """One persisted login session."""

    uid: int
    nickname: str = ""
    cellphone_masked: str = ""
    access_token: str = ""
    refresh_token: str = ""
    laohu_token: str = ""
    laohu_user_id: int = 0
    device_id: str = ""
    ht_role_id: int = 0
    logged_in_at: str = ""
    last_used_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> StoredAccount:
        # Tolerate forward-compatible additions: only consume known fields.
        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in raw.items() if k in known}
        return cls(**filtered)


def default_config_doc() -> TOMLDocument:
    return tomlkit.parse(_DEFAULT_CONFIG_TOML)


@dataclass(slots=True)
class _Cache:
    data: dict[str, Any] | None = field(default=None)
    config: TOMLDocument | None = field(default=None)


class Storage:
    """Read/write data.json + config.toml under ~/.config/taygedo/.

    A single Storage instance owns a small in-memory cache so repeated reads
    inside one CLI invocation don't hit the disk multiple times. ``save_*``
    methods invalidate the cache on the next read.
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        self._dir = config_dir or CONFIG_DIR
        self._data_file = self._dir / "data.json"
        self._config_file = self._dir / "config.toml"
        self._cache = _Cache()

    # ----- low-level r/w --------------------------------------------------

    def load_data(self) -> dict[str, Any]:
        if self._cache.data is not None:
            return self._cache.data
        if not self._data_file.exists():
            self._cache.data = {"active_uid": None, "accounts": {}}
            return self._cache.data
        with self._data_file.open("rb") as f:
            data: dict[str, Any] = orjson.loads(f.read())
        data.setdefault("active_uid", None)
        data.setdefault("accounts", {})
        self._cache.data = data
        return data

    def save_data(self, data: dict[str, Any]) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._atomic_write(
            self._data_file,
            orjson.dumps(data, option=orjson.OPT_INDENT_2),
            mode=0o600,
        )
        self._cache.data = data

    def load_config(self) -> TOMLDocument:
        if self._cache.config is not None:
            return self._cache.config
        if not self._config_file.exists():
            doc = default_config_doc()
            self.save_config(doc)
            return doc
        with self._config_file.open(encoding="utf-8") as f:
            doc = tomlkit.parse(f.read())
        self._cache.config = doc
        return doc

    def save_config(self, doc: TOMLDocument) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._atomic_write(
            self._config_file,
            tomlkit.dumps(doc).encode("utf-8"),
            mode=0o600,
        )
        self._cache.config = doc

    @staticmethod
    def _atomic_write(path: Path, payload: bytes, *, mode: int) -> None:
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=str(path.parent), prefix=path.name + ".", suffix=".tmp",
        )
        try:
            with os.fdopen(tmp_fd, "wb") as f:
                f.write(payload)
            os.chmod(tmp_path, mode)
            os.replace(tmp_path, path)
        except Exception:
            with contextlib_suppress(FileNotFoundError):
                os.unlink(tmp_path)
            raise

    # ----- account helpers ------------------------------------------------

    def list_accounts(self) -> list[StoredAccount]:
        accounts = self.load_data()["accounts"]
        return [StoredAccount.from_dict(v) for v in accounts.values()]

    def get_account(self, uid: int) -> StoredAccount | None:
        accounts = self.load_data()["accounts"]
        raw = accounts.get(str(uid))
        return StoredAccount.from_dict(raw) if raw else None

    def upsert_account(self, account: StoredAccount, *, set_active: bool = False) -> None:
        data = self.load_data()
        data["accounts"][str(account.uid)] = account.to_dict()
        if set_active:
            data["active_uid"] = account.uid
        self.save_data(data)

    def remove_account(self, uid: int) -> None:
        data = self.load_data()
        data["accounts"].pop(str(uid), None)
        if data.get("active_uid") == uid:
            # If the active account was removed, fall back to any remaining one.
            remaining = list(data["accounts"].keys())
            data["active_uid"] = int(remaining[0]) if remaining else None
        self.save_data(data)

    def clear_accounts(self) -> None:
        self.save_data({"active_uid": None, "accounts": {}})

    def active_uid(self) -> int | None:
        return self.load_data().get("active_uid")

    def set_active(self, uid: int) -> None:
        data = self.load_data()
        if str(uid) not in data["accounts"]:
            raise KeyError(f"uid {uid} is not stored")
        data["active_uid"] = uid
        self.save_data(data)

    # ----- config helpers (dotted access) ---------------------------------

    def get_config(self, dotted_key: str, default: Any = None) -> Any:
        doc = self.load_config()
        node: Any = doc
        for part in dotted_key.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def set_config(self, dotted_key: str, value: Any) -> None:
        doc = self.load_config()
        parts = dotted_key.split(".")
        node: Any = doc
        for part in parts[:-1]:
            if part not in node or not isinstance(node[part], dict):
                node[part] = tomlkit.table()
            node = node[part]
        node[parts[-1]] = value
        self.save_config(doc)


def contextlib_suppress(*excs: type[BaseException]) -> Any:
    # Tiny inline version to avoid a top-level import cost on every CLI call.
    import contextlib

    return contextlib.suppress(*excs)
