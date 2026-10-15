# VoiceOps AI

Real-time agentic voice operations platform for HR/payroll/labour-compliance.

## Stack
- **Voice agent:** Python, LiveKit Agents SDK, Deepgram STT, ElevenLabs TTS, Groq LLM (Llama 3.3 70B)
- **Backend:** FastAPI, PostgreSQL (pgvector), Redis
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, @livekit/components-react
- **Infra:** Docker Compose (local), AWS (prod)

## Structure
```
agent/       — LiveKit Python voice agent
backend/     — FastAPI API server
frontend/    — Next.js web client
```

## Running locally
1. Copy `.env.example` to `.env` and fill in API keys
2. `docker compose up -d` — starts LiveKit server, Postgres, Redis
3. `cd agent && pip install -r requirements.txt && python main.py dev` — starts voice agent
4. `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload` — starts API
5. `cd frontend && npm install && npm run dev` — starts web UI at http://localhost:3000

## Key constraints
- LLM never decides permissions — enforce authorization in backend
- Sensitive operations require confirmation step + audit trail
- All tools must have typed schemas, input validation, timeouts, and retries
