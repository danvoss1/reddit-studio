from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_ROOT / "data"
JOBS_DIR = DATA_DIR / "jobs"
GAMEPLAY_DIR = DATA_DIR / "assets" / "gameplay"
MUSIC_DIR = DATA_DIR / "assets" / "music"
BANNER_DIR = DATA_DIR / "assets" / "banner"

for folder in (
    DATA_DIR,
    JOBS_DIR,
    GAMEPLAY_DIR,
    MUSIC_DIR,
    BANNER_DIR,
):
    folder.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/reddit_studio.sqlite3"

    frontend_origin: str = "http://localhost:5173"
    local_frontend_url: str = "http://localhost:5173"
    public_frontend_url: str = "https://reddit-studio.vercel.app"

    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"

    elevenlabs_api_key: str = ""
    elevenlabs_model_id: str = "eleven_multilingual_v2"
    elevenlabs_female_voice_id: str = ""
    elevenlabs_male_voice_id: str = ""
    elevenlabs_female_voice_name: str = "Female narrator"
    elevenlabs_male_voice_name: str = "Male narrator"

    playwright_headless: bool = True

    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    tiktok_redirect_uri: str = (
        "https://reddit-studio.vercel.app/auth/tiktok/callback"
    )
    tiktok_token_encryption_key: str = ""
    tiktok_scopes: str = (
        "user.info.basic,video.publish,video.upload"
    )
    tiktok_local_callback_url: str = (
        "http://127.0.0.1:8000/api/tiktok/callback"
    )

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        origins = {
            self.frontend_origin.rstrip("/"),
            self.local_frontend_url.rstrip("/"),
            self.public_frontend_url.rstrip("/"),
        }
        return sorted(origin for origin in origins if origin)

    def voice_id_for_key(self, voice_key: str) -> str:
        voice_ids = {
            "female": self.elevenlabs_female_voice_id,
            "male": self.elevenlabs_male_voice_id,
        }

        voice_id = voice_ids.get(voice_key)

        if not voice_id:
            raise RuntimeError(
                f"No ElevenLabs voice ID configured for '{voice_key}'."
            )

        return voice_id

    def available_voices(self) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []

        if self.elevenlabs_female_voice_id:
            result.append(
                {
                    "key": "female",
                    "name": self.elevenlabs_female_voice_name,
                }
            )

        if self.elevenlabs_male_voice_id:
            result.append(
                {
                    "key": "male",
                    "name": self.elevenlabs_male_voice_name,
                }
            )

        return result

    def validate_tiktok_configuration(self) -> None:
        missing = []

        if not self.tiktok_client_key:
            missing.append("TIKTOK_CLIENT_KEY")

        if not self.tiktok_client_secret:
            missing.append("TIKTOK_CLIENT_SECRET")

        if not self.tiktok_redirect_uri:
            missing.append("TIKTOK_REDIRECT_URI")

        if not self.tiktok_token_encryption_key:
            missing.append("TIKTOK_TOKEN_ENCRYPTION_KEY")

        if missing:
            raise RuntimeError(
                "Missing TikTok configuration: "
                + ", ".join(missing)
            )


settings = Settings()
