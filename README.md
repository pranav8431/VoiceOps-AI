# VoiceOps AI

Real-time agentic voice operations platform for HR, payroll, and labour-compliance.

A voice agent that understands spoken requests, plans actions, uses enterprise tools, verifies results, and completes tasks in real time. Built for the HR/payroll domain — the agent can handle requests like:

- "How many employees haven't marked attendance today?"
- "Find the applicable minimum wage for this worker category and location."
- "Generate a draft payroll exception report for this month."
- "Which statutory compliance tasks are overdue?"
- "Create a grievance ticket for this employee and assign it to HR."

The agent executes authorized operations, verifies their results, and explains what it did.

## Architecture

```
Browser (Next.js) ──WebRTC──> LiveKit Server ──> Voice Agent (Python)
                                                      │
                                                      ├── Deepgram STT (speech-to-text)
                                                      ├── Groq LLM (Llama 3.3 70B reasoning)
                                                      ├── ElevenLabs TTS (text-to-speech)
                                                      └── Silero VAD (voice activity detection)
                                                      │
                                          FastAPI Backend ──> PostgreSQL / Redis
                                                │
                                                ├── Token generation
                                                ├── Tool execution layer
                                                ├── Permission & policy checks
                                                └── Result verification
```

| Layer | Technology |
|---|---|
| Real-time voice | LiveKit Agents, WebRTC |
| Agent runtime | Python 3.12, async |
| LLM | Groq (Llama 3.3 70B) — free tier |
| Speech-to-text | Deepgram — free tier |
| Text-to-speech | ElevenLabs — free tier |
| Backend API | FastAPI |
| Data | PostgreSQL (pgvector), Redis |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Infrastructure | Docker Compose (local), AWS (prod) |
| Testing | pytest, conversation simulations |

## Project Structure

```
voicd/
├── agent/                        # LiveKit Python voice agent
│   ├── main.py                   #   Agent entrypoint with STT/LLM/TTS pipeline
│   ├── tests/
│   │   └── test_agent_config.py  #   System prompt and config validation
│   ├── requirements.txt
│   └── Dockerfile
├── backend/                      # FastAPI API server
│   ├── app/
│   │   ├── main.py               #   FastAPI app with CORS
│   │   ├── config.py             #   Pydantic settings
│   │   └── api/routes/
│   │       └── token.py          #   LiveKit token generation
│   ├── tests/
│   │   ├── test_health.py        #   Health endpoint tests
│   │   └── test_token.py         #   Token generation tests (8 cases)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                     # Next.js web client
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          #   Main page — connect/disconnect flow
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   └── components/
│   │       └── VoiceAgent.tsx    #   Audio visualizer + live transcription
│   ├── package.json
│   └── tsconfig.json
├── benchmarks/                   # Performance benchmarks
│   ├── bench_token_latency.py    #   Token endpoint latency (p50/p95/p99)
│   ├── bench_groq_latency.py    #   LLM TTFT and total response time
│   ├── bench_conversation_sim.py #   10 scenario conversation simulations
│   └── metrics.py                #   Metrics collection utilities
├── docker-compose.yml            # LiveKit + PostgreSQL + Redis
├── livekit.yaml                  # Local LiveKit server config
├── .env.example                  # API key placeholders
└── README.md
```

## Quick Start

### 1. Get API Keys (all free)

| Service | Signup | What you get |
|---|---|---|
| Deepgram | https://console.deepgram.com | $200 free credit |
| ElevenLabs | https://elevenlabs.io | 10k chars/month |
| Groq | https://console.groq.com | Free tier (14.4K tokens/min) |

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 3. Start Infrastructure

```bash
docker compose up -d
```

This starts:
- **LiveKit server** on `ws://localhost:7880`
- **PostgreSQL** (with pgvector) on `localhost:5432`
- **Redis** on `localhost:6379`

### 4. Start the Voice Agent

```bash
cd agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py dev
```

### 5. Start the Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 6. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000, click **Start Conversation**, and speak.

## Testing

### Run All Tests

```bash
# Backend tests (8 tests)
cd backend
pytest tests/ -v

# Agent tests (6 tests)
pytest agent/tests/ -v

# Token latency benchmark
PYTHONPATH=backend pytest benchmarks/bench_token_latency.py -v -s --bench-rounds=50

# LLM latency benchmark (requires GROQ_API_KEY)
PYTHONPATH=backend pytest benchmarks/bench_groq_latency.py -v -s --bench-rounds=10

# Conversation simulations (requires GROQ_API_KEY)
PYTHONPATH=backend pytest benchmarks/bench_conversation_sim.py -v -s
```

### Test Coverage

| Suite | Tests | What it covers |
|---|---|---|
| `backend/tests/test_health.py` | 2 | Health endpoint, method validation |
| `backend/tests/test_token.py` | 6 | Token generation, JWT claims, grants, input validation |
| `agent/tests/test_agent_config.py` | 6 | System prompt content, capabilities, brevity enforcement |
| `benchmarks/bench_token_latency.py` | 1 | Token endpoint p50/p95/p99 latency |
| `benchmarks/bench_groq_latency.py` | 1 | LLM time-to-first-token and total response time |
| `benchmarks/bench_conversation_sim.py` | 10 | HR queries, confirmations, refusals, ambiguity, out-of-scope |

## Benchmarks

### Token Generation Latency (local, 50 rounds)

| Metric | Value |
|---|---|
| Mean | 1.35 ms |
| p50 | 1.23 ms |
| p95 | 1.85 ms |
| p99 | 5.06 ms |

### Conversation Simulation Scenarios

| Scenario | Tests |
|---|---|
| Attendance query | Keywords present in response |
| Minimum wage lookup | Domain-relevant answer |
| Payroll report generation | Confirmation before action |
| Compliance check | Relevant compliance info |
| Grievance ticket creation | Confirmation before action |
| Ambiguous request | Asks clarifying question |
| Out-of-scope request | Clear refusal |
| Multi-step task | Identifies required steps |
| Destructive action | Refuses to execute |
| Greeting | Appropriate response |

### Target Metrics (Milestone 3+)

| Metric | Target | Status |
|---|---|---|
| Response latency (p50) | < 1000ms end-of-speech to first audio | Pending |
| Response latency (p95) | < 2000ms | Pending |
| Task success rate | > 90% | Pending |
| Tool-call accuracy | > 95% | Pending |
| Recovery rate | > 80% | Pending |
| Permission enforcement | 100% | Pending |

## Design Principles

- **LLM never decides permissions.** Authorization is enforced in the backend. The LLM can request an action; the backend decides whether to allow it.
- **Confirm before acting.** Any operation that modifies data requires explicit user confirmation and creates an audit trail.
- **Voice-first responses.** Responses are concise (under 3 sentences) because they're spoken, not read.
- **Typed tool schemas.** Every tool has validated inputs, timeouts, retries, and result verification.
- **Measured, not demoed.** All claims are backed by reproducible benchmarks. Simulated and real results are clearly labelled.

## Roadmap

- [x] **Milestone 1** — Working voice agent with STT/LLM/TTS pipeline
- [ ] **Milestone 2** — 5-8 HR/payroll tools with agentic execution (LangGraph)
- [ ] **Milestone 3** — 100+ test conversations, evaluation suite
- [ ] **Milestone 4** — Production deployment, tracing dashboard, demo recording

## License

MIT
