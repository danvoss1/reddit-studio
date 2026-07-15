from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_ROOT / "data"
JOBS_DIR = DATA_DIR / "jobs"
GAMEPLAY_DIR = DATA_DIR / "assets" / "gameplay"
MUSIC_DIR = DATA_DIR / "assets" / "music"
BANNER_DIR = DATA_DIR / "assets" / "banner"

for folder in (DATA_DIR, JOBS_DIR, GAMEPLAY_DIR, MUSIC_DIR, BANNER_DIR):
    folder.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/reddit_studio.sqlite3"
    frontend_origin: str = "http://localhost:5173"

    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"

    elevenlabs_api_key: str = ""
    elevenlabs_model_id: str = "eleven_multilingual_v2"
    elevenlabs_female_voice_id: str = ""
    elevenlabs_male_voice_id: str = ""
    elevenlabs_female_voice_name: str = "Female narrator"
    elevenlabs_male_voice_name: str = "Male narrator"

    playwright_headless: bool = True

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

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
            result.append({
                "key": "female",
                "name": self.elevenlabs_female_voice_name,
            })
        if self.elevenlabs_male_voice_id:
            result.append({
                "key": "male",
                "name": self.elevenlabs_male_voice_name,
            })
        return result


settings = Settings()
