from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

VoiceKey = Literal["female", "male"]
SourceMode = Literal["reddit_url", "manual"]
UploadStatus = Literal["not_uploaded", "scheduled", "uploaded"]


class JobCreate(BaseModel):
    source_mode: SourceMode = "reddit_url"
    reddit_url: str | None = None
    source_title: str | None = None
    source_body: str | None = None

    gameplay_asset: str | None = None
    music_asset: str | None = None
    banner_asset: str | None = None
    use_music: bool = True

    voice_key: VoiceKey = "female"
    playback_speed: float = Field(default=1.2, ge=0.75, le=2.0)

    @model_validator(mode="after")
    def validate_source(self) -> "JobCreate":
        if self.source_mode == "reddit_url":
            if not self.reddit_url or not self.reddit_url.strip():
                raise ValueError("A Reddit URL is required.")
        elif not self.source_body or len(self.source_body.strip()) < 20:
            raise ValueError(
                "Manual story text must contain at least 20 characters."
            )

        if not self.use_music:
            self.music_asset = None
        return self


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime

    source_mode: SourceMode
    reddit_url: str | None
    title: str
    status: str
    stage: str
    progress: int
    logs: str
    error: str | None

    script: str | None
    approved_script: str | None

    gameplay_asset: str | None
    music_asset: str | None
    banner_asset: str | None
    use_music: bool
    voice_key: VoiceKey
    playback_speed: float

    output_video: str | None
    narration_file: str | None
    subtitle_file: str | None

    upload_status: str
    platform_url: str | None
    views: int


class ScriptApproval(BaseModel):
    script: str = Field(min_length=20)


class PublicationUpdate(BaseModel):
    upload_status: UploadStatus
    platform_url: str | None = None
    views: int = Field(default=0, ge=0)


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    kind: str
    original_name: str
    stored_path: str
    size_bytes: int


class VoiceRead(BaseModel):
    key: VoiceKey
    name: str


class StatsRead(BaseModel):
    total: int
    queued: int
    running: int
    awaiting_approval: int
    completed: int
    failed: int
    uploaded: int
    total_views: int
