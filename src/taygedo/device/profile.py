"""Device profile model used by Laohu request signing.

The LaohuSDK request signature embeds a fixed set of device-identity fields
(``deviceId``, ``deviceType``, etc.) plus a host-app identity (``appId``,
``bid``, ``channelId``). Both blocks are stable per host-app, so this module
exposes a small dataclass holding them and a convenience constructor for
``com.pwrd.htassistant`` populated with values verified against the captured
HAR (``_dev_data/bbs-api.tajiduo.com_2026_04_21_11_10_31.har``).
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

__all__ = ["AndroidDeviceProfile", "DeviceProfile"]


@runtime_checkable
class DeviceProfile(Protocol):
    """Read-only view over the device + host-app identity required for signing.

    All values are kept as ``str`` because they are eventually concatenated with
    the timestamp to form the MD5 ``sign`` source string.
    """

    @property
    def device_id(self) -> str: ...
    @property
    def device_type(self) -> str: ...
    @property
    def device_name(self) -> str: ...
    @property
    def device_model(self) -> str: ...
    @property
    def device_sys(self) -> str: ...
    @property
    def sdk_version(self) -> str: ...
    @property
    def version_code(self) -> str: ...
    @property
    def bid(self) -> str: ...
    @property
    def app_id(self) -> str: ...
    @property
    def channel_id(self) -> str: ...

    def base_params(self) -> dict[str, str]:
        """Return the full param block to be merged into every Laohu request."""
        ...


@dataclass(slots=True, frozen=True)
class AndroidDeviceProfile:
    """A concrete Android device + host-app identity bundle."""

    device_id: str
    device_model: str = "25098PN5AC"
    device_sys: str = "16"
    sdk_version: str = "4.273.0"
    version_code: str = "11"
    bid: str = "com.pwrd.htassistant"
    app_id: str = "10550"
    channel_id: str = "1"
    device_type: str = field(default="")
    device_name: str = field(default="")

    def __post_init__(self) -> None:
        # device_type / device_name typically mirror device_model on stock Android.
        if not self.device_type:
            object.__setattr__(self, "device_type", self.device_model)
        if not self.device_name:
            object.__setattr__(self, "device_name", self.device_model)

    @classmethod
    def for_htassistant(cls, device_id: str | None = None) -> AndroidDeviceProfile:
        """Default profile mirroring the captured htassistant Android client."""
        return cls(device_id=device_id or secrets.token_hex(16))

    def base_params(self) -> dict[str, str]:
        return {
            "deviceId": self.device_id,
            "deviceType": self.device_type,
            "deviceName": self.device_name,
            "deviceModel": self.device_model,
            "deviceSys": self.device_sys,
            "sdkVersion": self.sdk_version,
            "versionCode": self.version_code,
            "bid": self.bid,
            "appId": self.app_id,
            "channelId": self.channel_id,
        }
