import html
import re
import tempfile
from pathlib import Path

import requests
from youtube_transcript_api import YouTubeTranscriptApi

from modules.gemini_client import analyze_youtube_text


# ============================================================
# YOUTUBE URL / VIDEO ID
# ============================================================

def get_video_id(url):
    """
    Extract a YouTube video ID from common YouTube URL formats.
    """

    if not url:
        return None

    url = url.strip()

    patterns = [
        r"(?:youtube\.com/watch\?v=)([^&?#]+)",
        r"(?:youtube\.com/watch\?.*?v=)([^&?#]+)",
        r"(?:youtu\.be/)([^?&#]+)",
        r"(?:youtube\.com/shorts/)([^?&#]+)",
        r"(?:youtube\.com/embed/)([^?&#]+)",
        r"(?:youtube\.com/live/)([^?&#]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)

        if match:
            return match.group(1)

    return None


# ============================================================
# CLEAN TRANSCRIPT
# ============================================================

def clean_transcript_text(text):
    """
    Clean subtitle/transcript text before sending it to Gemini.
    """

    if not text:
        return ""

    text = html.unescape(text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove VTT positioning / formatting
    text = re.sub(r"\{[^}]+\}", " ", text)

    # Remove duplicate whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# METHOD 1
# youtube-transcript-api
# ============================================================

def get_transcript_api(video_id):
    """
    Try youtube-transcript-api first.

    Supports:
    - manually created transcripts
    - automatically generated transcripts
    - multiple languages
    """

    api = YouTubeTranscriptApi()

    language_preferences = [
        "en",
        "en-US",
        "en-GB",
        "hi",
        "hi-IN",
    ]

    # --------------------------------------------------------
    # Attempt 1: direct fetch
    # --------------------------------------------------------

    try:
        transcript = api.fetch(
            video_id,
            languages=language_preferences
        )

        text_parts = []

        for item in transcript:

            if hasattr(item, "text"):
                text_parts.append(item.text)

            elif isinstance(item, dict):
                text_parts.append(
                    item.get("text", "")
                )

        text = " ".join(
            part.strip()
            for part in text_parts
            if part and part.strip()
        )

        text = clean_transcript_text(text)

        if text:
            return text

    except Exception:
        pass

    # --------------------------------------------------------
    # Attempt 2: list all available transcripts
    # --------------------------------------------------------

    try:
        transcript_list = api.list(video_id)

        candidates = list(transcript_list)

        if not candidates:
            raise RuntimeError("No YouTube transcripts available.")

        # Prefer English
        candidates.sort(
            key=lambda item: (
                0
                if getattr(item, "language_code", "").lower()
                in ["en", "en-us", "en-gb"]
                else 1
            )
        )

        for transcript_obj in candidates:

            try:
                fetched = transcript_obj.fetch()

                text_parts = []

                for item in fetched:

                    if hasattr(item, "text"):
                        text_parts.append(item.text)

                    elif isinstance(item, dict):
                        text_parts.append(
                            item.get("text", "")
                        )

                text = " ".join(
                    part.strip()
                    for part in text_parts
                    if part and part.strip()
                )

                text = clean_transcript_text(text)

                if text:
                    return text

            except Exception:
                continue

    except Exception:
        pass

    return None


# ============================================================
# METHOD 2
# yt-dlp subtitle fallback
# ============================================================

def get_transcript_ytdlp(video_url, video_id):
    """
    Fallback transcript extraction using yt-dlp.

    It tries:
    - manually provided subtitles
    - automatically generated subtitles
    - English variants
    """

    try:
        from yt_dlp import YoutubeDL
    except ImportError as error:
        raise RuntimeError(
            "yt-dlp is not installed. "
            "Add yt-dlp to requirements.txt."
        ) from error

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_path = Path(temp_dir)

        output_template = str(
            temp_path / "%(id)s.%(ext)s"
        )

        options = {
            "skip_download": True,

            # Normal subtitles
            "writesubtitles": True,

            # Automatically generated subtitles
            "writeautomaticsub": True,

            # Try multiple English variants
            "subtitleslangs": [
                "en.*",
                "en",
                "en-US",
                "en-GB",
            ],

            # VTT is easy to parse
            "subtitlesformat": "vtt",

            "outtmpl": output_template,

            # Keep the Streamlit UI clean
            "quiet": True,
            "no_warnings": True,

            # Retry network requests
            "retries": 3,
            "fragment_retries": 3,

            # Do not fail the whole extraction because
            # one subtitle track is unavailable
            "ignoreerrors": True,
        }

        try:

            with YoutubeDL(options) as ydl:
                ydl.download([video_url])

        except Exception:
            return None

        # ----------------------------------------------------
        # Search for generated subtitle files
        # ----------------------------------------------------

        subtitle_files = list(
            temp_path.glob("*.vtt")
        )

        if not subtitle_files:
            # Some versions may create another subtitle format
            subtitle_files = list(
                temp_path.glob("*.*")
            )

        # ----------------------------------------------------
        # Prefer English files
        # ----------------------------------------------------

        subtitle_files.sort(
            key=lambda path: (
                0
                if ".en" in path.name.lower()
                else 1
            )
        )

        for subtitle_file in subtitle_files:

            try:

                if subtitle_file.suffix.lower() != ".vtt":
                    continue

                raw_text = subtitle_file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                if not raw_text:
                    continue

                text = parse_vtt(raw_text)

                if text:
                    return text

            except Exception:
                continue

    return None


# ============================================================
# VTT PARSER
# ============================================================

def parse_vtt(vtt_text):
    """
    Convert WebVTT subtitle content into clean plain text.
    """

    if not vtt_text:
        return ""

    lines = vtt_text.splitlines()

    text_parts = []

    previous_text = ""

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Header
        if line.upper().startswith("WEBVTT"):
            continue

        # Metadata / comments
        if line.upper().startswith("NOTE"):
            continue

        if line.upper().startswith("STYLE"):
            continue

        if line.upper().startswith("REGION"):
            continue

        # Subtitle timing line
        if "-->" in line:
            continue

        # Numeric cue identifier
        if re.fullmatch(r"\d+", line):
            continue

        # Remove timestamp tags
        line = re.sub(
            r"<\d{2}:\d{2}:\d{2}\.\d{3}>",
            "",
            line
        )

        line = re.sub(
            r"<\d{2}:\d{2}\.\d{3}>",
            "",
            line
        )

        # Remove HTML/VTT tags
        line = re.sub(
            r"<[^>]+>",
            "",
            line
        )

        # Decode HTML entities
        line = html.unescape(line)

        line = line.strip()

        if not line:
            continue

        # Avoid duplicated consecutive subtitle lines
        if line == previous_text:
            continue

        text_parts.append(line)
        previous_text = line

    text = " ".join(text_parts)

    # Clean whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# MAIN TRANSCRIPT FUNCTION
# ============================================================

def get_transcript(video_id, video_url):
    """
    Robust transcript pipeline.

    Order:

    1. youtube-transcript-api
    2. yt-dlp subtitles
    3. clear error message
    """

    # --------------------------------------------------------
    # METHOD 1
    # --------------------------------------------------------

    transcript = get_transcript_api(video_id)

    if transcript:

        return transcript

    # --------------------------------------------------------
    # METHOD 2
    # --------------------------------------------------------

    transcript = get_transcript_ytdlp(
        video_url,
        video_id
    )

    if transcript:

        return transcript

    # --------------------------------------------------------
    # Nothing worked
    # --------------------------------------------------------

    raise RuntimeError(
        "YouTube is reachable, but LectureLens could not "
        "retrieve captions for this video. "
        "Please try another public educational video "
        "with captions."
    )


# ============================================================
# MAIN URL PROCESSOR
# ============================================================

def analyze_url(url):

    if not url or not url.strip():

        raise ValueError(
            "Please enter a YouTube URL."
        )

    url = url.strip()

    video_id = get_video_id(url)

    if not video_id:

        raise ValueError(
            "Please enter a valid public YouTube URL."
        )

    # --------------------------------------------------------
    # Get transcript
    # --------------------------------------------------------

    transcript = get_transcript(
        video_id,
        url
    )

    if not transcript:

        raise RuntimeError(
            "The YouTube transcript was empty."
        )

    # --------------------------------------------------------
    # Protect Gemini from excessively large input
    # --------------------------------------------------------

    MAX_TRANSCRIPT_LENGTH = 80000

    if len(transcript) > MAX_TRANSCRIPT_LENGTH:

        transcript = transcript[
            :MAX_TRANSCRIPT_LENGTH
        ]

    # --------------------------------------------------------
    # Send transcript to Gemini
    # --------------------------------------------------------

    return analyze_youtube_text(
        transcript
    )