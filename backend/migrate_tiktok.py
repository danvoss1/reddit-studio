from pathlib import Path
import sqlite3

from app.db import Base, engine
import app.models  # noqa: F401


database = Path(
    "data/reddit_studio.sqlite3"
)

if not database.exists():
    print(
        "Database does not exist yet. "
        "Start FastAPI once, then run this migration."
    )
    raise SystemExit(1)


connection = sqlite3.connect(
    database
)

existing_columns = {
    row[1]
    for row in connection.execute(
        "PRAGMA table_info(video_jobs)"
    )
}

migrations = {
    "tiktok_publish_id": (
        "ALTER TABLE video_jobs "
        "ADD COLUMN tiktok_publish_id VARCHAR(128)"
    ),
    "tiktok_status": (
        "ALTER TABLE video_jobs "
        "ADD COLUMN tiktok_status VARCHAR(80)"
    ),
    "tiktok_caption": (
        "ALTER TABLE video_jobs "
        "ADD COLUMN tiktok_caption TEXT"
    ),
    "tiktok_privacy_level": (
        "ALTER TABLE video_jobs "
        "ADD COLUMN tiktok_privacy_level VARCHAR(80)"
    ),
    "tiktok_last_error": (
        "ALTER TABLE video_jobs "
        "ADD COLUMN tiktok_last_error TEXT"
    ),
}

for column, sql in migrations.items():
    if column in existing_columns:
        print(
            f"{column}: already exists"
        )
        continue

    connection.execute(sql)
    print(
        f"{column}: added"
    )

connection.commit()
connection.close()

Base.metadata.create_all(
    bind=engine
)

print(
    "TikTok migration complete."
)
