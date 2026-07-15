from pathlib import Path
import sqlite3

database = Path("data/reddit_studio.sqlite3")
if not database.exists():
    print("No database found; start FastAPI once first.")
    raise SystemExit(0)

connection = sqlite3.connect(database)
columns = {row[1] for row in connection.execute("PRAGMA table_info(video_jobs)")}

migrations = {
    "voice_key": (
        "ALTER TABLE video_jobs "
        "ADD COLUMN voice_key VARCHAR(30) NOT NULL DEFAULT 'female'"
    ),
    "playback_speed": (
        "ALTER TABLE video_jobs "
        "ADD COLUMN playback_speed FLOAT NOT NULL DEFAULT 1.2"
    ),
    "banner_asset": (
        "ALTER TABLE video_jobs ADD COLUMN banner_asset TEXT"
    ),
}

for name, sql in migrations.items():
    if name in columns:
        print(f"{name}: already exists")
    else:
        connection.execute(sql)
        print(f"{name}: added")

connection.commit()
connection.close()
print("Migration complete.")
