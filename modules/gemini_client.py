import os
import json
import re
import time
import random
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from your .env file.")

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=API_KEY)


def request(contents, json_mode=False, temperature=0.15, retries=3):

    last_error = None

    for attempt in range(retries):

        try:
            config = {
                "temperature": temperature
            }

            if json_mode:
                config["response_mime_type"] = "application/json"

            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=config
            )

            if not response or not response.text:
                raise RuntimeError("Gemini returned an empty response.")

            return response.text.strip()

        except Exception as error:

            last_error = error
            message = str(error).upper()

            if "429" in message or "RESOURCE_EXHAUSTED" in message:

                raise RuntimeError(
                    "Gemini quota is exhausted for this project. "
                    "Please use a project with available Gemini quota "
                    "or wait for the quota to reset."
                ) from error

            temporary_error = any(
                item in message
                for item in [
                    "503",
                    "UNAVAILABLE",
                    "500",
                    "INTERNAL",
                    "10053",
                    "CONNECTION ABORTED",
                    "CONNECTION RESET",
                    "TIMEOUT"
                ]
            )

            if not temporary_error or attempt == retries - 1:
                raise RuntimeError(
                    f"Gemini request failed: {error}"
                ) from error

            time.sleep(
                (2 ** attempt) + random.uniform(0.5, 1.5)
            )

    raise RuntimeError(
        f"Gemini request failed: {last_error}"
    )


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


def build_study_prompt(content, source_type="lecture"):

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


def analyze_content(content, source_type="lecture"):

    if not content or not str(content).strip():
        raise ValueError("No lecture content was received.")

    prompt = build_study_prompt(
        content,
        source_type
    )

    raw = request(
        prompt,
        json_mode=True,
        temperature=0.15,
        retries=2
    )

    return parse_json(raw)


def analyze_youtube_text(text):

    if not text or not text.strip():
        raise ValueError(
            "The YouTube transcript is empty."
        )

    return analyze_content(
        text,
        source_type="YouTube educational lecture"
    )


def analyze_audio_content(content):

    return analyze_content(
        content,
        source_type="audio lecture"
    )


def analyze_video_content(content):

    return analyze_content(
        content,
        source_type="video lecture"
    )


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
        retries=2
    )


def build_study_pack(content):

    return analyze_content(
        content,
        source_type="lecture"
    )