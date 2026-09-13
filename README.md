# RAG Chatbot with Live Human Handoff 

This is a support chatbot I built from scratch to actually learn how these things work end to end , not just 'call an API',  but the real pieces behind a production chatbot: retrieval, live search, confidence scoring, event streaming, and human escalation.

Try it here: https://rag-my-chatbot.onrender.com/api/chat-ui/

It's a light, pastel-doodle-themed chat window. Ask it anything, it'll answer from its own knowledge base when it can, and go pull real, current info from the web when it needs to (weather, news, prices, whatever's actually happening right now).

---

## What it actually does

- Answers from real documents — I gave it a small knowledge base, and it retrieves the relevant bits using semantic search rather than just keyword matching.
- Knows when it doesn't know — every answer gets a confidence score, using both how close the retrieved match was and the model's own honest self-assessment.
- Goes and checks the internet when it needs to — if you ask something time-sensitive, it doesn't guess from stale training data, it actually searches and tells you what's true right now.
- Notices when someone's frustrated — and quietly flags that conversation as needing a human.
- Actually pages a human — a real Slack message goes out the moment something needs attention, and there's a live dashboard that updates itself with no refresh, so an agent could genuinely watch it happen.
- Runs on a real event pipeline — every message goes through Kafka, and three separate little programs react to it independently (stats, sentiment, escalation) — which is the actual point of using something like Kafka instead of just doing everything in one function.
- Is genuinely live — not a localhost demo. It's deployed for real, on free-tier services, reachable from any device.

## How it's put together
You, in a browser
│
▼
Django backend
│
├─ looks up relevant info in Postgres (pgvector)
├─ asks Gemini to answer (pulling in live search results when needed)
└─ fires off an event ──► Kafka ──► three independent listeners:
├─ one just counts things
├─ one checks the mood
└─ one decides if a human's needed ──► Slack ping
└─► live dashboard update


## Built with

Django + DRF for the backend, Postgres with pgvector for semantic search (hosted on Supabase), Redis for the real-time dashboard (Upstash), Kafka for the event pipeline (local, via Docker), Gemini for the actual AI, Tavily for live web search, and Slack webhooks for the human-handoff alerts. Deployed on Render.

## Running it yourself

You'll need Python 3.11+, Docker Desktop, and free API keys for Gemini and Tavily.

```bash
git clone https://github.com/Karishma-r-h/rag-my-chatbot.git
cd rag-my-chatbot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

docker compose up -d          # spins up Postgres, Redis, Kafka

# add your .env file (see below), then:
python manage.py migrate
python manage.py runserver
```

Chat with it at `http://127.0.0.1:8000/api/chat-ui/`, and watch the live dashboard at `http://127.0.0.1:8000/api/dashboard/`.

To see the full event pipeline actually running, open three more terminals for:

bash
python manage.py run_analytics_consumer
python manage.py run_sentiment_consumer
python manage.py run_escalation_consumer


## Your '.env' file needs

GEMINI_API_KEY=
TAVILY_API_KEY=
DATABASE_URL=
REDIS_URL=
SLACK_WEBHOOK_URL=


## One honest note

Kafka only runs locally, on my own laptop via Docker — it's not part of the actual deployed site. Free hosting tiers don't really have room for a full Kafka broker running alongside everything else, and the point of including it here was to learn and demonstrate the architecture, not to run it in production. The live site quietly skips Kafka publishing if it's not available, so the core chatbot works either way.

