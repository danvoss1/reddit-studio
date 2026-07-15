# Reddit Studio — local full-stack dashboard

A localhost dashboard for turning Reddit story URLs into narrated vertical videos.

## Stack

- Frontend: React, TypeScript, Vite, TanStack Query
- Backend: FastAPI, SQLAlchemy, SQLite
- Media: ElevenLabs timestamps + FFmpeg
- Jobs: local background worker with persisted progress and logs

## Current features

- Paste a Reddit URL and create a job
- Optional direct story title/body input for testing
- Track queued, running, completed, failed, and cancelled jobs
- Live stage, percentage, and logs
- Approve/edit the generated script before ElevenLabs credits are used
- Upload and manage gameplay/music assets
- Render final vertical MP4
- History page
- Record TikTok upload URL/status and manual view counts
- Dashboard statistics
- Download/open generated artifacts through the API

Automatic TikTok publishing and analytics are intentionally a later integration because they require an approved TikTok developer app and account authorization.

## Prerequisites

- Python 3.11+
- Node.js 20+
- FFmpeg and ffprobe available on PATH

Check:

```powershell
python --version
node --version
ffmpeg -version
ffprobe -version
```

## Start backend

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
uvicorn app.main:app --reload --port 8000
```

## Start frontend

Open another VS Code terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Required environment values

For full rendering:

```env
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=
OPENAI_API_KEY=
```

For fetching Reddit URLs through PRAW:

```env
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=windows:reddit-studio:v1.0 (by /u/YOUR_USERNAME)
```

You can test the pipeline without Reddit credentials by selecting **Paste story text manually** in the New Video page.

## Workflow

1. Create job.
2. Backend fetches story.
3. OpenAI rewrites the script.
4. Job pauses at `awaiting_approval`.
5. Review/edit script in the job detail page.
6. Approve.
7. ElevenLabs creates narration and alignment.
8. Subtitles are created.
9. FFmpeg renders the final MP4.
10. Mark it uploaded and record its TikTok URL/views manually.

## Asset folders

Uploaded assets are stored in:

```text
backend/data/assets/gameplay
backend/data/assets/music
```

Job artifacts are stored in:

```text
backend/data/jobs/<job-id>
```

## Notes

This is a local single-user application. The in-process worker is suitable for one machine. A later production version should move rendering to Celery/RQ/Arq with Redis.
