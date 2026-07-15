from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class VideoJob(Base):
    __tablename__ = "video_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    source_mode: Mapped[str] = mapped_column(
        String(30),
        default="reddit_url",
    )
    reddit_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    source_title: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    source_body: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        Text,
        default="Untitled",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="queued",
    )
    stage: Mapped[str] = mapped_column(
        String(80),
        default="Queued",
    )
    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    logs: Mapped[str] = mapped_column(
        Text,
        default="",
    )
    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    script: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    approved_script: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    gameplay_asset: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    music_asset: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    banner_asset: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    use_music: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    voice_key: Mapped[str] = mapped_column(
        String(30),
        default="female",
        nullable=False,
    )
    playback_speed: Mapped[float] = mapped_column(
        Float,
        default=1.2,
        nullable=False,
    )

    output_video: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    narration_file: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    subtitle_file: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    upload_status: Mapped[str] = mapped_column(
        String(30),
        default="not_uploaded",
    )
    platform_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    views: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    tiktok_publish_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    tiktok_status: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )
    tiktok_caption: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    tiktok_privacy_level: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )
    tiktok_last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    kind: Mapped[str] = mapped_column(
        String(20),
    )
    original_name: Mapped[str] = mapped_column(
        Text,
    )
    stored_path: Mapped[str] = mapped_column(
        Text,
    )
    size_bytes: Mapped[int] = mapped_column(
        Integer,
    )


class TikTokAccount(Base):
    __tablename__ = "tiktok_accounts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=1,
    )
    open_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )
    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    access_token_encrypted: Mapped[str] = mapped_column(
        Text,
    )
    refresh_token_encrypted: Mapped[str] = mapped_column(
        Text,
    )
    scope: Mapped[str] = mapped_column(
        Text,
        default="",
    )
    access_token_expires_at: Mapped[datetime] = mapped_column(
        DateTime,
    )
    refresh_token_expires_at: Mapped[datetime] = mapped_column(
        DateTime,
    )
    connected_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class TikTokOAuthState(Base):
    __tablename__ = "tiktok_oauth_states"

    state: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
    )
