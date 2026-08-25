import os
import mimetypes
from modules.gemini_client import request


def analyze_audio(audio_file):

    if audio_file is None:
        raise ValueError(
            "Please upload or record an audio file."
        )

    audio_bytes = audio_file.getvalue()

    if not audio_bytes:
        raise ValueError(
            "The audio file is empty."
        )

    filename = getattr(
        audio_file,
        "name",
        "lecture_audio.wav"
    )

    mime_type = mimetypes.guess_type(
        filename
    )[0]

    if not mime_type:
        mime_type = "audio/wav"

    prompt = """
You are LectureLens AI, an advanced university study assistant.

Analyze this lecture audio carefully.

Understand the spoken lecture and transform it into detailed educational content.

Extract:

- Main concepts
- Definitions
- Important explanations
- Examples
- Applications
- Formulas
- Technical terminology
- Relationships between concepts
- Important exam points
- Potential misconceptions

Clean obvious speech recognition errors using context.

Do not invent information that is not supported by the lecture.

Return detailed educational text only.

The output will be passed to another AI study engine that will create:

- Detailed notes
- Flashcards
- Quiz questions
- Exam questions
- Revision plans
- Study recommendations

Make the extracted lecture content detailed and accurate.
"""

    return request(
        [
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": audio_bytes
                }
            },
            prompt
        ],
        temperature=0.15
    )