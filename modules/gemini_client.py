import os
import json
import re
import time
import random

from dotenv import load_dotenv
from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from your Streamlit secrets."
    )

client = genai.Client(api_key=API_KEY)


# ============================================================
# GEMINI MODELS
# ============================================================

# Current stable models.
#
# Primary = fast + economical
# Fallback = stronger general-purpose model
#
# Gemini 3.5 Flash-Lite is currently recommended by Google
# for high-throughput / cost-sensitive workloads.

PRIMARY_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODEL = "gemini-3.5-flash"


# ============================================================
# ERROR HELPERS
# ============================================================

def is_temporary_error(error):
    """
    Detect errors where retrying may succeed.
    """

    message = str(error).upper()

    temporary_markers = [
        "503",
        "UNAVAILABLE",
        "500",
        "INTERNAL",
        "502",
        "BAD GATEWAY",
        "504",
        "TIMEOUT",
        "TIMED OUT",
        "CONNECTION RESET",
        "CONNECTION ABORTED",
        "SERVICE UNAVAILABLE",
    ]

    return any(
        marker in message
        for marker in temporary_markers
    )


def is_rate_limit_error(error):
    """
    Detect temporary rate-limit / resource exhaustion errors.
    """

    message = str(error).upper()

    return (
        "429" in message
        or "RESOURCE_EXHAUSTED" in message
        or "RATE LIMIT" in message
        or "RATE_LIMIT" in message
    )


def is_model_not_found(error):
    """
    Detect invalid/unavailable model errors.
    """

    message = str(error).upper()

    return (
        "404" in message
        or "NOT_FOUND" in message
        or "MODEL" in message
        and "NOT AVAILABLE" in message
    )


def readable_error(error):
    """
    Prevent huge API errors from flooding the Streamlit UI.
    """

    message = str(error)

    if len(message) > 1200:
        message = message[:1200] + "..."

    return message


# ============================================================
# GEMINI REQUEST
# ============================================================

def request(
    contents,
    json_mode=False,
    temperature=0.15,
    retries=3
):
    """
    Robust Gemini request.

    Pipeline:

        Gemini 3.5 Flash-Lite
                ↓
        retry temporary errors
                ↓
        Gemini 3.5 Flash
                ↓
        retry temporary errors
                ↓
        clear final error
    """

    models = [
        PRIMARY_MODEL,
        FALLBACK_MODEL
    ]

    last_error = None

    for model_index, model in enumerate(models):

        for attempt in range(retries):

            try:

                # --------------------------------------------
                # Request configuration
                # --------------------------------------------

                config = {
                    "temperature": temperature
                }

                if json_mode:

                    config[
                        "response_mime_type"
                    ] = "application/json"

                # --------------------------------------------
                # Gemini API call
                # --------------------------------------------

                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )

                # --------------------------------------------
                # Validate response
                # --------------------------------------------

                if not response:

                    raise RuntimeError(
                        "Gemini returned no response."
                    )

                text = getattr(
                    response,
                    "text",
                    None
                )

                if not text:

                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return text.strip()

            except Exception as error:

                last_error = error

                # ====================================================
                # MODEL NOT AVAILABLE
                # ====================================================

                if is_model_not_found(error):

                    # Don't waste time retrying a model that
                    # the API project cannot access.
                    break

                # ====================================================
                # RATE LIMIT / TEMPORARY RESOURCE EXHAUSTION
                # ====================================================

                if is_rate_limit_error(error):

                    if attempt < retries - 1:

                        wait_time = (
                            (2 ** attempt) * 3
                            + random.uniform(0.5, 1.5)
                        )

                        time.sleep(wait_time)

                        continue

                    # Current model exhausted.
                    # Move to fallback.
                    break

                # ====================================================
                # TEMPORARY SERVER ERROR
                # ====================================================

                if is_temporary_error(error):

                    if attempt < retries - 1:

                        # Exponential backoff.
                        #
                        # ~2-4 sec
                        # ~4-6 sec
                        # ~8-10 sec

                        wait_time = (
                            (2 ** attempt) * 2
                            + random.uniform(0.5, 1.5)
                        )

                        time.sleep(wait_time)

                        continue

                    # Retries exhausted.
                    break

                # ====================================================
                # NON-RETRYABLE ERROR
                # ====================================================

                raise RuntimeError(
                    f"Gemini request failed using "
                    f"{model}: {readable_error(error)}"
                ) from error

        # --------------------------------------------------------
        # Move to next model.
        # --------------------------------------------------------

        if model_index < len(models) - 1:

            continue

    # ============================================================
    # ALL MODELS FAILED
    # ============================================================

    raise RuntimeError(
        "Gemini is temporarily unavailable. "
        "LectureLens tried the available Gemini models "
        "with retries. "
        f"Last error: {readable_error(last_error)}"
    ) from last_error


# ============================================================
# JSON CLEANING
# ============================================================

def clean_json(text):

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    # Remove ```json
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove ```
    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    # Locate JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end >= 0:

        text = text[
            start:end + 1
        ]

    return text.strip()


# ============================================================
# JSON PARSER
# ============================================================

def parse_json(text):

    cleaned = clean_json(text)

    try:

        return json.loads(cleaned)

    except json.JSONDecodeError:

        # Attempt simple trailing-comma repair
        repaired = re.sub(
            r",\s*([}\]])",
            r"\1",
            cleaned
        )

        try:

            return json.loads(repaired)

        except json.JSONDecodeError as error:

            raise RuntimeError(
                "Gemini returned an invalid study-pack response."
            ) from error


# ============================================================
# STUDY PACK PROMPT
# ============================================================

def build_study_prompt(
    content,
    source_type="lecture"
):

    return f"""
You are LectureLens AI, a university-level AI study engine.

The source is a {source_type}.

Transform the source into a complete,
exam-oriented personal study workspace.

Use ONLY information supported by the supplied source.

Do not invent facts.

You may reorganize and simplify explanations
for better learning while preserving technical accuracy.

Return ONLY valid JSON.

Do not use Markdown.

Do not use code fences.

Do not write anything outside the JSON object.

Use EXACTLY this structure:

{{
    "title": "Clear lecture title",

    "subject": "Subject",

    "difficulty": "Beginner, Intermediate or Advanced",

    "duration_estimate": "Estimated study time",

    "summary": "Detailed overall summary",

    "tldr": "Short last-minute revision summary",

    "key_concepts": [
        "Concept 1",
        "Concept 2"
    ],

    "detailed_notes": [
        {{
            "heading": "Concept heading",
            "explanation": "Detailed explanation",
            "example": "Example if supported by the source"
        }}
    ],

    "definitions": [
        {{
            "term": "Important term",
            "definition": "Clear definition"
        }}
    ],

    "formulas": [
        {{
            "name": "Formula name",
            "formula": "Formula",
            "meaning": "Meaning and application"
        }}
    ],

    "important_points": [
        "Important exam point"
    ],

    "common_mistakes": [
        "Common misunderstanding or mistake"
    ],

    "flashcards": [
        {{
            "question": "Question",
            "answer": "Detailed answer"
        }}
    ],

    "quiz": [
        {{
            "question": "Question",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "correct_answer": "Option A",
            "explanation": "Why this is correct"
        }}
    ],

    "exam_questions": [
        {{
            "question": "Likely university exam question",
            "answer_outline": "Structured answer suitable for exam preparation"
        }}
    ],

    "study_coach": [
        "Personalized study recommendation"
    ],

    "revision_plan": [
        "Step 1",
        "Step 2",
        "Step 3"
    ]
}}

REQUIREMENTS:

Create 6 to 10 detailed note sections.

Create 10 flashcards.

Create 6 quiz questions.

Create 5 exam-oriented questions.

Create useful definitions whenever the source contains terminology.

Create formulas whenever the source contains mathematical
or scientific formulas.

For every formula, explain important variables.

Identify high-priority exam topics.

Include examples when supported by the source.

Include common mistakes related to the concepts.

Make the study coach practical.

Create a short revision plan for examination preparation.

Keep answers detailed enough to be genuinely useful
for university study.

SOURCE CONTENT:

{content}
"""


# ============================================================
# ANALYZE CONTENT
# ============================================================

def analyze_content(
    content,
    source_type="lecture"
):

    if not content or not str(content).strip():

        raise ValueError(
            "No lecture content was received."
        )

    prompt = build_study_prompt(
        content,
        source_type
    )

    raw = request(
        prompt,
        json_mode=True,
        temperature=0.15,
        retries=3
    )

    return parse_json(raw)


# ============================================================
# YOUTUBE
# ============================================================

def analyze_youtube_text(text):

    if not text or not text.strip():

        raise ValueError(
            "The YouTube transcript is empty."
        )

    return analyze_content(
        text,
        source_type="YouTube educational lecture"
    )


# ============================================================
# AUDIO
# ============================================================

def analyze_audio_content(content):

    return analyze_content(
        content,
        source_type="audio lecture"
    )


# ============================================================
# VIDEO
# ============================================================

def analyze_video_content(content):

    return analyze_content(
        content,
        source_type="video lecture"
    )


# ============================================================
# MEDIA → TEXT
# ============================================================

def media_to_text(uploaded, kind):

    prompt = f"""
You are LectureLens AI.

Analyze this {kind} lecture.

Extract the complete educational content needed
for university-level study.

Focus on:

- Main concepts
- Definitions
- Important explanations
- Examples
- Applications
- Formulas
- Technical terminology
- Relationships between concepts
- Exam-relevant information
- Important visual information when available

Clean obvious transcription errors using context.

Do not invent information.

Return detailed educational content as plain text.
"""

    return request(
        [
            uploaded,
            prompt
        ],
        temperature=0.15,
        retries=3
    )


# ============================================================
# STUDY PACK
# ============================================================

def build_study_pack(content):

    return analyze_content(
        content,
        source_type="lecture"
    )