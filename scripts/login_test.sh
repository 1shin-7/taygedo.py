#!/usr/bin/env bash
# Minimum-gap login test:
#   1. Read cellphone + captcha from $1, $2.
#   2. POST sendPhoneCaptchaWithOutLogin via the Python SignLaohu (we need the sign).
#   3. POST sms/new/login (reuse Python sign).
#   4. Immediately POST /usercenter/api/login via xh.
# This is just a thin orchestrator — the heavy lifting (AES + MD5 sign) stays in
# Python because it's already correct and reused by the framework.
set -euo pipefail

cd "$(dirname "$0")/.."

PHONE="${1:?usage: $0 <cellphone> <captcha>}"
CAPTCHA="${2:?usage: $0 <cellphone> <captcha>}"

# Run a tiny Python helper that does sms_login and prints the laohu token.
TOKEN=$(uv run python <<PY
import asyncio, sys
from taygedo.client import TaygedoClient
from taygedo.models import SmsLoginRequest

async def main():
    async with TaygedoClient() as c:
        env = await c.login.sms_login(
            body=SmsLoginRequest.model_validate({
                "cellphone": "$PHONE",
                "captcha": "$CAPTCHA",
                "areaCodeId": "1",
            }),
        )
        if env.result is None:
            sys.exit(f"sms_login failed: code={env.code} msg={env.message}")
        # Print: token<TAB>userId<TAB>deviceId
        print(f"{env.result.token}\t{env.result.user_id}\t{c.device.device_id}")

asyncio.run(main())
PY
)

echo "Got laohu token: $TOKEN"
LAOHU_TOKEN=$(echo "$TOKEN" | cut -f1)
USER_ID=$(echo "$TOKEN" | cut -f2)
DEVICE_ID=$(echo "$TOKEN" | cut -f3)

echo
echo "=== xh POST /usercenter/api/login (immediately) ==="
xh --ignore-stdin -v --form POST https://bbs-api.tajiduo.com/usercenter/api/login \
    "token=$LAOHU_TOKEN" \
    "userIdentity=$USER_ID" \
    "appId=10551" \
    "accept:application/json, text/plain, */*" \
    platform:android \
    appversion:1.2.2 \
    uid:0 \
    "deviceid:$DEVICE_ID" \
    User-Agent:okhttp/4.12.0
