# MindChat

A full stack AI chatbot built from scratch — FastAPI backend, TinyLlama LLM running locally on CPU, JWT authentication, real-time streaming responses, and a React frontend.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python |
| Database | SQLite + SQLAlchemy |
| Authentication | JWT + bcrypt |
| Model | TinyLlama 1.1B (GGUF format) |
| Inference | llama-cpp-python |
| Frontend | React, Tailwind CSS, Vite |

---

## Project Structure
```bash
mindchat/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, startup, middleware
│   │   ├── config.py            # Settings and environment variables
│   │   ├── routers/
│   │   │   ├── auth.py          # Register, login, /me endpoints
│   │   │   └── chat.py          # Chat, stream, history endpoints
│   │   ├── services/
│   │   │   ├── auth_service.py  # JWT, password hashing, user lookup
│   │   │   ├── chat_service.py  # Conversation logic, message history
│   │   │   └── inference.py     # Model loading, prompt formatting, generation
│   │   ├── models/
│   │   │   ├── user.py          # User database model
│   │   │   └── conversation.py  # Conversation and Message database models
│   │   ├── schemas/
│   │   │   ├── user.py          # Pydantic schemas for auth
│   │   │   └── chat.py          # Pydantic schemas for chat
│   │   └── db/
│   │       ├── database.py      # SQLAlchemy engine and session
│   │       └── init_db.py       # Table creation on startup
│   └── requirements.txt
├── model/
│   └── checkpoints/             # GGUF model file goes here
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Login.jsx        # Login and register page
│       │   └── Chat.jsx         # Main chat interface
│       ├── services/
│       │   └── api.js           # All API calls in one place
│       └── App.jsx              # Routing
└── README.
```

---

## Data Flow

### Authentication

User fills login form
→ POST /auth/login
→ backend verifies email + bcrypt password check
→ JWT token created with user ID inside
→ token stored in browser localStorage
→ user redirected to chat page

### Chat Request (streaming)

User types message → hits Enter
→ frontend calls POST /chat/stream with JWT token in header
→ backend verifies JWT → extracts user ID
→ fetches or creates conversation in DB
→ loads last 10 messages from conversation history
→ formats full history into ChatML prompt:
<|system|> You are MindChat... </s>
<|user|> previous message </s>
<|assistant|> previous response </s>
<|user|> new message </s>
<|assistant|>    ← model generates from here
→ llama-cpp-python runs inference on CPU
→ tokens streamed back one by one via Server-Sent Events
→ frontend receives tokens and renders them in real time
→ on stream complete, full response saved to DB
→ conversation title updated from first message

### Conversation History

User clicks past conversation in sidebar
→ GET /chat/conversations/{id}/messages
→ all messages fetched from DB in chronological order
→ rendered in chat window

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 22+
- TinyLlama GGUF model file

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

APP_NAME=MindChat
APP_VERSION=0.1.0
DEBUG=True
SECRET_KEY=your-secret-key-here

Download the model:
```bash
python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF',
    filename='tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
    local_dir='../model/checkpoints'
)
"
```

Update `MODEL_PATH` in `backend/app/config.py` to point to the downloaded file.

Start the backend:
```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | /auth/register | Create account | No |
| POST | /auth/login | Login, get JWT | No |
| GET | /auth/me | Get current user | Yes |
| POST | /chat/ | Send message | Yes |
| POST | /chat/stream | Send message, stream response | Yes |
| GET | /chat/conversations | List all conversations | Yes |
| GET | /chat/conversations/{id}/messages | Get conversation messages | Yes |

---

## Limitations

**Model size** — TinyLlama is a 1.1B parameter model. It gives coherent responses but hallucinates frequently, struggles with complex reasoning, and has limited world knowledge compared to larger models like GPT-4 or Claude.

**CPU inference** — The model runs entirely on CPU with 4-bit quantization. Response times are 3-10 seconds depending on response length. Not suitable for multiple concurrent users.

**Context window** — Only the last 10 messages are passed to the model to stay within the 2048 token context limit. Very long conversations lose early context.

**No streaming interruption** — Once a response starts generating it cannot be cancelled. The user must wait for it to finish.

**Local only** — The model file is 670MB and not included in the repo. Setup requires manually downloading the model.

**Authentication** — JWT tokens are stored in localStorage which is vulnerable to XSS attacks. A production app would use httpOnly cookies.

**Single user database** — SQLite works fine for development and portfolio use but does not scale to multiple concurrent users. A production deployment would use PostgreSQL.

---

## What I Learned

- Building a production-style REST API with FastAPI and async SQLAlchemy
- Running a quantized LLM locally using llama-cpp-python
- Implementing JWT authentication from scratch
- Streaming HTTP responses with Server-Sent Events
- Connecting a React frontend to a Python backend end to end
- Managing conversation context and message history for an LLM

---

## Future Improvements

- Fine-tune the model on custom conversational data using LoRA
- Add RAG (Retrieval Augmented Generation) for document Q&A
- Upgrade to a larger model for better response quality
- Add PostgreSQL for production database
- Deploy backend to Railway, model to Hugging Face Spaces
