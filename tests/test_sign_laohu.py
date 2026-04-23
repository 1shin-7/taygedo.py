"""Validate SignLaohu against ground-truth values derived from the algorithm.

Algorithm reference (extracted from the LaohuSDK 4.273.0 dex):

* dex (``com.pwrd.htassistant.MainActivity:35``):
    ``app_key = "89155cc4e8634ec5b1b6364013b23e3e"``
    → AES-ECB key = ``app_key[-16:]`` = ``b"b1b6364013b23e3e"``
* For test fixtures we use the canonical Chinese test phone number
  ``13800138000`` and demo captcha ``123456`` / ``654321`` so the file does
  not embed real PII. The ciphertexts below were precomputed from the
  algorithm itself.
"""

from __future__ import annotations

import time

from taygedo.core import PreparedRequest
from taygedo.device import AndroidDeviceProfile
from taygedo.signers import HTASSISTANT_APP_KEY, LOGIN_SENSITIVE_FIELDS, LaohuConfig, SignLaohu


def _device() -> AndroidDeviceProfile:
    return AndroidDeviceProfile(device_id="0123456789abcdef0123456789abcdef")


def test_app_key_default_matches_dex_extraction() -> None:
    assert HTASSISTANT_APP_KEY == "89155cc4e8634ec5b1b6364013b23e3e"


def test_aes_key_is_app_key_last_16_chars() -> None:
    signer = SignLaohu(LaohuConfig(sensitive_fields=frozenset({"x"})), _device())
    assert signer._encrypt("13800138000") == "Rlh+swk6SKpMGqO+z6pMQw=="


def test_captcha_encrypted_matches_algorithm() -> None:
    signer = SignLaohu(LaohuConfig(), _device())
    assert signer._encrypt("123456") == "TyWSYItqCceQ7+iFvOTXbA=="
    assert signer._encrypt("654321") == "BwVN8TkLcmAPS/SU5P7qyQ=="


def test_send_captcha_sign_is_deterministic() -> None:
    """Reproduce the sign for sendPhoneCaptchaWithOutLogin (cellphone in plaintext)."""
    signer = SignLaohu(LaohuConfig(), _device())
    req = PreparedRequest(
        method="POST",
        url="/m/newApi/sendPhoneCaptchaWithOutLogin",
        params={
            "type": "16",
            "areaCodeId": "1",
            "cellphone": "13800138000",
        },
    )
    out = _sign_with_fixed_timestamp(signer, req, t="1700000000")
    assert out.params["sign"] == "9f56d1d8b1a3786b36e0a448f5274515"
    # cellphone stays plain — this endpoint is NOT in LOGIN_SENSITIVE_FIELDS.
    assert out.params["cellphone"] == "13800138000"


def test_sms_login_encrypts_cellphone_then_signs() -> None:
    """``/openApi/sms/new/login`` AES-encrypts the sensitive fields first."""
    signer = SignLaohu(
        LaohuConfig(sensitive_fields=LOGIN_SENSITIVE_FIELDS, timestamp_unit="ms"),
        _device(),
    )
    req = PreparedRequest(
        method="POST",
        url="/openApi/sms/new/login",
        params={
            "type": "16",
            "areaCodeId": "1",
            "cellphone": "13800138000",
            "captcha": "123456",
        },
    )
    out = signer.sign(req)
    assert out.params["cellphone"] == "Rlh+swk6SKpMGqO+z6pMQw=="
    assert out.params["captcha"] == "TyWSYItqCceQ7+iFvOTXbA=="
    assert "sign" in out.params and len(out.params["sign"]) == 32


def test_sign_uses_encrypted_value_for_sensitive_fields() -> None:
    """Sign must be computed from post-encryption values."""
    signer = SignLaohu(
        LaohuConfig(sensitive_fields=frozenset({"cellphone"})),
        _device(),
    )
    req_plain = PreparedRequest(method="POST", url="/x", params={"cellphone": "13800138000"})
    req_already_encrypted = PreparedRequest(
        method="POST", url="/x", params={"cellphone": "Rlh+swk6SKpMGqO+z6pMQw=="},
    )
    s1 = _sign_with_fixed_timestamp(signer, req_plain, t="1000")
    # Re-sign the second request without the sensitive list so the value is
    # passed through unchanged: the resulting sign must equal s1's.
    passthrough = SignLaohu(LaohuConfig(sensitive_fields=frozenset()), _device())
    s2 = _sign_with_fixed_timestamp(passthrough, req_already_encrypted, t="1000")
    assert s1.params["sign"] == s2.params["sign"]


def test_timestamp_unit_seconds_vs_ms() -> None:
    sec_signer = SignLaohu(LaohuConfig(timestamp_unit="s"), _device())
    ms_signer = SignLaohu(LaohuConfig(timestamp_unit="ms"), _device())
    before_ms = int(time.time() * 1000)
    sec_t = sec_signer._timestamp()
    ms_t = ms_signer._timestamp()
    assert len(sec_t) == 10
    assert len(ms_t) == 13
    assert int(ms_t) - before_ms < 5_000


def test_short_app_key_rejected() -> None:
    import pytest

    from taygedo.core.exceptions import SignError

    with pytest.raises(SignError, match="at least 16"):
        SignLaohu(LaohuConfig(app_key="too short"), _device())


def _sign_with_fixed_timestamp(
    signer: SignLaohu, req: PreparedRequest, *, t: str,
) -> PreparedRequest:
    """Helper: inject a deterministic ``t`` so the generated sign is reproducible."""
    out = req.copy()
    out.params = {**out.params, "t": t}
    return signer.sign(out)
