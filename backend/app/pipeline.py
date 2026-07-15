from __future__ import annotations

import base64
import json
import random
import re
import shutil
import subprocess
import traceback
import textwrap
from pathlib import Path
from threading import Lock, Thread

import requests
from openai import OpenAI
from playwright.sync_api import (
    Browser,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)
from sqlalchemy.orm import Session

from .config import JOBS_DIR, settings
from .db import SessionLocal
from .models import Asset, VideoJob


_worker_lock = Lock()
_running_jobs: set[str] = set()


# ---------------------------------------------------------------------------
# Database/job helpers
# ---------------------------------------------------------------------------


def append_log(job: VideoJob, message: str) -> None:
    """Append a line to a job's persisted log."""

    cleaned = message.rstrip()

    if not cleaned:
        return

    job.logs = f"{job.logs or ''}{cleaned}\n"

    # Prevent the database field from growing indefinitely.
    job.logs = job.logs[-50_000:]


def update_job(
    db: Session,
    job: VideoJob,
    stage: str,
    progress: int,
    status: str = "running",
    log: str | None = None,
) -> None:
    """Update and persist the visible state of a job."""

    job.stage = stage
    job.progress = max(0, min(progress, 100))
    job.status = status

    if log:
        append_log(job, log)

    db.commit()
    db.refresh(job)


def job_was_cancelled(db: Session, job_id: str) -> bool:
    """Check the latest persisted cancellation state."""

    db.expire_all()
    job = db.get(VideoJob, job_id)

    return job is None or job.status == "cancelled"


# ---------------------------------------------------------------------------
# Reddit extraction with Playwright
# ---------------------------------------------------------------------------


def normalize_reddit_url(url: str) -> str:
    url = url.strip()

    if not url.startswith(("https://", "http://")):
        raise RuntimeError(
            "The Reddit URL must begin with http:// or https://."
        )

    lowered = url.lower()

    if "reddit.com" not in lowered and "redd.it" not in lowered:
        raise RuntimeError(
            "The supplied URL does not appear to be a Reddit URL."
        )

    return url


def dismiss_reddit_dialogs(page: Page) -> None:
    """Try to close cookie, login and app-promotion dialogs."""

    button_labels = [
        "Accept all",
        "Accept",
        "Continue",
        "I agree",
        "Close",
        "Not now",
        "Maybe later",
        "Decline",
    ]

    for label in button_labels:
        try:
            button = page.get_by_role(
                "button",
                name=label,
                exact=False,
            )

            if button.count() > 0 and button.first.is_visible():
                button.first.click(timeout=1_500)
        except Exception:
            continue


def clean_extracted_text(text: str) -> str:
    """Remove common Reddit interface text from extracted content."""

    text = text.replace("\u200b", "")
    text = re.sub(r"\r\n?", "\n", text)

    unwanted_line_patterns = [
        r"^upvote$",
        r"^downvote$",
        r"^comment$",
        r"^share$",
        r"^award$",
        r"^save$",
        r"^follow$",
        r"^reply$",
        r"^sort by.*$",
        r"^view all comments.*$",
        r"^open app$",
        r"^continue in app$",
        r"^join$",
        r"^log in$",
        r"^sign up$",
    ]

    cleaned_lines: list[str] = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if any(
            re.match(pattern, line, flags=re.IGNORECASE)
            for pattern in unwanted_line_patterns
        ):
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_meta_content(page: Page, selector: str) -> str | None:
    try:
        locator = page.locator(selector)

        if locator.count() == 0:
            return None

        value = locator.first.get_attribute("content")

        if value and value.strip():
            return value.strip()
    except Exception:
        return None

    return None


def extract_title(page: Page) -> str:
    """Extract a Reddit post title from several possible layouts."""

    text_selectors = [
        "shreddit-post h1",
        'shreddit-post [slot="title"]',
        '[data-testid="post-title"]',
        '[data-post-click-location="title"]',
        "main h1",
        "article h1",
        "h1",
    ]

    for selector in text_selectors:
        try:
            locator = page.locator(selector)

            if locator.count() == 0:
                continue

            for index in range(min(locator.count(), 5)):
                value = locator.nth(index).inner_text(
                    timeout=2_000
                )

                if value and value.strip():
                    return clean_extracted_text(value)
        except Exception:
            continue

    meta_title = extract_meta_content(
        page,
        'meta[property="og:title"]',
    )

    if meta_title:
        return re.sub(
            r"\s*[-|:]\s*Reddit.*$",
            "",
            meta_title,
            flags=re.IGNORECASE,
        ).strip()

    page_title = page.title().strip()

    if page_title:
        page_title = re.sub(
            r"\s*[-|:]\s*Reddit.*$",
            "",
            page_title,
            flags=re.IGNORECASE,
        ).strip()

        if page_title:
            return page_title

    return "Untitled Reddit story"


def extract_body_from_locator(page: Page, selector: str) -> str | None:
    try:
        locator = page.locator(selector)

        if locator.count() == 0:
            return None

        for index in range(min(locator.count(), 8)):
            item = locator.nth(index)

            try:
                text = item.inner_text(timeout=3_000)
            except Exception:
                continue

            text = clean_extracted_text(text)

            if len(text) >= 30:
                return text
    except Exception:
        return None

    return None


def extract_post_body(page: Page) -> str:
    """Extract the self-post text from old or new Reddit layouts."""

    selectors = [
        'shreddit-post [slot="text-body"]',
        'shreddit-post div[slot="text-body"]',
        '[data-post-click-location="text-body"]',
        '[data-testid="post-content"]',
        '[data-testid="post-container"] [data-click-id="text"]',
        '[data-click-id="text"]',
        "article [slot='text-body']",
        '[id^="t3_"] .md',
        ".usertext-body .md",
    ]

    for selector in selectors:
        body = extract_body_from_locator(page, selector)

        if body:
            return body

    # Reddit often embeds the post in JSON-LD.
    try:
        json_ld_nodes = page.locator(
            'script[type="application/ld+json"]'
        )

        for index in range(json_ld_nodes.count()):
            raw = json_ld_nodes.nth(index).text_content()

            if not raw:
                continue

            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                continue

            records = parsed if isinstance(parsed, list) else [parsed]

            for record in records:
                if not isinstance(record, dict):
                    continue

                for key in (
                    "articleBody",
                    "text",
                    "description",
                ):
                    value = record.get(key)

                    if isinstance(value, str):
                        value = clean_extracted_text(value)

                        if len(value) >= 30:
                            return value
    except Exception:
        pass

    for selector in (
        'meta[property="og:description"]',
        'meta[name="description"]',
    ):
        description = extract_meta_content(page, selector)

        if description:
            description = clean_extracted_text(description)

            if len(description) >= 30:
                return description

    raise RuntimeError(
        "The Reddit post body could not be extracted. "
        "The post may be deleted, private, age-restricted, "
        "image-only, or Reddit may have changed its page structure."
    )


def fetch_reddit(url: str) -> tuple[str, str]:
    """Load a Reddit post in Chromium and return title and body."""

    url = normalize_reddit_url(url)

    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(
            headless=settings.playwright_headless,
        )

        context = browser.new_context(
            viewport={
                "width": 1440,
                "height": 1200,
            },
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )

        page = context.new_page()

        try:
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=45_000,
            )

            dismiss_reddit_dialogs(page)

            try:
                page.wait_for_load_state(
                    "networkidle",
                    timeout=10_000,
                )
            except PlaywrightTimeoutError:
                # Reddit commonly keeps network requests open.
                pass

            # Give dynamic web components a moment to render.
            page.wait_for_timeout(2_000)

            title = extract_title(page)
            body = extract_post_body(page)

            if len(body.strip()) < 20:
                raise RuntimeError(
                    "Reddit returned a post body that was too short."
                )

            return title.strip(), body.strip()

        except PlaywrightTimeoutError as exc:
            raise RuntimeError(
                "Reddit took too long to load."
            ) from exc

        finally:
            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# AI script rewriting
# ---------------------------------------------------------------------------


def clean_story_without_ai(title: str, body: str) -> str:
    text = f"{title}\n\n{body}"

    text = re.sub(
        r"https?://\S+",
        "",
        text,
    )

    text = re.sub(
        r"(?im)^\s*edit\s*\d*\s*:.*$",
        "",
        text,
    )

    text = re.sub(
        r"(?im)^\s*update\s*\d*\s*:.*$",
        "",
        text,
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()[:7_000]


def rewrite_story(title: str, body: str) -> str:
    """Rewrite a story into a narration-friendly script."""

    if not settings.openai_api_key:
        return clean_story_without_ai(title, body)

    client = OpenAI(
        api_key=settings.openai_api_key,
    )

    instructions = """
You edit user-submitted stories for spoken short-form video.

Rules:
- Preserve the factual meaning.
- Do not invent events, dialogue, motives, or outcomes.
- Remove usernames, links, edit notes and identifying details.
- Do not present allegations as independently verified facts.
- Start with a strong but truthful opening hook.
- Use natural spoken English.
- Prefer short, clear sentences.
- Preserve the conflict, escalation and outcome.
- Remove filler and repetition.
- Do not include headings, markdown, hashtags or stage directions.
- Return only the narration script.
""".strip()

    input_text = f"""
TITLE:
{title}

STORY:
{body}
""".strip()

    response = client.responses.create(
        model=settings.openai_model,
        instructions=instructions,
        input=input_text,
    )

    script = response.output_text.strip()

    if len(script) < 20:
        raise RuntimeError(
            "OpenAI returned an empty or unusably short script."
        )

    return script


# ---------------------------------------------------------------------------
# ElevenLabs narration
# ---------------------------------------------------------------------------


def create_speech(
    text: str,
    voice_key: str,
    audio_path: Path,
    alignment_path: Path,
) -> dict:
    """Create speech and character timing data with ElevenLabs."""

    if not settings.elevenlabs_api_key:
        raise RuntimeError(
            "ELEVENLABS_API_KEY is missing."
        )

    voice_id = settings.voice_id_for_key(voice_key)

    url = (
        "https://api.elevenlabs.io/v1/"
        f"text-to-speech/{voice_id}/with-timestamps"
    )

    response = requests.post(
        url,
        headers={
            "xi-api-key": settings.elevenlabs_api_key,
            "Content-Type": "application/json",
        },
        params={
            "output_format": "mp3_44100_128",
        },
        json={
            "text": text,
            "model_id": settings.elevenlabs_model_id,
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.75,
                "style": 0.25,
                "use_speaker_boost": True,
            },
        },
        timeout=240,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text

        raise RuntimeError(
            f"ElevenLabs request failed: {detail}"
        ) from exc

    data = response.json()

    audio_base64 = data.get("audio_base64")

    alignment = (
        data.get("normalized_alignment")
        or data.get("alignment")
    )

    if not audio_base64:
        raise RuntimeError(
            "ElevenLabs returned no audio data."
        )

    if not alignment:
        raise RuntimeError(
            "ElevenLabs returned no timestamp alignment."
        )

    audio_path.write_bytes(
        base64.b64decode(audio_base64)
    )

    alignment_path.write_text(
        json.dumps(
            alignment,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return alignment


# ---------------------------------------------------------------------------
# Subtitle creation
# ---------------------------------------------------------------------------


def alignment_to_words(
    alignment: dict,
) -> list[tuple[str, float, float]]:
    characters = alignment.get("characters")
    starts = alignment.get(
        "character_start_times_seconds"
    )
    ends = alignment.get(
        "character_end_times_seconds"
    )

    if not characters or not starts or not ends:
        raise RuntimeError(
            "The ElevenLabs alignment format was incomplete."
        )

    words: list[tuple[str, float, float]] = []

    current_characters: list[str] = []
    current_start: float | None = None
    current_end: float | None = None

    def flush_word() -> None:
        nonlocal current_characters
        nonlocal current_start
        nonlocal current_end

        text = "".join(current_characters).strip()

        if (
            text
            and current_start is not None
            and current_end is not None
        ):
            words.append(
                (
                    text,
                    float(current_start),
                    float(current_end),
                )
            )

        current_characters = []
        current_start = None
        current_end = None

    for character, start, end in zip(
        characters,
        starts,
        ends,
    ):
        if str(character).isspace():
            flush_word()
            continue

        if current_start is None:
            current_start = float(start)

        current_characters.append(str(character))
        current_end = float(end)

    flush_word()

    return words


def ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = seconds % 60

    return (
        f"{hours}:"
        f"{minutes:02d}:"
        f"{remaining_seconds:05.2f}"
    )


def escape_ass_text(text: str) -> str:
    text = text.replace("\\", r"\\")
    text = text.replace("{", r"\{")
    text = text.replace("}", r"\}")
    text = text.replace("\n", r"\N")

    return text


def alignment_to_ass(
    alignment: dict,
    output_path: Path,
    font_name: str = "Montserrat ExtraBold",
    font_size: int = 86,
) -> None:
    words = alignment_to_words(alignment)
    if not words:
        raise RuntimeError("No subtitle words could be generated.")

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H70000000,-1,0,0,0,100,100,0,0,1,8,2,5,50,50,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [header]
    for word, start, end in words:
        text = escape_ass_text(word)
        lines.append(
            "Dialogue: "
            f"0,{ass_time(start)},{ass_time(end)},"
            "Default,,0,0,0,,"
            f"{{\\an5\\pos(540,850)}}{text}\n"
        )

    output_path.write_text("".join(lines), encoding="utf-8-sig")

def ffmpeg_escape_path(path: Path) -> str:
    return (
        str(path.resolve())
        .replace("\\", "/")
        .replace(":", r"\:")
        .replace("'", r"\'")
    )


# ---------------------------------------------------------------------------
# Assets and FFmpeg
# ---------------------------------------------------------------------------


def media_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    value = result.stdout.strip()

    if not value:
        raise RuntimeError(
            f"Could not determine media duration: {path.name}"
        )

    return float(value)


def choose_asset(
    db: Session,
    kind: str,
    requested_id: str | None,
    required: bool = True,
) -> Path | None:
    """Select a requested asset, choose one randomly, or return None."""

    if requested_id:
        asset = db.get(Asset, requested_id)

        if not asset:
            raise RuntimeError(
                f"The selected {kind} asset does not exist."
            )

        if asset.kind != kind:
            raise RuntimeError(
                f"The selected asset is not a {kind} asset."
            )

        path = Path(asset.stored_path)

        if not path.exists():
            raise RuntimeError(
                f"The selected {kind} file no longer exists."
            )

        return path

    assets = (
        db.query(Asset)
        .filter(Asset.kind == kind)
        .all()
    )

    existing_paths = [
        Path(asset.stored_path)
        for asset in assets
        if Path(asset.stored_path).exists()
    ]

    if not existing_paths:
        if required:
            raise RuntimeError(
                f"No {kind} assets have been uploaded."
            )
        return None

    return random.choice(existing_paths)

def render_video(
    gameplay: Path,
    narration: Path,
    subtitles: Path,
    output: Path,
    title_file: Path,
    speed: float,
    music: Path | None = None,
    banner: Path | None = None,
) -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg/ffprobe is not available on PATH.")

    narration_duration = media_duration(narration)
    final_duration = narration_duration / speed
    gameplay_duration = media_duration(gameplay)
    start = random.uniform(
        0.0, max(0.0, gameplay_duration - narration_duration)
    )

    sub_path = ffmpeg_escape_path(subtitles)
    title_path = ffmpeg_escape_path(title_file)

    font_file = Path(
        r"C:\Users\dvoss\AppData\Local\Microsoft\Windows\Fonts\Montserrat-VariableFont_wght.ttf"
    )

    if not font_file.exists():
        raise RuntimeError(
            "Montserrat font file was not found."
    )

    font_path = ffmpeg_escape_path(font_file)

    command = ["ffmpeg", "-y"]
    if gameplay_duration < narration_duration:
        command += ["-stream_loop", "-1"]

    command += [
        "-ss", f"{start:.3f}",
        "-i", str(gameplay),
        "-i", str(narration),
    ]

    next_index = 2
    music_index: int | None = None
    banner_index: int | None = None

    if music:
        music_index = next_index
        next_index += 1
        command += ["-stream_loop", "-1", "-i", str(music)]

    if banner:
        banner_index = next_index
        command += ["-loop", "1", "-i", str(banner)]

    filters = [
        "[0:v]"
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,fps=30,"
        f"subtitles='{sub_path}'[base]"
    ]

    video_label = "base"

    if banner and banner_index is not None:
        source_banner_duration = 10.0 * speed

        filters += [
            f"[{banner_index}:v]"
            "scale=900:350:force_original_aspect_ratio=decrease[banner]",
            f"[{video_label}][banner]"
            "overlay=x=(W-w)/2:y=(H-h)/2:"
            f"enable='between(t,0,{source_banner_duration})'[with_banner]",
            "[with_banner]"
            "drawtext="
            f"textfile='{title_path}':"
            f"fontfile='{font_path}':"
            "fontcolor=white:fontsize=60:"
            "borderw=4:bordercolor=black:"
            "line_spacing=8:"
            "x=(w-text_w)/2:y=(h-text_h)/2:"
            f"enable='between(t,0,{source_banner_duration})'[titled]",
        ]
        video_label = "titled"

    filters += [
        f"[{video_label}]setpts=PTS/{speed}[video]",
        f"[1:a]atempo={speed},volume=1.0,aresample=async=1[voice]",
    ]

    if music and music_index is not None:
        filters += [
            f"[{music_index}:a]volume=0.08,"
            f"atrim=duration={final_duration},aresample=async=1[music]",
            "[voice][music]"
            "amix=inputs=2:duration=first:dropout_transition=2[audio]",
        ]
    else:
        filters.append("[voice]anull[audio]")

    command += [
        "-filter_complex", ";".join(filters),
        "-map", "[video]",
        "-map", "[audio]",
        "-t", f"{final_duration:.3f}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(output),
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg rendering failed:\n"
            + (result.stderr[-8000:] if result.stderr else "Unknown error")
        )


# ---------------------------------------------------------------------------
# Pipeline phases
# ---------------------------------------------------------------------------


def process_until_approval(job_id: str) -> None:
    """
    Retrieve the story and preserve its complete text exactly.

    The pipeline then pauses so the user can review the full story
    before ElevenLabs credits are consumed.
    """

    db = SessionLocal()

    try:
        job = db.get(VideoJob, job_id)

        if job is None:
            return

        if job.status == "cancelled":
            return

        update_job(
            db=db,
            job=job,
            stage="Reading source",
            progress=10,
            status="running",
            log="Reading the story source.",
        )

        if job.source_mode == "reddit_url":
            if not job.reddit_url:
                raise RuntimeError(
                    "No Reddit URL was supplied."
                )

            title, body = fetch_reddit(job.reddit_url)

            append_log(
                job,
                "Reddit story extracted successfully.",
            )

        elif job.source_mode == "manual":
            title = (
                job.source_title
                or "Manual story"
            )

            body = (
                job.source_body
                or ""
            )

            if len(body.strip()) < 20:
                raise RuntimeError(
                    "The manually supplied story is too short."
                )

        else:
            raise RuntimeError(
                f"Unsupported source mode: {job.source_mode}"
            )

        # Store the source information in the database.
        job.title = title
        job.source_title = title
        job.source_body = body

        db.commit()
        db.refresh(job)

        if job_was_cancelled(db, job_id):
            return

        update_job(
            db=db,
            job=job,
            stage="Preparing original story",
            progress=28,
            status="running",
            log=(
                "Preparing the complete original story "
                "without shortening or rewriting it."
            ),
        )

        # Preserve the entire story.
        #
        # strip() only removes whitespace at the very beginning
        # and end. It does not summarize or rewrite the story.
        script_text = body.strip()

        if len(script_text) < 20:
            raise RuntimeError(
                "The extracted story text is missing or too short."
            )

        # The VideoJob object receives the text.
        # Do not write script_text.script or script.script.
        job.script = script_text
        job.approved_script = None

        update_job(
            db=db,
            job=job,
            stage="Waiting for script approval",
            progress=38,
            status="awaiting_approval",
            log=(
                "The complete original story is ready. "
                "Review it and approve it in the dashboard."
            ),
        )

    except Exception as exc:
        job = db.get(VideoJob, job_id)

        if job is not None:
            job.status = "failed"
            job.stage = "Failed"
            job.error = str(exc)

            append_log(
                job,
                traceback.format_exc(),
            )

            db.commit()

    finally:
        db.close()

        with _worker_lock:
            _running_jobs.discard(job_id)


def process_after_approval(job_id: str) -> None:
    """Generate narration, subtitles, banner overlay and final video."""

    db = SessionLocal()

    try:
        job = db.get(VideoJob, job_id)

        if not job or job.status == "cancelled":
            return

        script = (
            job.approved_script
            or job.script
            or ""
        ).strip()

        if len(script) < 20:
            raise RuntimeError(
                "The approved script is missing or too short."
            )

        work_directory = JOBS_DIR / job.id
        work_directory.mkdir(parents=True, exist_ok=True)

        source_file = work_directory / "source.json"
        script_file = work_directory / "script.txt"
        audio_file = work_directory / "narration.mp3"
        alignment_file = work_directory / "alignment.json"
        subtitle_file = work_directory / "subtitles.ass"
        title_file = work_directory / "banner-title.txt"
        output_file = work_directory / "final.mp4"

        source_file.write_text(
            json.dumps(
                {
                    "title": job.title,
                    "reddit_url": job.reddit_url,
                    "source_mode": job.source_mode,
                    "voice_key": job.voice_key,
                    "playback_speed": job.playback_speed,
                    "banner_asset": job.banner_asset,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        script_file.write_text(script, encoding="utf-8")

        # Wrap long titles so they remain inside a typical 900 x 350 banner.
        wrapped_title = "\n".join(
            textwrap.wrap(
                job.title.strip(),
                width=32,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
        wrapped_title = "\n".join(
            textwrap.wrap(
                job.title,
                width=32,
                max_lines=4,
                placeholder="…",
            )
        )

        title_file.write_text(
            wrapped_title,
            encoding="utf-8",
        )

        update_job(
            db=db,
            job=job,
            stage="Generating ElevenLabs narration",
            progress=48,
            log=(
                "Generating narration with the "
                f"'{job.voice_key}' voice."
            ),
        )

        alignment = create_speech(
            text=script,
            voice_key=job.voice_key,
            audio_path=audio_file,
            alignment_path=alignment_file,
        )

        job.narration_file = str(audio_file)
        db.commit()

        if job_was_cancelled(db, job_id):
            return

        update_job(
            db=db,
            job=job,
            stage="Creating subtitles",
            progress=65,
            log="Creating centered, one-word subtitles.",
        )

        alignment_to_ass(
            alignment=alignment,
            output_path=subtitle_file,
            font_name="Montserrat ExtraBold",
            font_size=86,
        )

        job.subtitle_file = str(subtitle_file)
        db.commit()

        if job_was_cancelled(db, job_id):
            return

        update_job(
            db=db,
            job=job,
            stage="Selecting media",
            progress=72,
            log="Selecting gameplay, music and banner assets.",
        )

        gameplay = choose_asset(
            db=db,
            kind="gameplay",
            requested_id=job.gameplay_asset,
            required=True,
        )
        assert gameplay is not None

        music: Path | None = None
        if job.use_music:
            music = choose_asset(
                db=db,
                kind="music",
                requested_id=job.music_asset,
                required=True,
            )

        banner: Path | None = None

        if job.banner_asset:
            banner = choose_asset(
                db=db,
                kind="banner",
                requested_id=job.banner_asset,
                required=True,
            )
        

        append_log(job, f"Gameplay selected: {gameplay.name}")
        append_log(
            job,
            f"Music selected: {music.name}"
            if music
            else "Rendering without background music.",
        )
        append_log(
            job,
            f"Banner selected: {banner.name}"
            if banner
            else "Rendering without an opening banner.",
        )
        db.commit()

        if job_was_cancelled(db, job_id):
            return

        update_job(
            db=db,
            job=job,
            stage="Rendering video",
            progress=78,
            log=(
                "Starting FFmpeg rendering at "
                f"{job.playback_speed:.2f}x speed."
            ),
        )

        render_video(
            gameplay=gameplay,
            narration=audio_file,
            subtitles=subtitle_file,
            output=output_file,
            title_file=title_file,
            speed=job.playback_speed,
            music=music,
            banner=banner,
        )

        job.output_video = str(output_file)

        update_job(
            db=db,
            job=job,
            stage="Completed",
            progress=100,
            status="completed",
            log="The final video was created successfully.",
        )

    except Exception as exc:
        job = db.get(VideoJob, job_id)

        if job:
            job.status = "failed"
            job.stage = "Failed"
            job.error = str(exc)
            append_log(job, traceback.format_exc())
            db.commit()

    finally:
        db.close()

        with _worker_lock:
            _running_jobs.discard(job_id)


# ---------------------------------------------------------------------------
# Worker launcher
# ---------------------------------------------------------------------------


def start_job(
    job_id: str,
    phase: str = "prepare",
) -> bool:
    """
    Start one pipeline phase in a background thread.

    phase:
    - prepare: fetch source and create script
    - render: create narration, subtitles and final video
    """

    with _worker_lock:
        if job_id in _running_jobs:
            return False

        _running_jobs.add(job_id)

    if phase == "prepare":
        target = process_until_approval
    elif phase == "render":
        target = process_after_approval
    else:
        with _worker_lock:
            _running_jobs.discard(job_id)

        raise ValueError(
            f"Unknown pipeline phase: {phase}"
        )

    worker = Thread(
        target=target,
        args=(job_id,),
        daemon=True,
        name=f"reddit-studio-{phase}-{job_id}",
    )

    worker.start()

    return True