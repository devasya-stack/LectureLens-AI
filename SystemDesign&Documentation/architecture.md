# LectureLens AI — System Design & Documentation

## 1. System Overview

LectureLens AI is an AI-powered personal study workspace built using Python, Streamlit and Google Gemini.

The application transforms lectures, audio recordings, videos and public YouTube educational content into structured study material.

The system supports four primary lecture sources:

- Microphone recording
- Audio upload
- Video upload
- Public YouTube URL

The main processing flow is:

```text
Student
   |
   v
Streamlit Interface
   |
   v
Lecture Input
   |
   v
Content Processing
   |
   v
Gemini AI Study Engine
   |
   v
Structured Study Pack
   |
   v
Personal Study Workspace
```

The generated study workspace contains detailed notes, key concepts, definitions, formulas, flashcards, quizzes, exam questions, study coaching and revision planning.

---

## 2. Lucidchart System Architecture

The system architecture was designed using Lucidchart.

The architecture diagram represents the complete application flow from lecture input to AI-generated study resources.

https://github.com/devasya-stack/LectureLens-AI/blob/main/SystemDesign%26Documentation/lecturelens-architecture.png.png

### Architecture Components

The architecture contains the following major components:

```text
Student
   |
   v
LectureLens AI Streamlit Interface
   |
   +---- Microphone Recording
   |
   +---- Audio Upload
   |
   +---- Video Upload
   |
   +---- Public YouTube URL
              |
              v
       Content Processing
              |
              v
      Educational Content
              |
              v
       Gemini AI Engine
              |
              v
      Structured Study Pack
              |
              +---- Detailed Notes
              +---- Key Concepts
              +---- Definitions
              +---- Formulas
              +---- Flashcards
              +---- Quiz
              +---- Exam Questions
              +---- Study Coach
              +---- Revision Plan
              |
              v
       Personal Study Workspace
```

The technical implementation is divided into Python modules and deployed through Streamlit Community Cloud.

---

## 3. Data Flow Documentation

### Step 1 — Lecture Input

The student selects a lecture source from the Streamlit interface.

Available sources include:

```text
Microphone
Audio Upload
Video Upload
Public YouTube URL
```

### Step 2 — Source Processing

The selected source is sent to the appropriate processing pipeline.

Audio and video content is analyzed to identify useful educational information.

For YouTube input, the application:

1. Validates the URL.
2. Extracts the YouTube video ID.
3. Attempts to retrieve the available transcript.
4. Converts the transcript into educational content.

### Step 3 — Educational Content

The extracted information is prepared for AI processing.

The system focuses on:

- Main concepts
- Definitions
- Examples
- Applications
- Formulas
- Technical terminology
- Important explanations
- Exam-relevant information

### Step 4 — Gemini Processing

The processed lecture content is combined with a specialized LectureLens AI prompt.

The prompt dynamically provides the lecture content to Gemini.

### Step 5 — Structured Study Pack

Gemini generates a structured study pack containing:

- Summary
- TL;DR
- Key concepts
- Detailed notes
- Definitions
- Formulas
- Important points
- Common mistakes
- Flashcards
- Quiz questions
- Exam questions
- Study coach guidance
- Revision plan

### Step 6 — Study Workspace

The generated resources are displayed in the LectureLens AI study workspace.

The student can use the generated material for:

```text
Understanding
     ↓
Recall
     ↓
Practice
     ↓
Revision
     ↓
Exam Preparation
```

---

## 4. API Integration Strategy

LectureLens AI uses the Google Gemini API as its primary artificial intelligence engine.

The Gemini integration is centralized inside:

```text
modules/gemini_client.py
```

This module handles:

- Gemini client initialization
- Model configuration
- API requests
- Dynamic prompt construction
- Structured responses
- JSON parsing
- Error handling
- Retry handling

### Dynamic Prompt Engineering

Lecture content is dynamically inserted into the educational prompt.

Example:

```python
prompt = f"""
You are LectureLens AI.

Create a university-level study pack
from the following lecture content:

{content}
"""
```

The AI is instructed to behave as a specialized educational study engine rather than a generic chatbot.

The generated response is structured so that the application can separately display notes, flashcards, quizzes and exam preparation material.

### AI Output

The Gemini study engine generates:

```text
Detailed Notes
Key Concepts
Definitions
Formulas
Important Points
Common Mistakes
Flashcards
Quiz
Exam Questions
Study Coach
Revision Plan
```

---

## 5. Module Documentation

### `app.py`

The main Streamlit application.

Responsibilities:

- Application interface
- Source selection
- Audio and video upload
- YouTube URL input
- Study workspace
- Session state
- Progress tracking
- User interaction

### `modules/gemini_client.py`

Central Gemini API integration module.

Responsibilities:

- Gemini client initialization
- Model configuration
- AI requests
- Prompt processing
- Structured JSON output
- JSON parsing
- Error handling
- Retry handling

### `modules/audio_processor.py`

Processes lecture audio.

Responsibilities include preparing recorded or uploaded audio for educational analysis.

### `modules/video_processor.py`

Processes uploaded lecture videos.

The module prepares video content for multimodal educational analysis.

### `modules/url_processor.py`

Processes public YouTube URLs.

Responsibilities:

- YouTube URL validation
- Video ID extraction
- Transcript retrieval
- Transcript processing
- Educational content preparation

### `modules/flashcard_engine.py`

Handles flashcard-related functionality.

Responsibilities include:

- Flashcard generation
- Flashcard presentation
- Study interaction
- Flashcard progress

### `modules/quiz_engine.py`

Handles quiz functionality.

Responsibilities include:

- Quiz generation
- Answer checking
- Quiz scoring
- Quiz interaction

### `utils/`

Contains reusable application utilities.

These utilities support:

- Prompt handling
- UI helpers
- Reusable interface functionality

---

## 6. State Management

LectureLens AI uses Streamlit `st.session_state` to preserve important application information across Streamlit reruns.

This prevents generated study information from unnecessarily disappearing when the user interacts with the application.

Important state includes:

```text
Generated Study Pack
Selected Source
Flashcard Progress
Quiz State
Quiz Score
Study Progress
```

### Why Session State Is Used

Streamlit applications can rerun when users interact with widgets.

Session state allows LectureLens AI to preserve the current study session during these reruns.

This supports a smoother interactive study experience.

---

## 7. Deployment Architecture

LectureLens AI is deployed using Streamlit Community Cloud.

The deployment architecture is:

```text
GitHub Repository
       |
       v
Streamlit Community Cloud
       |
       v
LectureLens AI
       |
       +----------------------+
       |                      |
       v                      v
Application Modules     Streamlit Secrets
                              |
                              v
                       Google Gemini API
```

### Deployment Components

#### GitHub

The source code is maintained in the LectureLens AI GitHub repository.

Repository:

https://github.com/devasya-stack/LectureLens-AI

#### Streamlit Community Cloud

The Streamlit application is deployed publicly through Streamlit Community Cloud.

Live application:

https://lecture-lens-ai.streamlit.app/

#### Requirements

The application dependencies are defined in:

```text
requirements.txt
```

This allows the cloud deployment environment to install the required Python packages.

#### Secrets

API credentials are stored using Streamlit Secrets rather than being committed to the public repository.

---

## 8. Security Strategy

LectureLens AI follows an environment-based API credential strategy.

### Local Development

During local development, Gemini credentials are stored in environment variables.

Example:

```text
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-3.6-flash
```

The `.env` file is excluded from version control using `.gitignore`.

### Cloud Deployment

For Streamlit Community Cloud, credentials are stored using Streamlit Secrets.

Example:

```toml
GEMINI_API_KEY = "your_api_key"
GEMINI_MODEL = "gemini-3.6-flash"
```

The actual API key is never included in the public GitHub repository.

### Security Principles

```text
API Key
   |
   v
Environment / Streamlit Secrets
   |
   v
Gemini Client
   |
   v
Gemini API
```

This prevents sensitive credentials from being exposed in the source code.

---

## 9. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web application and user interface |
| Google Gemini | AI lecture understanding and study generation |
| YouTube Transcript API | YouTube transcript extraction |
| Requests | HTTP communication |
| Pandas | Data processing |
| python-dotenv | Environment configuration |

### Main Application Components

```text
Frontend / UI
    ↓
Streamlit

Application Logic
    ↓
Python

AI Engine
    ↓
Google Gemini

YouTube Processing
    ↓
YouTube Transcript API

Cloud Deployment
    ↓
Streamlit Community Cloud
```

---

## 10. Complete System Flow

```text
                         STUDENT
                            |
                            v
                  ┌───────────────────┐
                  │   STREAMLIT UI    │
                  │   LectureLens AI  │
                  └─────────┬─────────┘
                            |
              ┌─────────────┼─────────────┐
              |             |             |
              v             v             v
        MICROPHONE        AUDIO          VIDEO
        RECORDING         UPLOAD         UPLOAD
              |             |             |
              └─────────────┼─────────────┘
                            |
                            v
                     YOUTUBE URL
                            |
                            v
                  CONTENT PROCESSING
                            |
                            v
                 EDUCATIONAL CONTENT
                            |
                            v
                  GEMINI AI ENGINE
                            |
                            v
                STRUCTURED STUDY PACK
                            |
        ┌───────────┬───────┼───────┬───────────┐
        |           |       |       |           |
        v           v       v       v           v
      NOTES    FLASHCARDS  QUIZ  EXAM PREP   STUDY COACH
        |           |       |       |           |
        └───────────┴───────┼───────┴───────────┘
                            |
                            v
                   REVISION PLAN
                            |
                            v
                PERSONAL STUDY WORKSPACE
```

### Processing Pipeline

```text
Lecture Source
      ↓
Input Validation
      ↓
Content Extraction
      ↓
Educational Content
      ↓
Dynamic Gemini Prompt
      ↓
Gemini AI
      ↓
Structured JSON Response
      ↓
JSON Parsing
      ↓
Study Workspace
```

---

## 11. Capstone Rubric Alignment

### Technical Implementation & Architecture — 25 Points

LectureLens AI demonstrates:

- Modular Python architecture
- Streamlit application architecture
- `st.session_state`
- Structured content processing
- Gemini API abstraction
- JSON response parsing
- Error handling
- Retry handling

### AI Integration & Prompt Engineering — 20 Points

The application demonstrates:

- Google Gemini API integration
- Dynamic prompts
- f-string lecture context
- Audio processing
- Video processing
- YouTube processing
- Structured AI output
- Educational prompt engineering
- AI-generated study resources

### UI/UX & Data Visualization — 20 Points

The application provides:

- Product-style dashboard
- Streamlit column layouts
- KPI metrics
- Expanders
- Interactive flashcards
- Interactive quizzes
- Study progress
- Structured study workspace

### Deployment & Cloud Engineering — 15 Points

The project provides:

- Streamlit Community Cloud deployment
- Public live application
- GitHub source repository
- `requirements.txt`
- Streamlit Secrets
- Cloud-based API configuration

### Open-Source Branding — 10 Points

The repository provides:

- Customized README
- Project overview
- Feature documentation
- Architecture documentation
- Setup instructions
- Technology stack
- Security information
- Deployment information
- Live application link
- GitHub repository link

### System Design & Documentation — 10 Points

This technical design document provides:

- Lucidchart system architecture
- Data-flow documentation
- Gemini API integration strategy
- Module documentation
- State-management strategy
- Deployment architecture
- Security strategy
- Technology stack
- Complete processing pipeline

---

## Project Links

### Live Application

https://lecture-lens-ai.streamlit.app/

### GitHub Repository

https://github.com/devasya-stack/LectureLens-AI

### Architecture Diagram

The visual architecture diagram is available in:

```text
docs/lecturelens-architecture.png
```

---

## Conclusion

LectureLens AI transforms unstructured lecture content into a complete AI-powered study system.

The application combines multimodal content processing, Gemini AI, structured study generation and an interactive Streamlit interface to help students understand, recall, practice and revise academic material.