"""Authentication payloads — bbs login + LaohuSDK login flow."""

from __future__ import annotations

from pydantic import Field

from ._base import BbsBase, LaohuBase

__all__ = [
    "AreaCode",
    "BbsLoginResult",
    "GdtAdConfig",
    "InitConfig",
    "OneKeySmsLogin",
    "SmsLoginResult",
    "UserIdentify",
    "WebViewUrls",
]


# ---------- bbs-api.tajiduo.com ---------------------------------------------


class BbsLoginResult(BbsBase):
    """``POST /usercenter/api/login`` payload."""

    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    uid: int
    first_login: bool = Field(alias="firstLogin", default=False)


# ---------- user.laohu.com --------------------------------------------------


class UserIdentify(LaohuBase):
    """Real-name verification block embedded in ``SmsLoginResult.userIdentify``."""

    user_id: int = Field(alias="userId")
    real_name: str = Field(alias="realName", default="")
    id_number: str = Field(alias="idNumber", default="")
    age: int = 0
    sex: int = 0
    civic_type: int = Field(alias="civicType", default=0)
    status: int = 0
    times: int = 0
    contact_info: str = Field(alias="contactInfo", default="")
    facial_status: int = Field(alias="facialStatus", default=0)
    passport: int = 0
    pi: str = ""
    need_check: bool = Field(alias="needCheck", default=False)
    create_time: int = Field(alias="createTime", default=0)
    update_time: int = Field(alias="updateTime", default=0)
    button: int = 0
    """Realname-action button state (LaohuSDK; absent in older payloads)."""
    msg: str = ""
    """Server-side message accompanying the realname state."""


class SmsLoginResult(LaohuBase):
    """``POST /openApi/sms/new/login`` payload."""

    user_id: int = Field(alias="userId")
    username: str
    nickname: str = ""
    cellphone: str = ""
    show_cellphone: str = Field(alias="showCellphone", default="")
    email: str = ""
    show_email: str = Field(alias="showEmail", default="")
    show_contact_info: str = Field(alias="showContactInfo", default="")
    id_card_type: int = Field(alias="idCardType", default=0)
    is_temp_user: bool = Field(alias="isTempUser", default=False)
    expire_tips: str = Field(alias="expireTips", default="")
    token: str
    """LaohuSDK token to be exchanged for a bbs accessToken via ``/usercenter/api/login``."""

    have_pwd: bool = Field(alias="havePwd", default=False)
    is_active: bool = Field(alias="isActive", default=True)
    adult: int = 1
    user_identify: UserIdentify | None = Field(alias="userIdentify", default=None)
    secure_score: int = Field(alias="secureScore", default=0)
    set_pwd: bool = Field(alias="setPwd", default=False)
    set_third_cellphone: bool = Field(alias="setThirdCellphone", default=False)
    source: int = 0
    special_account: int = Field(alias="specialAccount", default=0)
    new_login: bool = Field(alias="newLogin", default=False)
    trade_time: int = Field(alias="tradeTime", default=0)
    sex: int | None = None
    is_head_img_default: bool = Field(alias="isHeadImgDefault", default=False)
    head_img: str = Field(alias="headImg", default="")
    bind_relation: dict[str, object] = Field(alias="bindRelation", default_factory=dict)
    user_games: list[object] = Field(alias="userGames", default_factory=list)
    ios_review_url: str = Field(alias="iosReviewUrl", default="")
    encrypted_id: str = Field(alias="encryptedId", default="")
    need_bind_mobile: int = Field(alias="needBindMobile", default=0)
    facial_ticket: str = Field(alias="facialTicket", default="")
    """Optional ticket used during facial-recognition realname flows."""
    ticket: str = ""
    """Optional cross-call ticket returned by some login pathways."""


class AreaCode(LaohuBase):
    """One row in ``/m/newApi/areaCode/list``."""

    area_code_id: int = Field(alias="areaCodeId")
    area_code: int = Field(alias="areaCode")
    area_name: str = Field(alias="areaName")


class OneKeySmsLogin(LaohuBase):
    """One-tap SMS login provider config inside ``InitConfig``."""

    app_key: str = Field(alias="appKey", default="")
    one_key_app_id: str = Field(alias="oneKeyAppId", default="")
    ym_one_key_app_id: str = Field(alias="ymOneKeyAppId", default="")
    chuanglan_one_key_app_id: str = Field(alias="chuanglanOneKeyAppId", default="")
    probability: str = ""


class GdtAdConfig(LaohuBase):
    gdt_switch: int = Field(alias="gdtSwitch", default=0)
    gdt_user_action_set_id: str = Field(alias="gdtUserActionSetId", default="")
    gdt_app_secret_key: str = Field(alias="gdtAppSecretKey", default="")


class InitConfig(LaohuBase):
    """``/m/newApi/initConfig`` payload."""

    one_key_sms_login: OneKeySmsLogin = Field(alias="oneKeySmsLogin")
    login_option_config: list[int] = Field(
        alias="loginOptionConfig", default_factory=list,
    )
    wm_oauth2_client_id: int = Field(alias="wmOauth2ClientId", default=0)
    ace: object | None = None
    service_terms: object | None = Field(alias="serviceTerms", default=None)
    client_log_switch: int = Field(alias="clientLogSwitch", default=0)
    qq_app_id: str = "-1"
    weixin_app_id: str = "-1"
    weibo_app_key: str = "-1"
    taptap: dict[str, object] = Field(default_factory=dict)
    game_customization_log_upload_address: str | None = Field(
        alias="gameCustomizationLogUploadAddress", default=None,
    )
    rvc: bool = True
    general_log_upload_address: str | None = Field(
        alias="generalLogUploadAddress", default=None,
    )
    real_name_status: int = Field(alias="realNameStatus", default=0)
    real_name_tips: str = Field(alias="realNameTips", default="")
    gdt_ad_pre_attribution_config: GdtAdConfig = Field(
        alias="gdtAdPreAttributionConfig", default_factory=GdtAdConfig,
    )
    disable_ia_ad: int = Field(alias="DisableIAAd", default=0)
    request_idfa: int = 0
    bbs_switch: int = Field(alias="bbsSwitch", default=0)
    activity_wm_passport_switch: int = Field(
        alias="activityWmPassportSwitch", default=0,
    )
    imei: int = 0
    receipt: int = 1
    kefu_switch: int = Field(alias="kefuSwitch", default=0)


class WebViewUrls(LaohuBase):
    """``POST /m/newThird/getWebViewUrl`` payload."""

    state: str = ""
    qq_url: str = Field(alias="qqUrl", default="")
    wx_url: str = Field(alias="wxUrl", default="")
    pw_url: str = Field(alias="pwUrl", default="")
    sina_url: str = Field(alias="sinaUrl", default="")
    qq_login_redi: str = Field(alias="qqLoginRedi", default="")
    qq_bind_redi: str = Field(alias="qqBindRedi", default="")
    qq_comp_redi: str = Field(alias="qqCompRedi", default="")
    wx_login_redirect: str = Field(alias="wxLoginRedirect", default="")
    pw_login_redi: str = Field(alias="pwLoginRedi", default="")
    pw_comp_redi: str = Field(alias="pwCompRedi", default="")
    sina_login_redi: str = Field(alias="sinaLoginRedi", default="")
    sina_bind_redi: str = Field(alias="sinaBindRedi", default="")
    sina_comp_redi: str = Field(alias="sinaCompRedi", default="")
    sina_get_fans_redi: str = Field(alias="sinaGetFansRedi", default="")
