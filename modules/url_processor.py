import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from modules.gemini_client import analyze_youtube_text


def get_video_id(url):

    patterns = [
        r"(?:youtube\.com/watch\?v=)([^&]+)",
        r"(?:youtu\.be/)([^?&]+)",
        r"(?:youtube\.com/shorts/)([^?&]+)",
        r"(?:youtube\.com/embed/)([^?&]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            url
        )

        if match:
            return match.group(1)

    return None


def get_transcript(video_id):

    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9"
    })

    try:

        response = session.get(
            f"https://www.youtube.com/watch?v={video_id}",
            timeout=15
        )

        response.raise_for_status()

    except requests.RequestException as error:

        raise RuntimeError(
            f"Could not connect to YouTube: {error}"
        ) from error

    api = YouTubeTranscriptApi()

    transcript = None

    try:

        transcript = api.fetch(
            video_id,
            languages=[
                "en",
                "en-US",
                "en-GB"
            ]
        )

    except Exception:

        try:

            transcript = api.fetch(
                video_id
            )

        except Exception as error:

            raise RuntimeError(
                "YouTube is reachable, but an accessible "
                "transcript was not found for this video. "
                "Please use a public educational video with captions."
            ) from error

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

    if not text:
        raise RuntimeError(
            "The YouTube transcript was empty."
        )

    return text


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

    transcript = get_transcript(
        video_id
    )

    if len(transcript) > 80000:
        transcript = transcript[:80000]

    return analyze_youtube_text(
        transcript
    )