# SupMTI Intelligent Chatbot 🎓

> AI-powered chatbot for student orientation at SupMTI.
> Supports text & voice interaction in **Darija 🇲🇦**, **Français 🇫🇷**, and **English 🇬🇧**.

## Architecture

```
supmti-project/
├── backend/              # FastAPI + RAG Pipeline
│   ├── app/
│   │   ├── main.py       # FastAPI entry point
│   │   ├── config.py     # Environment configuration
│   │   ├── rag/          # RAG pipeline components
│   │   │   ├── embeddings.py   # Sentence-transformers (local)
│   │   │   ├── vectorstore.py  # ChromaDB vector store
│   │   │   ├── retriever.py    # Hybrid semantic + BM25 search
│   │   │   ├── generator.py    # OpenRouter LLM generation
│   │   │   └── pipeline.py     # Full RAG orchestration
│   │   ├── services/     # Business logic
│   │   │   ├── chat_service.py
│   │   │   ├── eligibility_service.py
│   │   │   ├── recommendation_service.py
│   │   │   ├── voice_service.py
│   │   │   └── language_service.py
│   │   └── routers/      # API endpoints
│   │       ├── chat.py   # REST + WebSocket streaming
│   │       ├── voice.py  # TTS endpoint
│   │       ├── eligibility.py
│   │       └── recommend.py
│   ├── data/             # Knowledge base documents
│   ├── scripts/
│   │   └── ingest.py     # Data ingestion into ChromaDB
│   └── requirements.txt
├── frontend/             # Next.js + React
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx      # Main chat interface
│   │   │   ├── layout.tsx    # Root layout
│   │   │   └── globals.css   # Design system
│   │   └── components/
│   │       ├── ChatWindow.tsx
│   │       ├── VoiceButton.tsx
│   │       ├── LanguageSelector.tsx
│   │       └── Sidebar.tsx
│   └── package.json
└── ROADMAP.md
```

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file and add your API key
cp .env.example .env
# Edit .env → set OPENROUTER_API_KEY=sk-or-v1-your-key

# Ingest knowledge base data
python -m scripts.ingest

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 3. Open the App

Visit **http://localhost:3000** 🚀

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send a message, get AI response |
| `/ws/chat` | WebSocket | Streaming chat |
| `/api/voice/tts` | POST | Text-to-Speech (returns MP3) |
| `/api/voice/voices` | GET | List available TTS voices |
| `/api/eligibility/check` | POST | Check student eligibility |
| `/api/eligibility/programs` | GET | List all programs |
| `/api/recommend/` | POST | Get program recommendations |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger API documentation |

## Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| LLM | OpenRouter (GPT-4o-mini / Llama 70B) | ~$0.10-0.50/day |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Free (local) |
| Vector DB | ChromaDB | Free (local) |
| Backend | FastAPI (Python) | Free |
| Frontend | Next.js + React | Free |
| STT | Web Speech API (browser) | Free |
| TTS | Edge TTS (Microsoft) | Free |

## License

Built for the SupMTI AI Competition 🏆
