# AI Code Review Assistant 🤖

AI-powered code review platform that automatically analyzes GitHub pull requests and generates security, performance, and style recommendations with inline feedback.

## Features

- 🔗 **GitHub Integration** — Connect repositories via OAuth, receive PR webhooks
- 🧠 **AI-Powered Analysis** — Uses OpenAI GPT-4 (or local Ollama) to find bugs, security issues, and code smells
- 📝 **Inline PR Comments** — Posts review comments directly on GitHub PRs
- 🔒 **Security Scanning** — Detects common vulnerabilities (SQL injection, XSS, hardcoded secrets)
- 📊 **Review Dashboard** — Browse review history with severity filtering
- 🐳 **Dockerized** — Full Docker Compose setup for local dev and deployment
- ⚡ **Async Processing** — Background task queue for non-blocking reviews

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11+) |
| Database | PostgreSQL 15 |
| Cache/Queue | Redis 7 |
| AI | OpenAI API / Ollama |
| Auth | GitHub OAuth + JWT |
| Containers | Docker + Docker Compose |
| Migrations | Alembic |
| Testing | pytest + httpx |

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Settings / environment config
│   ├── database.py          # SQLAlchemy async engine + session
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic layer
│   │   ├── github.py        # GitHub API client
│   │   ├── ai_reviewer.py   # LLM integration
│   │   └── webhook.py       # Webhook processing
│   └── utils/               # Helpers, auth, etc.
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- GitHub account (for OAuth app)
- OpenAI API key (or Ollama installed locally)

### 1. Clone and configure

```bash
git clone https://github.com/yourusername/AI-Code-Review-Assistant.git
cd AI-Code-Review-Assistant
cp .env.example .env
# Edit .env with your credentials
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### 3. Run locally (development)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/github` | GitHub OAuth callback |
| GET | `/repos` | List connected repositories |
| POST | `/repos/connect` | Connect a GitHub repository |
| POST | `/webhooks/github` | GitHub webhook receiver |
| GET | `/reviews` | List all reviews |
| GET | `/reviews/{id}` | Get review details with findings |
| POST | `/reviews/trigger` | Manually trigger a review |

## Environment Variables

See `.env.example` for all required configuration.

## License

MIT
