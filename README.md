# ✦ LectureLens AI

### Turn lectures into knowledge.

LectureLens AI is an AI-powered personal study workspace that transforms lectures, audio recordings, videos and public YouTube educational content into structured learning material.

It uses Google's Gemini API to understand educational content and generate detailed notes, key concepts, definitions, formulas, flashcards, quizzes, exam questions and personalized revision guidance.

Live App: https://lecture-lens-ai.streamlit.app/ Jai Hanuman Ji

## 🚀 Features

- 🎙️ Record lectures directly from the browser
- 📁 Upload lecture audio
- 🎬 Upload lecture videos
- 🔗 Process public YouTube educational videos
- 🧠 Gemini-powered lecture understanding
- 📝 Detailed AI-generated study notes
- 💡 Key concepts and definitions
- 📐 Formula extraction
- 🃏 Automatic flashcard generation
- 🧪 Interactive quizzes
- 🎯 Exam-oriented questions
- 🧑‍🏫 AI Study Coach
- 📅 Personalized revision plan
- 📊 Study progress dashboard
- 💾 Persistent Streamlit session state
- 🌙 Product-style Streamlit interface

## 🧠 AI Study Pipeline

```text
Lecture Source
     │
     ├── Microphone
     ├── Audio Upload
     ├── Video Upload
     └── YouTube URL
             │
             ▼
       Content Extraction
             │
             ▼
        Gemini AI Engine
             │
             ▼
      Structured Study Pack
             │
     ┌───────┼────────┐
     ▼       ▼        ▼
   Notes  Flashcards  Quiz
     │       │        │
     └───────┼────────┘
             ▼
       Exam Preparation
             │
             ▼
       AI Study Coach