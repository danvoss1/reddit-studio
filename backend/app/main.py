from __future__ import annotations
import mimetypes
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from .config import (
    BANNER_DIR,
    GAMEPLAY_DIR,
    MUSIC_DIR,
    settings,
)
from .db import Base, engine, get_db
from .models import Asset, VideoJob
from .pipeline import append_log, start_job
from .schemas import (
    AssetRead, JobCreate, JobRead, PublicationUpdate, ScriptApproval, StatsRead, VoiceRead
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reddit Studio API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get(
    "/api/voices",
    response_model=list[VoiceRead],
)
def list_voices():
    return settings.available_voices()


@app.get("/api/jobs", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(VideoJob).order_by(VideoJob.created_at.desc()).all()


@app.post("/api/jobs", response_model=JobRead, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    if payload.source_mode == "reddit_url" and not payload.reddit_url:
        raise HTTPException(422, "reddit_url is required.")
    if payload.source_mode == "manual" and not payload.source_body:
        raise HTTPException(422, "source_body is required.")

    job = VideoJob(
    id=str(uuid4()),
    source_mode=payload.source_mode,
    reddit_url=payload.reddit_url,
    source_title=payload.source_title,
    source_body=payload.source_body,
    gameplay_asset=payload.gameplay_asset,
    music_asset=payload.music_asset,
    use_music=payload.use_music,
    voice_key=payload.voice_key,
    title=payload.source_title or "New Reddit video",
    status="queued",
    stage="Queued",
    progress=0,
    )
    
    append_log(job, "Job created.")
    db.add(job)
    db.commit()
    db.refresh(job)
    start_job(job.id, "prepare")
    return job


@app.get("/api/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(VideoJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    return job


@app.post("/api/jobs/{job_id}/approve", response_model=JobRead)
def approve_job(job_id: str, payload: ScriptApproval, db: Session = Depends(get_db)):
    job = db.get(VideoJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    if job.status != "awaiting_approval":
        raise HTTPException(409, "Job is not waiting for approval.")
    job.approved_script = payload.script.strip()
    job.status = "queued"
    job.stage = "Approved and queued"
    append_log(job, "Script approved.")
    db.commit()
    start_job(job.id, "render")
    db.refresh(job)
    return job


@app.post("/api/jobs/{job_id}/cancel", response_model=JobRead)
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(VideoJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    if job.status in {"completed", "failed"}:
        raise HTTPException(409, "Finished jobs cannot be cancelled.")
    job.status = "cancelled"
    job.stage = "Cancelled"
    append_log(job, "Cancellation requested.")
    db.commit()
    return job


@app.post("/api/jobs/{job_id}/publication", response_model=JobRead)
def update_publication(job_id: str, payload: PublicationUpdate, db: Session = Depends(get_db)):
    job = db.get(VideoJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    job.upload_status = payload.upload_status
    job.platform_url = payload.platform_url
    job.views = payload.views
    db.commit()
    return job


@app.get("/api/jobs/{job_id}/video")
def download_video(job_id: str, db: Session = Depends(get_db)):
    job = db.get(VideoJob, job_id)
    if not job or not job.output_video:
        raise HTTPException(404, "Video is not available.")
    path = Path(job.output_video)
    if not path.exists():
        raise HTTPException(404, "Video file no longer exists.")
    return FileResponse(path, media_type="video/mp4", filename=f"{job.title[:60]}.mp4")


@app.get("/api/assets", response_model=list[AssetRead])
def list_assets(kind: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Asset)
    if kind:
        query = query.filter(Asset.kind == kind)
    return query.order_by(Asset.created_at.desc()).all()


@app.post("/api/assets/{kind}", response_model=AssetRead, status_code=201)
@app.post("/api/assets/{kind}", response_model=AssetRead, status_code=201)
def upload_asset(
    kind: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    allowed = {
        "gameplay": {".mp4", ".mov", ".mkv", ".webm"},
        "music": {".mp3", ".wav", ".m4a", ".aac"},
        "banner": {".png", ".webp"},
    }
    folders = {
        "gameplay": GAMEPLAY_DIR,
        "music": MUSIC_DIR,
        "banner": BANNER_DIR,
    }

    if kind not in allowed:
        raise HTTPException(
            422, "kind must be gameplay, music, or banner."
        )

    extension = Path(file.filename or "").suffix.lower()
    if extension not in allowed[kind]:
        raise HTTPException(422, f"Unsupported {kind} file extension.")

    asset_id = str(uuid4())
    destination = folders[kind] / f"{asset_id}{extension}"

    with destination.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    asset = Asset(
        id=asset_id,
        kind=kind,
        original_name=file.filename or destination.name,
        stored_path=str(destination),
        size_bytes=destination.stat().st_size,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@app.delete("/api/assets/{asset_id}", status_code=204)
def delete_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(404, "Asset not found.")
    Path(asset.stored_path).unlink(missing_ok=True)
    db.delete(asset)
    db.commit()


@app.get("/api/stats", response_model=StatsRead)
def stats(db: Session = Depends(get_db)):
    def count(status: str) -> int:
        return db.query(func.count(VideoJob.id)).filter(VideoJob.status == status).scalar() or 0
    return StatsRead(
        total=db.query(func.count(VideoJob.id)).scalar() or 0,
        queued=count("queued"),
        running=count("running"),
        awaiting_approval=count("awaiting_approval"),
        completed=count("completed"),
        failed=count("failed"),
        uploaded=db.query(func.count(VideoJob.id)).filter(VideoJob.upload_status == "uploaded").scalar() or 0,
        total_views=db.query(func.coalesce(func.sum(VideoJob.views), 0)).scalar() or 0,
    )
