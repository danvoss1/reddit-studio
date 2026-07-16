from __future__ import annotations

import secrets
import shutil
from pathlib import Path
from urllib.parse import urlencode
from uuid import uuid4

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from .config import (
    BANNER_DIR,
    GAMEPLAY_DIR,
    MUSIC_DIR,
    settings,
)
from .db import Base, engine, get_db
from .models import Asset, TikTokAccount, VideoJob
from .pipeline import append_log, start_job
from .schemas import (
    AssetRead,
    JobCreate,
    JobRead,
    PublicationUpdate,
    ScriptApproval,
    StatsRead,
    TikTokAccountRead,
    TikTokConnectRead,
    TikTokCreatorInfoRead,
    TikTokPostStatusRead,
    TikTokPublishRead,
    TikTokPublishRequest,
    VoiceRead,
)
from .tiktok import (
    TikTokAPIError,
    create_authorization_url,
    disconnect_account,
    exchange_authorization_code,
    fetch_post_status,
    get_account,
    publish_video,
    query_creator_info,
)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reddit Studio API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# These routes must stay reachable without the private dashboard API key.
# TikTok's OAuth callback is protected by the one-time OAuth state value.
PUBLIC_API_PATHS = {
    "/api/health",
    "/api/tiktok/callback",
    "/docs",
    "/openapi.json",
    "/redoc",
}


@app.middleware("http")
async def require_local_app_key(
    request: Request,
    call_next,
):
    if (
        request.method == "OPTIONS"
        or request.url.path in PUBLIC_API_PATHS
    ):
        return await call_next(request)

    configured_key = settings.local_app_api_key

    if not configured_key:
        return JSONResponse(
            status_code=503,
            content={
                "detail": (
                    "LOCAL_APP_API_KEY is not configured on the backend."
                )
            },
        )

    supplied_key = request.headers.get(
        "X-Reddit-Studio-Key",
        "",
    )

    if not secrets.compare_digest(
        supplied_key,
        configured_key,
    ):
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Invalid or missing local application key."
            },
        )

    return await call_next(request)


def _http_error(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=str(exc),
    )


@app.get("/api/health")
def health():
    return {
        "status": "ok",
    }


@app.get(
    "/api/voices",
    response_model=list[VoiceRead],
)
def list_voices():
    return settings.available_voices()


@app.get(
    "/api/jobs",
    response_model=list[JobRead],
)
def list_jobs(
    db: Session = Depends(get_db),
):
    return (
        db.query(VideoJob)
        .order_by(
            VideoJob.created_at.desc()
        )
        .all()
    )


@app.post(
    "/api/jobs",
    response_model=JobRead,
    status_code=201,
)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
):
    job = VideoJob(
        id=str(uuid4()),
        source_mode=payload.source_mode,
        reddit_url=payload.reddit_url,
        source_title=payload.source_title,
        source_body=payload.source_body,
        gameplay_asset=payload.gameplay_asset,
        music_asset=payload.music_asset,
        banner_asset=payload.banner_asset,
        use_music=payload.use_music,
        voice_key=payload.voice_key,
        playback_speed=payload.playback_speed,
        title=(
            payload.source_title
            or "New Reddit video"
        ),
        status="queued",
        stage="Queued",
        progress=0,
    )

    append_log(
        job,
        "Job created.",
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    start_job(
        job.id,
        "prepare",
    )

    return job


@app.get(
    "/api/jobs/{job_id}",
    response_model=JobRead,
)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.get(
        VideoJob,
        job_id,
    )

    if not job:
        raise HTTPException(
            404,
            "Job not found.",
        )

    return job


@app.post(
    "/api/jobs/{job_id}/approve",
    response_model=JobRead,
)
def approve_job(
    job_id: str,
    payload: ScriptApproval,
    db: Session = Depends(get_db),
):
    job = db.get(
        VideoJob,
        job_id,
    )

    if not job:
        raise HTTPException(
            404,
            "Job not found.",
        )

    if job.status != "awaiting_approval":
        raise HTTPException(
            409,
            "Job is not waiting for approval.",
        )

    job.approved_script = (
        payload.script.strip()
    )
    job.status = "queued"
    job.stage = "Approved and queued"

    append_log(
        job,
        "Script approved.",
    )

    db.commit()

    start_job(
        job.id,
        "render",
    )

    db.refresh(job)

    return job


@app.post(
    "/api/jobs/{job_id}/cancel",
    response_model=JobRead,
)
def cancel_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.get(
        VideoJob,
        job_id,
    )

    if not job:
        raise HTTPException(
            404,
            "Job not found.",
        )

    if job.status in {
        "completed",
        "failed",
    }:
        raise HTTPException(
            409,
            "Finished jobs cannot be cancelled.",
        )

    job.status = "cancelled"
    job.stage = "Cancelled"

    append_log(
        job,
        "Cancellation requested.",
    )

    db.commit()

    return job


@app.post(
    "/api/jobs/{job_id}/publication",
    response_model=JobRead,
)
def update_publication(
    job_id: str,
    payload: PublicationUpdate,
    db: Session = Depends(get_db),
):
    job = db.get(
        VideoJob,
        job_id,
    )

    if not job:
        raise HTTPException(
            404,
            "Job not found.",
        )

    job.upload_status = (
        payload.upload_status
    )
    job.platform_url = (
        payload.platform_url
    )
    job.views = payload.views

    db.commit()
    db.refresh(job)

    return job


@app.get("/api/jobs/{job_id}/video")
def download_video(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.get(
        VideoJob,
        job_id,
    )

    if (
        not job
        or not job.output_video
    ):
        raise HTTPException(
            404,
            "Video is not available.",
        )

    path = Path(
        job.output_video
    )

    if not path.exists():
        raise HTTPException(
            404,
            "Video file no longer exists.",
        )

    return FileResponse(
        path,
        media_type="video/mp4",
        filename=(
            f"{job.title[:60]}.mp4"
        ),
    )


@app.get(
    "/api/assets",
    response_model=list[AssetRead],
)
def list_assets(
    kind: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Asset)

    if kind:
        query = query.filter(
            Asset.kind == kind
        )

    return (
        query
        .order_by(
            Asset.created_at.desc()
        )
        .all()
    )


@app.post(
    "/api/assets/{kind}",
    response_model=AssetRead,
    status_code=201,
)
def upload_asset(
    kind: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    allowed = {
        "gameplay": {
            ".mp4",
            ".mov",
            ".mkv",
            ".webm",
        },
        "music": {
            ".mp3",
            ".wav",
            ".m4a",
            ".aac",
        },
        "banner": {
            ".png",
            ".webp",
        },
    }

    folders = {
        "gameplay":
            GAMEPLAY_DIR,
        "music":
            MUSIC_DIR,
        "banner":
            BANNER_DIR,
    }

    if kind not in allowed:
        raise HTTPException(
            422,
            "kind must be gameplay, music, or banner.",
        )

    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in allowed[kind]:
        raise HTTPException(
            422,
            f"Unsupported {kind} file extension.",
        )

    asset_id = str(uuid4())
    destination = (
        folders[kind]
        / f"{asset_id}{extension}"
    )

    with destination.open(
        "wb"
    ) as output:
        shutil.copyfileobj(
            file.file,
            output,
        )

    asset = Asset(
        id=asset_id,
        kind=kind,
        original_name=(
            file.filename
            or destination.name
        ),
        stored_path=str(
            destination
        ),
        size_bytes=(
            destination
            .stat()
            .st_size
        ),
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset


@app.delete(
    "/api/assets/{asset_id}",
    status_code=204,
)
def delete_asset(
    asset_id: str,
    db: Session = Depends(get_db),
):
    asset = db.get(
        Asset,
        asset_id,
    )

    if not asset:
        raise HTTPException(
            404,
            "Asset not found.",
        )

    Path(
        asset.stored_path
    ).unlink(
        missing_ok=True,
    )

    db.delete(asset)
    db.commit()


@app.get(
    "/api/stats",
    response_model=StatsRead,
)
def stats(
    db: Session = Depends(get_db),
):
    def count(
        status: str,
    ) -> int:
        return (
            db.query(
                func.count(
                    VideoJob.id
                )
            )
            .filter(
                VideoJob.status
                == status
            )
            .scalar()
            or 0
        )

    return StatsRead(
        total=(
            db.query(
                func.count(
                    VideoJob.id
                )
            )
            .scalar()
            or 0
        ),
        queued=count(
            "queued"
        ),
        running=count(
            "running"
        ),
        awaiting_approval=count(
            "awaiting_approval"
        ),
        completed=count(
            "completed"
        ),
        failed=count(
            "failed"
        ),
        uploaded=(
            db.query(
                func.count(
                    VideoJob.id
                )
            )
            .filter(
                VideoJob.upload_status
                == "uploaded"
            )
            .scalar()
            or 0
        ),
        total_views=(
            db.query(
                func.coalesce(
                    func.sum(
                        VideoJob.views
                    ),
                    0,
                )
            )
            .scalar()
            or 0
        ),
    )


@app.get(
    "/api/tiktok/account",
    response_model=TikTokAccountRead,
)
def tiktok_account(
    db: Session = Depends(get_db),
):
    account = get_account(db)

    if not account:
        return TikTokAccountRead(
            connected=False,
        )

    return TikTokAccountRead(
        connected=True,
        display_name=account.display_name,
        avatar_url=account.avatar_url,
        open_id=account.open_id,
        scope=account.scope,
    )


@app.post(
    "/api/tiktok/connect",
    response_model=TikTokConnectRead,
)
def tiktok_connect(
    db: Session = Depends(get_db),
):
    try:
        return TikTokConnectRead(
            authorization_url=(
                create_authorization_url(
                    db
                )
            )
        )
    except Exception as exc:
        raise _http_error(exc) from exc


@app.get("/api/tiktok/callback")
def tiktok_callback(
    code: str | None = Query(
        default=None
    ),
    state: str | None = Query(
        default=None
    ),
    error: str | None = Query(
        default=None
    ),
    error_description: str | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
):
    if error:
        query = urlencode(
            {
                "tiktok_error":
                    error_description
                    or error,
            }
        )

        return RedirectResponse(
            url=(
                f"{settings.local_frontend_url}"
                f"/tiktok?{query}"
            )
        )

    if not code or not state:
        raise HTTPException(
            400,
            "TikTok callback is missing code or state.",
        )

    try:
        exchange_authorization_code(
            db=db,
            code=code,
            state=state,
        )
    except Exception as exc:
        query = urlencode(
            {
                "tiktok_error":
                    str(exc),
            }
        )

        return RedirectResponse(
            url=(
                f"{settings.local_frontend_url}"
                f"/tiktok?{query}"
            )
        )

    return RedirectResponse(
        url=(
            f"{settings.local_frontend_url}"
            "/tiktok?connected=1"
        )
    )


@app.delete(
    "/api/tiktok/account",
    status_code=204,
)
def tiktok_disconnect(
    db: Session = Depends(get_db),
):
    try:
        disconnect_account(db)
    except Exception as exc:
        raise _http_error(exc) from exc


@app.get(
    "/api/tiktok/creator-info",
    response_model=TikTokCreatorInfoRead,
)
def tiktok_creator_info(
    db: Session = Depends(get_db),
):
    try:
        data = query_creator_info(
            db
        )

        return TikTokCreatorInfoRead(
            creator_username=(
                data.get(
                    "creator_username"
                )
            ),
            creator_nickname=(
                data.get(
                    "creator_nickname"
                )
            ),
            creator_avatar_url=(
                data.get(
                    "creator_avatar_url"
                )
            ),
            privacy_level_options=(
                data.get(
                    "privacy_level_options",
                    [],
                )
            ),
            comment_disabled=bool(
                data.get(
                    "comment_disabled",
                    False,
                )
            ),
            duet_disabled=bool(
                data.get(
                    "duet_disabled",
                    False,
                )
            ),
            stitch_disabled=bool(
                data.get(
                    "stitch_disabled",
                    False,
                )
            ),
            max_video_post_duration_sec=int(
                data.get(
                    "max_video_post_duration_sec",
                    0,
                )
            ),
        )
    except Exception as exc:
        raise _http_error(exc) from exc


@app.post(
    "/api/jobs/{job_id}/tiktok/publish",
    response_model=TikTokPublishRead,
)
def tiktok_publish_job(
    job_id: str,
    payload: TikTokPublishRequest,
    db: Session = Depends(get_db),
):
    job = db.get(
        VideoJob,
        job_id,
    )

    if not job:
        raise HTTPException(
            404,
            "Job not found.",
        )

    if job.status != "completed":
        raise HTTPException(
            409,
            "Only completed jobs can be published.",
        )

    try:
        publish_id = publish_video(
            db=db,
            job=job,
            payload=payload,
        )

        return TikTokPublishRead(
            publish_id=publish_id,
            status=(
                job.tiktok_status
                or "PROCESSING_UPLOAD"
            ),
        )
    except Exception as exc:
        job.upload_status = "failed"
        job.tiktok_status = "FAILED"
        job.tiktok_last_error = str(
            exc
        )
        db.commit()

        raise _http_error(exc) from exc


@app.post(
    "/api/jobs/{job_id}/tiktok/status",
    response_model=TikTokPostStatusRead,
)
def tiktok_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.get(
        VideoJob,
        job_id,
    )

    if not job:
        raise HTTPException(
            404,
            "Job not found.",
        )

    try:
        data = fetch_post_status(
            db=db,
            job=job,
        )
    except Exception as exc:
        raise _http_error(exc) from exc

    post_ids = data.get(
        "publicaly_available_post_id",
        [],
    )

    return TikTokPostStatusRead(
        publish_id=(
            job.tiktok_publish_id
            or ""
        ),
        status=data.get(
            "status",
            "UNKNOWN",
        ),
        fail_reason=data.get(
            "fail_reason"
        ),
        publicly_available_post_ids=[
            str(post_id)
            for post_id in post_ids
        ],
        uploaded_bytes=data.get(
            "uploaded_bytes"
        ),
    )
