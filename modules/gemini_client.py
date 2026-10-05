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
        "GEMINI_API_KEY is missing from your Streamlit secrets/environment."
    )

client = genai.Client(api_key=API_KEY)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

# You can override these from Streamlit secrets/environment.
#
# Primary:
# GEMINI_MODEL=gemini-2.5-flash
#
# Fallback:
# GEMINI_FALLBACK_MODEL=gemini-2.5-flash-lite

PRIMARY_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

FALLBACK_MODEL = os.getenv(
    "GEMINI_FALLBACK_MODEL",
    "gemini-2.5-flash-lite"
)


# ============================================================
# HELPERS
# ============================================================

def is_temporary_error(error):
    """
    Detect temporary Gemini/API/network failures.
    """

    message = str(error).upper()

    temporary_markers = [
        "503",
        "UNAVAILABLE",
        "500",
        "INTERNAL",
        "502",
        "504",
        "429",
        "RESOURCE_EXHAUSTED",
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


def is_quota_error(error):
    """
    Detect errors where retrying the same request is unlikely to help.
    """

    message = str(error).upper()

    quota_markers = [
        "RESOURCE_EXHAUSTED",
        "QUOTA",
        "RATE LIMIT",
        "RATE_LIMIT",
    ]

    return any(
        marker in message
        for marker in quota_markers
    )


def clean_error_message(error):
    """
    Keep UI error messages readable.
    """

    message = str(error)

    if len(message) > 1000:
        message = message[:1000] + "..."

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

    Strategy:

    1. Try primary model.
    2. Retry temporary failures with exponential backoff.
    3. If primary model remains unavailable, try fallback model.
    4. Retry fallback model.
    5. Return the first successful response.
    """

    models = []

    # Primary model
    if PRIMARY_MODEL:
        models.append(PRIMARY_MODEL)

    # Fallback model
    if (
        FALLBACK_MODEL
        and FALLBACK_MODEL not in models
    ):
        models.append(FALLBACK_MODEL)

    last_error = None

    for model_index, model in enumerate(models):

        for attempt in range(retries):

            try:

                config = {
                    "temperature": temperature
                }

                if json_mode:

                    config["response_mime_type"] = (
                        "application/json"
                    )

                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )

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

                # ------------------------------------------------
                # QUOTA / RATE LIMIT
                # ------------------------------------------------

                if is_quota_error(error):

                    # If it is a temporary 429, retry.
                    # Otherwise move to fallback model.
                    message = str(error).upper()

                    if (
                        "429" not in message
                        and "RESOURCE_EXHAUSTED" not in message
                    ):
                        raise RuntimeError(
                            "Gemini quota is exhausted. "
                            "Please use a Gemini API project "
                            "with available quota."
                        ) from error

                # ------------------------------------------------
                # TEMPORARY ERROR
                # ------------------------------------------------

                if is_temporary_error(error):

                    # We have exhausted retries for this model.
                    if attempt == retries - 1:
                        break

                    # Exponential backoff with jitter.
                    #
                    # Attempt 1: ~2-4 sec
                    # Attempt 2: ~4-6 sec
                    # Attempt 3: ~8-10 sec
                    wait_time = (
                        (2 ** attempt) * 2
                        + random.uniform(0.5, 1.5)
                    )

                    time.sleep(wait_time)

                    continue

                # ------------------------------------------------
                # NON-TEMPORARY ERROR
                # ------------------------------------------------

                raise RuntimeError(
                    f"Gemini request failed "
                    f"using {model}: "
                    f"{clean_error_message(error)}"
                ) from error

        # --------------------------------------------------------
        # Primary model failed.
        #
        # Move automatically to fallback model.
        # --------------------------------------------------------

        if model_index < len(models) - 1:

            continue

    # ============================================================
    # EVERYTHING FAILED
    # ============================================================

    raise RuntimeError(
        "Gemini is temporarily unavailable. "
        "LectureLens tried multiple retries and a fallback model. "
        f"Last error: {clean_error_message(last_error)}"
    ) from last_error


# ============================================================
# JSON CLEANING
# ============================================================

def clean_json(text):

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

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

    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end >= 0:
        text = text[start:end + 1]

    return text.strip()


# ============================================================
# JSON PARSER
# ============================================================

def parse_json(text):

    cleaned = clean_json(text)

    try:

        return json.loads(cleaned)

    except json.JSONDecodeError:

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
# STUDY PROMPT
# ============================================================

def build_study_prompt(
    content,
    source_type="lecture"
):

    return f"""
You are LectureLens AI, a university-level AI study engine.

The source is a {source_type}.

Your task is to transform the source into a COMPLETE,
exam-oriented personal study workspace.

Use ONLY information supported by the supplied source.

Do not invent facts.

You may reorganize, simplify and explain concepts
for better learning while preserving technical accuracy.

Return ONLY valid JSON.

Do not use Markdown.

Do not use code fences.

Do not write anything outside the JSON object.

Use exactly this structure:

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

Requirements:

Create 6 to 10 detailed note sections.

Create 10 flashcards.

Create 6 quiz questions.

Create 5 exam-oriented questions.

Create useful definitions whenever the source contains terminology.

Create formulas whenever the source contains mathematical or scientific formulas.

For every formula, explain what each important variable means.

Identify high-priority exam topics.

Include examples when supported by the source.

Include common mistakes based on the concepts in the source.

Make the study coach practical.

Create a short revision plan for someone preparing for an examination.

Keep answers detailed enough to be genuinely useful for university study.

SOURCE CONTENT:

{content}
"""


# ============================================================
# CONTENT ANALYSIS
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