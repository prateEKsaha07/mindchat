# MindChat

A full stack AI chatbot built with FastAPI, TinyLlama, and React.

## Tech Stack

- **Backend** — FastAPI, SQLAlchemy, SQLite
- **Model** — TinyLlama 1.1B (GGUF, llama-cpp-python)
- **Auth** — JWT with bcrypt
- **Frontend** — React, Tailwind CSS, Vite

## Features

- User registration and login
- Real-time streaming responses
- Persistent conversation history
- Lightweight LLM running on CPU

## Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Model
Download TinyLlama GGUF model and place it in `model/checkpoints/`.
Update `MODEL_PATH` in `backend/app/config.py`.

## API Docs
Visit `http://localhost:8000/docs` after starting the backend.