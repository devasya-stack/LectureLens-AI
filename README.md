# ✦ LectureLens AI

## Turn lectures into knowledge.

LectureLens AI is an AI-powered personal study workspace that transforms lectures, audio recordings, videos and public YouTube educational content into structured study material.

It uses Google Gemini to understand lecture content and generate detailed notes, key concepts, definitions, formulas, flashcards, quizzes, exam questions and revision guidance.

---

## 🚀 Live Demo

### [▶ Open LectureLens AI](https://lecture-lens-ai.streamlit.app/) Jai Hanuman ji

### [📦 View Source Code on GitHub](https://github.com/devasya-stack/LectureLens-AI)

---

## 🎓 Problem Statement

### Voice-Notes to Flashcards

LectureLens AI is based on the MirAI School of Technology EdTech problem statement:

> Users speak a chaotic lecture summary into the microphone. The application processes the lecture and uses Gemini to generate useful study material.

The project extends the idea by supporting multiple educational sources:

- Microphone recording
- Audio upload
- Video upload
- Public YouTube URLs

The content is transformed into a complete study workspace instead of only generating flashcards.

---

# ✦ Features

### 🎙️ Voice Recording

Record lecture content directly through the browser.

### 📁 Audio Upload

Upload existing lecture recordings and process them with Gemini.

### 🎬 Video Upload

Upload educational videos and extract useful learning content.

### 🔗 YouTube URL

Provide a public educational YouTube URL and LectureLens processes the available transcript.

### 🧠 Gemini AI Study Engine

Gemini acts as a specialized educational engine rather than a generic chatbot.

### 📝 Detailed Notes

Generate structured university-level study notes.

### 💡 Key Concepts

Identify the most important concepts from the lecture.

### 📖 Definitions

Extract important terminology and explain it clearly.

### 📐 Formulas

Identify relevant formulas and explain their meaning and application.

### 🃏 Flashcards

Automatically generate active-recall flashcards.

### 🧪 Quiz

Generate multiple-choice questions with answers and explanations.

### 🎯 Exam Preparation

Generate likely exam questions and answer outlines.

### 🧑‍🏫 AI Study Coach

Generate personalized study recommendations.

### 📅 Revision Plan

Create a structured revision approach based on the lecture.

---

# 🧠 AI Study Pipeline

```text
                    LECTURE INPUT
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   🎙 Microphone    📁 Audio Upload   🎬 Video Upload
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                  🔗 YouTube URL
                         │
                         ▼
                CONTENT PROCESSING
                         │
                         ▼
                  GEMINI AI ENGINE
                         │
                         ▼
                STRUCTURED STUDY PACK
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
      NOTES        FLASHCARDS           QUIZ
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                  EXAM PREPARATION
                         │
                         ▼
                    STUDY COACH
                         │
                         ▼
                 PERSONAL WORKSPAC


# 🏗️ System Architecture
flowchart TD

    A[Student] --> B[Streamlit UI]

    B --> C{Choose Source}

    C --> D[Microphone]
    C --> E[Audio Upload]
    C --> F[Video Upload]
    C --> G[YouTube URL]

    D --> H[Content Processing]
    E --> H
    F --> H
    G --> I[Transcript Extraction]

    I --> H

    H --> J[Lecture Content]

    J --> K[Gemini AI Study Engine]

    K --> L[Structured Study Pack]

    L --> M[Detailed Notes]
    L --> N[Key Concepts]
    L --> O[Definitions]
    L --> P[Formulas]
    L --> Q[Flashcards]
    L --> R[Quiz]
    L --> S[Exam Questions]
    L --> T[Study Coach]
    L --> U[Revision Plan]

    M --> V[Study Workspace]
    N --> V
    O --> V
    P --> V
    Q --> V
    R --> V
    S --> V
    T --> V
    U --> V