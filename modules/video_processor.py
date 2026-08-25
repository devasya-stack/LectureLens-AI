import mimetypes
from modules.gemini_client import request


def analyze_video(video_file):

    if video_file is None:
        raise ValueError(
            "Please upload a video file."
        )

    video_bytes = video_file.getvalue()

    if not video_bytes:
        raise ValueError(
            "The video file is empty."
        )

    filename = getattr(
        video_file,
        "name",
        "lecture.mp4"
    )

    mime_type = mimetypes.guess_type(
        filename
    )[0]

    if not mime_type:
        mime_type = "video/mp4"

    prompt = """
You are LectureLens AI, an advanced university study assistant.

Analyze this lecture video carefully.

Understand the educational content from the video and transform it into detailed study material.

Extract:

- Main concepts
- Definitions
- Important explanations
- Examples
- Applications
- Formulas
- Technical terminology
- Relationships between concepts
- Exam-relevant information
- Important visual explanations when relevant
- Common misconceptions

Use the spoken lecture and relevant visual information.

Correct obvious speech/transcription errors using context.

Do not invent information that is not supported by the video.

Return detailed educational lecture content only.

The extracted content will be passed to the LectureLens study engine to generate:

- Detailed notes
- Flashcards
- Quiz questions
- Exam questions
- Revision plans
- Study recommendations

Make the output detailed enough for university-level examination preparation.
"""

    return request(
        [
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": video_bytes
                }
            },
            prompt
        ],
        temperature=0.15,
        retries=5
    )