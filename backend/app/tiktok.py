from __future__ import annotations

import math
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

import requests
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.orm import Session

from .config import settings
from .models import TikTokAccount, TikTokOAuthState, VideoJob
from .schemas import TikTokPublishRequest


TIKTOK_AUTHORIZE_URL = (
    "https://www.tiktok.com/v2/auth/authorize/"
)
TIKTOK_TOKEN_URL = (
    "https://open.tiktokapis.com/v2/oauth/token/"
)
TIKTOK_REVOKE_URL = (
    "https://open.tiktokapis.com/v2/oauth/revoke/"
)
TIKTOK_USER_INFO_URL = (
    "https://open.tiktokapis.com/v2/user/info/"
)
TIKTOK_CREATOR_INFO_URL = (
    "https://open.tiktokapis.com/"
    "v2/post/publish/creator_info/query/"
)
TIKTOK_DIRECT_POST_URL = (
    "https://open.tiktokapis.com/"
    "v2/post/publish/video/init/"
)
TIKTOK_POST_STATUS_URL = (
    "https://open.tiktokapis.com/"
    "v2/post/publish/status/fetch/"
)

ACCOUNT_ID = 1
STATE_LIFETIME_MINUTES = 10
TOKEN_REFRESH_MARGIN_MINUTES = 5

MIN_CHUNK_SIZE = 5 * 1024 * 1024
PREFERRED_CHUNK_SIZE = 32 * 1024 * 1024
MAX_SINGLE_CHUNK_SIZE = 64 * 1024 * 1024


class TikTokAPIError(RuntimeError):
    pass


def _utcnow() -> datetime:
    return datetime.utcnow()


def _fernet() -> Fernet:
    settings.validate_tiktok_configuration()

    try:
        return Fernet(
            settings.tiktok_token_encryption_key.encode(
                "utf-8"
            )
        )
    except (ValueError, TypeError) as exc:
        raise RuntimeError(
            "TIKTOK_TOKEN_ENCRYPTION_KEY is not a valid "
            "Fernet key. Generate one with "
            "`python -c \"from cryptography.fernet "
            "import Fernet; print(Fernet.generate_key().decode())\"`."
        ) from exc


def _encrypt(value: str) -> str:
    return _fernet().encrypt(
        value.encode("utf-8")
    ).decode("utf-8")


def _decrypt(value: str) -> str:
    try:
        return _fernet().decrypt(
            value.encode("utf-8")
        ).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError(
            "Stored TikTok token could not be decrypted. "
            "The encryption key may have changed."
        ) from exc


def _json_or_error(
    response: requests.Response,
    operation: str,
) -> dict:
    try:
        data = response.json()
    except ValueError:
        data = {
            "raw_response": response.text,
        }

    if not response.ok:
        raise TikTokAPIError(
            f"{operation} failed with HTTP "
            f"{response.status_code}: {data}"
        )

    error = data.get("error")

    if isinstance(error, dict):
        code = error.get("code")

        if code and code != "ok":
            raise TikTokAPIError(
                f"{operation} failed: "
                f"{code}: {error.get('message', '')}"
            )

    if isinstance(error, str):
        raise TikTokAPIError(
            f"{operation} failed: "
            f"{error}: "
            f"{data.get('error_description', '')}"
        )

    return data


def create_authorization_url(
    db: Session,
) -> str:
    settings.validate_tiktok_configuration()

    now = _utcnow()

    db.query(TikTokOAuthState).filter(
        TikTokOAuthState.expires_at < now
    ).delete(
        synchronize_session=False
    )

    state = secrets.token_urlsafe(48)

    db.add(
        TikTokOAuthState(
            state=state,
            expires_at=now
            + timedelta(
                minutes=STATE_LIFETIME_MINUTES
            ),
        )
    )
    db.commit()

    query = urlencode(
        {
            "client_key":
                settings.tiktok_client_key,
            "response_type":
                "code",
            "scope":
                settings.tiktok_scopes,
            "redirect_uri":
                settings.tiktok_redirect_uri,
            "state":
                state,
            "disable_auto_auth":
                "1",
        }
    )

    return (
        f"{TIKTOK_AUTHORIZE_URL}?{query}"
    )


def exchange_authorization_code(
    db: Session,
    code: str,
    state: str,
) -> TikTokAccount:
    oauth_state = db.get(
        TikTokOAuthState,
        state,
    )

    if not oauth_state:
        raise TikTokAPIError(
            "OAuth state is invalid or has already been used."
        )

    if oauth_state.expires_at < _utcnow():
        db.delete(oauth_state)
        db.commit()

        raise TikTokAPIError(
            "OAuth state has expired. Start the connection again."
        )

    db.delete(oauth_state)
    db.commit()

    response = requests.post(
        TIKTOK_TOKEN_URL,
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded",
            "Cache-Control":
                "no-cache",
        },
        data={
            "client_key":
                settings.tiktok_client_key,
            "client_secret":
                settings.tiktok_client_secret,
            "code":
                code,
            "grant_type":
                "authorization_code",
            "redirect_uri":
                settings.tiktok_redirect_uri,
        },
        timeout=45,
    )

    token_data = _json_or_error(
        response,
        "TikTok token exchange",
    )

    access_token = token_data[
        "access_token"
    ]
    refresh_token = token_data[
        "refresh_token"
    ]

    profile = fetch_user_profile(
        access_token
    )

    now = _utcnow()

    account = db.get(
        TikTokAccount,
        ACCOUNT_ID,
    )

    if not account:
        account = TikTokAccount(
            id=ACCOUNT_ID,
            open_id=token_data["open_id"],
            access_token_encrypted="",
            refresh_token_encrypted="",
            access_token_expires_at=now,
            refresh_token_expires_at=now,
        )
        db.add(account)

    account.open_id = token_data[
        "open_id"
    ]
    account.display_name = profile.get(
        "display_name"
    )
    account.avatar_url = profile.get(
        "avatar_url"
    )
    account.scope = token_data.get(
        "scope",
        "",
    )
    account.access_token_encrypted = (
        _encrypt(access_token)
    )
    account.refresh_token_encrypted = (
        _encrypt(refresh_token)
    )
    account.access_token_expires_at = (
        now
        + timedelta(
            seconds=int(
                token_data.get(
                    "expires_in",
                    86400,
                )
            )
        )
    )
    account.refresh_token_expires_at = (
        now
        + timedelta(
            seconds=int(
                token_data.get(
                    "refresh_expires_in",
                    31536000,
                )
            )
        )
    )
    account.updated_at = now

    db.commit()
    db.refresh(account)

    return account


def fetch_user_profile(
    access_token: str,
) -> dict:
    response = requests.get(
        TIKTOK_USER_INFO_URL,
        headers={
            "Authorization":
                f"Bearer {access_token}",
        },
        params={
            "fields":
                "open_id,display_name,avatar_url",
        },
        timeout=30,
    )

    data = _json_or_error(
        response,
        "TikTok user profile request",
    )

    return (
        data.get("data", {})
        .get("user", {})
    )


def get_account(
    db: Session,
) -> TikTokAccount | None:
    return db.get(
        TikTokAccount,
        ACCOUNT_ID,
    )


def get_valid_access_token(
    db: Session,
) -> str:
    account = get_account(db)

    if not account:
        raise TikTokAPIError(
            "No TikTok account is connected."
        )

    now = _utcnow()

    if (
        account.access_token_expires_at
        > now
        + timedelta(
            minutes=TOKEN_REFRESH_MARGIN_MINUTES
        )
    ):
        return _decrypt(
            account.access_token_encrypted
        )

    if account.refresh_token_expires_at <= now:
        raise TikTokAPIError(
            "TikTok refresh token has expired. "
            "Reconnect the account."
        )

    refresh_token = _decrypt(
        account.refresh_token_encrypted
    )

    response = requests.post(
        TIKTOK_TOKEN_URL,
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded",
            "Cache-Control":
                "no-cache",
        },
        data={
            "client_key":
                settings.tiktok_client_key,
            "client_secret":
                settings.tiktok_client_secret,
            "grant_type":
                "refresh_token",
            "refresh_token":
                refresh_token,
        },
        timeout=45,
    )

    token_data = _json_or_error(
        response,
        "TikTok token refresh",
    )

    new_access_token = token_data[
        "access_token"
    ]
    new_refresh_token = token_data.get(
        "refresh_token",
        refresh_token,
    )

    account.access_token_encrypted = (
        _encrypt(new_access_token)
    )
    account.refresh_token_encrypted = (
        _encrypt(new_refresh_token)
    )
    account.scope = token_data.get(
        "scope",
        account.scope,
    )
    account.access_token_expires_at = (
        now
        + timedelta(
            seconds=int(
                token_data.get(
                    "expires_in",
                    86400,
                )
            )
        )
    )
    account.refresh_token_expires_at = (
        now
        + timedelta(
            seconds=int(
                token_data.get(
                    "refresh_expires_in",
                    31536000,
                )
            )
        )
    )
    account.updated_at = now

    db.commit()

    return new_access_token


def disconnect_account(
    db: Session,
) -> None:
    account = get_account(db)

    if not account:
        return

    try:
        access_token = _decrypt(
            account.access_token_encrypted
        )

        requests.post(
            TIKTOK_REVOKE_URL,
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded",
                "Cache-Control":
                    "no-cache",
            },
            data={
                "client_key":
                    settings.tiktok_client_key,
                "client_secret":
                    settings.tiktok_client_secret,
                "token":
                    access_token,
            },
            timeout=30,
        )
    finally:
        db.delete(account)
        db.commit()


def query_creator_info(
    db: Session,
) -> dict:
    access_token = get_valid_access_token(
        db
    )

    response = requests.post(
        TIKTOK_CREATOR_INFO_URL,
        headers={
            "Authorization":
                f"Bearer {access_token}",
            "Content-Type":
                "application/json; charset=UTF-8",
        },
        json={},
        timeout=30,
    )

    data = _json_or_error(
        response,
        "TikTok creator info request",
    )

    return data.get(
        "data",
        {},
    )


def _chunk_plan(
    video_size: int,
) -> tuple[int, int]:
    if video_size <= 0:
        raise TikTokAPIError(
            "The video file is empty."
        )

    if video_size <= MAX_SINGLE_CHUNK_SIZE:
        return video_size, 1

    chunk_size = PREFERRED_CHUNK_SIZE
    total_chunk_count = (
        video_size // chunk_size
    )

    if total_chunk_count < 1:
        total_chunk_count = 1

    if total_chunk_count > 1000:
        raise TikTokAPIError(
            "The video requires more than 1000 upload chunks."
        )

    return (
        chunk_size,
        total_chunk_count,
    )


def _upload_file(
    upload_url: str,
    path: Path,
    chunk_size: int,
    total_chunk_count: int,
) -> None:
    total_size = path.stat().st_size

    with path.open("rb") as source:
        for index in range(
            total_chunk_count
        ):
            start = index * chunk_size

            if index == total_chunk_count - 1:
                length = total_size - start
            else:
                length = chunk_size

            chunk = source.read(length)

            if len(chunk) != length:
                raise TikTokAPIError(
                    "Could not read the expected video upload chunk."
                )

            end = (
                start
                + len(chunk)
                - 1
            )

            response = requests.put(
                upload_url,
                headers={
                    "Content-Type":
                        "video/mp4",
                    "Content-Length":
                        str(len(chunk)),
                    "Content-Range":
                        f"bytes {start}-{end}/{total_size}",
                },
                data=chunk,
                timeout=300,
            )

            expected_status = (
                201
                if index
                == total_chunk_count - 1
                else 206
            )

            if response.status_code != expected_status:
                raise TikTokAPIError(
                    "TikTok video chunk upload failed. "
                    f"Expected HTTP {expected_status}, "
                    f"received {response.status_code}: "
                    f"{response.text}"
                )


def publish_video(
    db: Session,
    job: VideoJob,
    payload: TikTokPublishRequest,
) -> str:
    if not job.output_video:
        raise TikTokAPIError(
            "This job has no rendered video."
        )

    video_path = Path(
        job.output_video
    )

    if not video_path.exists():
        raise TikTokAPIError(
            "The rendered MP4 file does not exist."
        )

    creator_info = query_creator_info(
        db
    )

    privacy_options = creator_info.get(
        "privacy_level_options",
        [],
    )

    if (
        payload.privacy_level
        not in privacy_options
    ):
        raise TikTokAPIError(
            "The selected privacy level is not currently "
            "available for this TikTok account."
        )

    access_token = get_valid_access_token(
        db
    )

    video_size = video_path.stat().st_size
    (
        chunk_size,
        total_chunk_count,
    ) = _chunk_plan(video_size)

    init_response = requests.post(
        TIKTOK_DIRECT_POST_URL,
        headers={
            "Authorization":
                f"Bearer {access_token}",
            "Content-Type":
                "application/json; charset=UTF-8",
        },
        json={
            "post_info": {
                "title":
                    payload.caption,
                "privacy_level":
                    payload.privacy_level,
                "disable_duet":
                    payload.disable_duet,
                "disable_comment":
                    payload.disable_comment,
                "disable_stitch":
                    payload.disable_stitch,
                "video_cover_timestamp_ms":
                    payload.video_cover_timestamp_ms,
                "brand_content_toggle":
                    payload.brand_content_toggle,
                "brand_organic_toggle":
                    payload.brand_organic_toggle,
                "is_aigc":
                    payload.is_aigc,
            },
            "source_info": {
                "source":
                    "FILE_UPLOAD",
                "video_size":
                    video_size,
                "chunk_size":
                    chunk_size,
                "total_chunk_count":
                    total_chunk_count,
            },
        },
        timeout=45,
    )

    init_data = _json_or_error(
        init_response,
        "TikTok direct-post initialization",
    )

    publish_data = init_data.get(
        "data",
        {},
    )
    publish_id = publish_data.get(
        "publish_id"
    )
    upload_url = publish_data.get(
        "upload_url"
    )

    if not publish_id or not upload_url:
        raise TikTokAPIError(
            "TikTok did not return a publish ID and upload URL."
        )

    job.tiktok_publish_id = publish_id
    job.tiktok_status = "PROCESSING_UPLOAD"
    job.tiktok_caption = payload.caption
    job.tiktok_privacy_level = (
        payload.privacy_level
    )
    job.tiktok_last_error = None
    job.upload_status = "uploading"
    db.commit()

    try:
        _upload_file(
            upload_url=upload_url,
            path=video_path,
            chunk_size=chunk_size,
            total_chunk_count=total_chunk_count,
        )
    except Exception as exc:
        job.upload_status = "failed"
        job.tiktok_status = "FAILED"
        job.tiktok_last_error = str(exc)
        db.commit()
        raise

    job.upload_status = "processing"
    job.tiktok_status = "PROCESSING_UPLOAD"
    db.commit()

    return publish_id


def fetch_post_status(
    db: Session,
    job: VideoJob,
) -> dict:
    if not job.tiktok_publish_id:
        raise TikTokAPIError(
            "This job has no TikTok publish ID."
        )

    access_token = get_valid_access_token(
        db
    )

    response = requests.post(
        TIKTOK_POST_STATUS_URL,
        headers={
            "Authorization":
                f"Bearer {access_token}",
            "Content-Type":
                "application/json; charset=UTF-8",
        },
        json={
            "publish_id":
                job.tiktok_publish_id,
        },
        timeout=30,
    )

    response_data = _json_or_error(
        response,
        "TikTok post-status request",
    )

    data = response_data.get(
        "data",
        {},
    )
    status = data.get(
        "status",
        "UNKNOWN",
    )
    fail_reason = data.get(
        "fail_reason"
    )

    job.tiktok_status = status
    job.tiktok_last_error = fail_reason

    if status == "PUBLISH_COMPLETE":
        job.upload_status = "uploaded"
    elif status == "FAILED":
        job.upload_status = "failed"
    else:
        job.upload_status = "processing"

    db.commit()

    return data
