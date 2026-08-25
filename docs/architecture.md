# Technical Design

## Data Flow

1. The student chooses a source in the Streamlit form.
2. Audio/video is processed through the Gemini media pipeline.
3. Public YouTube content is converted to educational text through transcript extraction.
4. Gemini receives the extracted content through a dynamic study prompt.
5. The model produces a structured study pack.
6. `st.session_state` keeps the study pack and learning progress available across reruns.
7. Pandas aggregates lecture-level analytics.
8. Streamlit renders KPIs, charts and interactive study views.

## API Strategy

The expensive AI workflow is triggered by a single `st.form_submit_button`. Temporary Gemini capacity errors use retry/backoff in the Gemini client. API credentials are read from environment variables and are never stored in source code.

## State Strategy

The app stores the current study pack, flashcard index, quiz score, studied-card count and lecture history in `st.session_state`.
