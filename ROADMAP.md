# 🚀 ROADMAP – SupMTI Intelligent Chatbot (Vocal & Textuel)

> **Compétition IA** – Assistant intelligent pour l'orientation scolaire  
> Architecture: **RAG (Retrieval-Augmented Generation)** via **OpenRouter API**

---

## 📊 Project Overview

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| **LLM Backend** | OpenRouter API (Qwen3 / DeepSeek-R1 / GPT-4o-mini) | Cost-effective, multilingual, high accuracy |
| **Embedding Model** | `all-MiniLM-L6-v2` (sentence-transformers) | Free, fast, multilingual, runs locally |
| **Vector Store** | ChromaDB | Lightweight, persistent, Python-native, metadata filtering |
| **STT (Speech-to-Text)** | Whisper (openai/whisper) via browser + API fallback | Best multilingual ASR, Darija support via fine-tuned models |
| **TTS (Text-to-Speech)** | Web Speech API (browser) + Edge TTS fallback | Zero-cost, multilingual, natural voices |
| **Frontend** | Next.js / React | Modern, fast, SSR, great DX |
| **Backend** | FastAPI (Python) | Async, fast, perfect for ML pipelines |
| **Deployment** | Vercel (frontend) + Railway/Render (backend) | Free tiers, easy CI/CD |

---

## 🏗️ Phase 1: Data Collection & Knowledge Base Preparation

> **Goal:** Build the school's knowledge base that powers the RAG system

- [x] Define data schema and categories
- [ ] Collect school data:
  - [ ] Programs & filières (descriptions, modules, duration, career paths)
  - [ ] Admission requirements per filière (diplôme requis, notes minimales, spécialités)
  - [ ] Registration process & deadlines
  - [ ] School fees & scholarships
  - [ ] Campus info (location, facilities, clubs)
  - [ ] Faculty & staff info
  - [ ] FAQ (frequently asked questions)
  - [ ] Contact information
- [ ] Structure data in JSON/Markdown documents
- [ ] Translate key documents into 3 languages (FR / EN / Darija)
- [ ] Create eligibility rules matrix (diplôme × filière → eligible/not)

### 📝 Data Format
```
data/
├── programs/
│   ├── genie_informatique.md
│   ├── genie_civil.md
│   ├── genie_electrique.md
│   └── ...
├── admissions/
│   ├── eligibility_rules.json
│   ├── process.md
│   └── deadlines.md
├── general/
│   ├── fees.md
│   ├── campus.md
│   ├── faq.md
│   └── contacts.md
└── translations/
    ├── fr/
    ├── en/
    └── darija/
```

---

## 🧠 Phase 2: RAG Pipeline Development

> **Goal:** Build the core intelligence engine

- [ ] Set up Python backend with FastAPI
- [ ] Install & configure dependencies:
  - [ ] `chromadb` for vector storage
  - [ ] `sentence-transformers` for local embeddings
  - [ ] `langchain` for RAG orchestration
  - [ ] `openai` SDK (for OpenRouter compatibility)
- [ ] Build document ingestion pipeline:
  - [ ] Parse Markdown/JSON documents
  - [ ] Chunk documents intelligently (by section, ~500 tokens)
  - [ ] Generate embeddings using `all-MiniLM-L6-v2`
  - [ ] Store in ChromaDB with metadata (category, language, filière)
- [ ] Build retrieval pipeline:
  - [ ] Implement semantic search with metadata filtering
  - [ ] Add re-ranking for better accuracy (cross-encoder)
  - [ ] Implement hybrid search (semantic + keyword BM25)
- [ ] Build generation pipeline:
  - [ ] Design system prompt with school persona
  - [ ] Inject retrieved context into LLM prompt
  - [ ] Add guardrails (stay on-topic, no hallucinations)
  - [ ] Implement streaming responses
- [ ] Build eligibility checker:
  - [ ] Rule-based engine for immediate eligibility checks
  - [ ] LLM-assisted for nuanced recommendations
  - [ ] Return structured results (eligible filières + alternatives)

### 🔧 Advanced RAG Techniques
- [ ] **Query Rewriting**: Rephrase user queries for better retrieval
- [ ] **Multi-Query RAG**: Generate multiple search queries from one question
- [ ] **Contextual Compression**: Extract only relevant portions from retrieved docs
- [ ] **Conversation Memory**: Track chat history for follow-up questions
- [ ] **Fallback Strategy**: Graceful handling when no relevant docs found

---

## 🎙️ Phase 3: Voice Integration

> **Goal:** Enable speech-to-text and text-to-speech in 3 languages

- [ ] **Speech-to-Text (STT)**:
  - [ ] Primary: Web Speech API (browser-native, zero-cost)
  - [ ] Fallback: Whisper API via OpenRouter or local whisper.cpp
  - [ ] Language detection (auto-detect Darija/FR/EN)
  - [ ] Handle noisy audio and informal speech
- [ ] **Text-to-Speech (TTS)**:
  - [ ] Primary: Web Speech API with language-specific voices
  - [ ] Fallback: Edge TTS API (free, high-quality Microsoft voices)
  - [ ] Support Darija with Arabic voice synthesis
  - [ ] Implement voice selection per language
- [ ] **Voice UX**:
  - [ ] Push-to-talk button with visual feedback
  - [ ] Real-time transcription display
  - [ ] Audio waveform visualization during recording
  - [ ] Voice activity detection (VAD) for auto-stop

---

## 🌍 Phase 4: Multilingual Support

> **Goal:** Seamless experience in Darija 🇲🇦, Français 🇫🇷, English 🇬🇧

- [ ] **Language Detection**:
  - [ ] Auto-detect input language from text
  - [ ] Auto-detect spoken language from audio
  - [ ] Manual language selector in UI
- [ ] **Translation Strategy**:
  - [ ] Store knowledge base primarily in French
  - [ ] Use LLM to respond in the detected language
  - [ ] Ensure Darija responses use natural Moroccan dialect (not MSA)
- [ ] **Darija Handling** (Innovation Point 🌟):
  - [ ] Support both Arabic script (الدارجة) and Latinized Darija (3aribiya)
  - [ ] Custom glossary for school-specific Darija terms
  - [ ] LLM prompt engineering for authentic Darija output
- [ ] **UI Localization**:
  - [ ] Interface labels in all 3 languages
  - [ ] RTL support for Arabic/Darija text
  - [ ] Culturally appropriate UI elements per language

---

## 🎨 Phase 5: Frontend & UX Design

> **Goal:** Build a stunning, award-winning UI

- [ ] **Design System**:
  - [ ] School brand colors & typography
  - [ ] Glassmorphism + dark mode aesthetic
  - [ ] Smooth micro-animations (Framer Motion)
  - [ ] Mobile-first responsive design
- [ ] **Chat Interface**:
  - [ ] Modern chat bubble design
  - [ ] Typing indicator with animated dots
  - [ ] Message reactions & feedback (thumbs up/down)
  - [ ] Rich message types (cards, carousels, tables)
  - [ ] Code-like eligibility result cards
- [ ] **Voice Interface**:
  - [ ] Animated microphone button with pulse effect
  - [ ] Real-time audio waveform visualization
  - [ ] Language indicator badge
  - [ ] Voice-to-text live transcription overlay
- [ ] **Onboarding Flow**:
  - [ ] Welcome screen with school branding
  - [ ] Quick profile setup (diplôme, interests, language)
  - [ ] Guided tour of features
  - [ ] Suggested questions carousel
- [ ] **Recommendation Dashboard**:
  - [ ] Visual filière comparison cards
  - [ ] Compatibility score visualization (radar chart)
  - [ ] Career path timeline
  - [ ] Interactive eligibility checklist
- [ ] **Innovative Features** 🏆:
  - [ ] 3D school campus preview (Three.js)
  - [ ] Animated mascot/avatar for the chatbot
  - [ ] Dark/Light mode toggle with smooth transition
  - [ ] Confetti animation on eligibility confirmation
  - [ ] Share results via link/QR code

---

## 🔌 Phase 6: API & Backend Architecture

> **Goal:** Robust, scalable backend

```
┌──────────────────────────────────────────────┐
│                   Frontend                    │
│              (Next.js / React)                │
└─────────────────┬────────────────────────────┘
                  │ REST / WebSocket
┌─────────────────▼────────────────────────────┐
│               FastAPI Backend                 │
├───────────────────────────────────────────────┤
│  /api/chat          → RAG pipeline            │
│  /api/voice/stt     → Speech-to-Text          │
│  /api/voice/tts     → Text-to-Speech          │
│  /api/eligibility   → Eligibility checker     │
│  /api/recommend     → Recommendation engine   │
│  /api/feedback      → User feedback           │
│  /ws/chat           → Streaming chat           │
└──────┬────────┬────────┬─────────────────────┘
       │        │        │
┌──────▼──┐ ┌──▼────┐ ┌─▼──────────┐
│ChromaDB │ │OpenR. │ │Eligibility │
│(Vectors)│ │ API   │ │  Rules DB  │
└─────────┘ └───────┘ └────────────┘
```

- [ ] FastAPI app structure with routers
- [ ] WebSocket support for streaming responses
- [ ] Rate limiting & error handling
- [ ] CORS configuration for frontend
- [ ] Environment variable management
- [ ] API documentation (auto-generated Swagger)
- [ ] Health check & monitoring endpoints
- [ ] Logging & analytics

---

## 📏 Phase 7: Evaluation & Quality Assurance

> **Goal:** Ensure high accuracy and win the "Meilleure IA" category

- [ ] **RAG Evaluation Framework**:
  - [ ] Build test dataset: 100+ Q&A pairs across all topics
  - [ ] Metrics: Retrieval Precision@K, Answer Relevance, Faithfulness
  - [ ] Use RAGAS framework for automated evaluation
  - [ ] Test edge cases: typos, mixed languages, vague questions
- [ ] **Eligibility Testing**:
  - [ ] Test all diploma × filière combinations
  - [ ] Verify alternative suggestions accuracy
  - [ ] Edge cases: dual diplomas, foreign degrees
- [ ] **Voice Testing**:
  - [ ] Test STT accuracy across 3 languages
  - [ ] Test TTS naturalness (MOS scoring)
  - [ ] Test in noisy environments
- [ ] **UX Testing**:
  - [ ] Mobile responsiveness testing
  - [ ] Accessibility audit (WCAG 2.1)
  - [ ] Load testing (concurrent users)
  - [ ] Browser compatibility
- [ ] **Prompt Engineering Iteration**:
  - [ ] A/B test different system prompts
  - [ ] Fine-tune context window size
  - [ ] Optimize chunk size for retrieval quality

---

## 🚢 Phase 8: Deployment & Demo Prep

> **Goal:** Deploy and prepare winning demo

- [ ] **Deployment**:
  - [ ] Deploy backend to Railway/Render (free tier)
  - [ ] Deploy frontend to Vercel
  - [ ] Set up environment variables
  - [ ] Configure HTTPS & custom domain (optional)
  - [ ] Set up monitoring & alerting
- [ ] **Demo Preparation**:
  - [ ] Prepare demo script (5-min walkthrough)
  - [ ] Pre-load impressive conversation scenarios
  - [ ] Test voice features in demo room conditions
  - [ ] Prepare backup plan (offline fallback)
  - [ ] Create presentation slides
- [ ] **Documentation**:
  - [ ] Architecture diagram
  - [ ] Setup & deployment guide
  - [ ] Cost analysis (API usage estimates)
  - [ ] Innovation highlights document

---

## 💰 Cost Estimation

| Component | Cost | Notes |
|-----------|------|-------|
| OpenRouter API (LLM) | ~$0.10-0.50/day | Using cheap models (GPT-4o-mini, Qwen, DeepSeek) |
| Embedding Model | **$0** | Runs locally (sentence-transformers) |
| ChromaDB | **$0** | Self-hosted, open-source |
| STT (Whisper) | **$0** | Browser Web Speech API / local whisper |
| TTS | **$0** | Browser Web Speech API / Edge TTS |
| Frontend Hosting | **$0** | Vercel free tier |
| Backend Hosting | **$0** | Railway/Render free tier |
| **Total** | **~$0.10-0.50/day** | Mostly free! |

---

## 🏆 Competition Strategy

### "Meilleure IA" 🧠
- Hybrid RAG (semantic + BM25) for high retrieval accuracy
- Advanced prompt engineering with guardrails
- Query rewriting for handling poorly formatted questions
- RAGAS evaluation scores as proof of quality

### "Meilleure UX" 🎨
- Glassmorphism dark mode with school branding
- Smooth animations (Framer Motion)
- Mobile-first responsive design
- Onboarding flow with guided tour
- Rich message types (cards, charts, timelines)

### "Projet le plus innovant" 💡
- Darija support with both Arabic & Latin script
- Voice interaction with live waveform visualization
- AI-powered filière recommendation with compatibility radar chart
- 3D campus preview
- Share results via QR code
- Animated chatbot mascot

---

## ⏱️ Timeline (Estimated)

| Phase | Duration | Priority |
|-------|----------|----------|
| Phase 1: Data Collection | 2-3 days | 🔴 Critical |
| Phase 2: RAG Pipeline | 3-4 days | 🔴 Critical |
| Phase 3: Voice | 2 days | 🟡 Important |
| Phase 4: Multilingual | 1-2 days | 🟡 Important |
| Phase 5: Frontend/UX | 3-4 days | 🔴 Critical |
| Phase 6: Backend API | 2 days | 🔴 Critical |
| Phase 7: Evaluation | 2 days | 🟡 Important |
| Phase 8: Deployment | 1 day | 🔴 Critical |
| **Total** | **~16-18 days** | |

---

> **Next Steps:** Set up the project structure and begin Phase 1 & 2 in parallel.
