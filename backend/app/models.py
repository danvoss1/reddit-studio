from __future__ import annotations
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class VideoJob(Base):
    __tablename__ = "video_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    source_mode: Mapped[str] = mapped_column(String(30), default="reddit_url")
    reddit_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_body: Mapped[str | None] = mapped_column(Text, nullable=True)

    title: Mapped[str] = mapped_column(Text, default="Untitled")
    status: Mapped[str] = mapped_column(String(30), default="queued")
    stage: Mapped[str] = mapped_column(String(80), default="Queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    logs: Mapped[str] = mapped_column(Text, default="")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    script: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_script: Mapped[str | None] = mapped_column(Text, nullable=True)

    gameplay_asset: Mapped[str | None] = mapped_column(Text, nullable=True)
    music_asset: Mapped[str | None] = mapped_column(Text, nullable=True)
    banner_asset: Mapped[str | None] = mapped_column(Text, nullable=True)
    use_music: Mapped[bool] = mapped_column(default=True)

    voice_key: Mapped[str] = mapped_column(
        String(30), default="female", nullable=False
    )
    playback_speed: Mapped[float] = mapped_column(
        Float, default=1.2, nullable=False
    )

    output_video: Mapped[str | None] = mapped_column(Text, nullable=True)
    narration_file: Mapped[str | None] = mapped_column(Text, nullable=True)
    subtitle_file: Mapped[str | None] = mapped_column(Text, nullable=True)

    upload_status: Mapped[str] = mapped_column(
        String(30), default="not_uploaded"
    )
    platform_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    kind: Mapped[str] = mapped_column(String(20))
    original_name: Mapped[str] = mapped_column(Text)
    stored_path: Mapped[str] = mapped_column(Text)
    size_bytes: Mapped[int] = mapped_column(Integer)
