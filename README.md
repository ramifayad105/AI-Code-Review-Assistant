# AI Code Review Assistant 🤖

AI-powered code review platform that automatically analyzes GitHub pull requests and posts inline feedback on bugs, security issues, and code quality — plus a dashboard for managing repos and browsing review history.

## How It Works

```
GitHub PR opened/updated
        │
        ▼
   Webhook ──► FastAPI Backend ──► AI Analysis ──► Posts comments on GitHub PR
                     │
                     ▼
                PostgreSQL (stores all reviews + findings)
                     │
                     ▲
                React Dashboard (manage repos, browse history, view stats)
```

1. User connects a GitHub repository via the dashboard
2. A webhook is registered on the repo for pull request events
3. When a PR is opened or updated, the backend fetches the diff
4. The AI analyzes the diff for bugs, security issues, performance problems, and style
5. Findings are posted as inline review comments directly on the GitHub PR
6. All reviews are stored and viewable in the dashboard

## Features

- 🔗 **GitHub Integration** — OAuth login, repo connection, webhook automation
- 🧠 **AI Analysis** — OpenAI GPT-4 (or local Ollama) reviews diffs for real issues
- 💬 **Inline PR Comments** — Findings posted directly on GitHub, no context switching
- 📊 **Dashboard** — Browse review history, filter by severity, view stats
- 🔒 **Security Detection** — SQL injection, XSS, hardcoded secrets, insecure patterns
- 🐳 **Dockerized** — Full Docker Compose setup for local dev and deployment
- ⚡ **Async** — Background processing so webhooks respond instantly

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11+) |
| Frontend | React + Next.js |
| Database | PostgreSQL |
| Cache/Queue | Redis |
| AI | OpenAI API / Ollama |
| Auth | GitHub OAuth + JWT |
| Containers | Docker + Docker Compose |
| Migrations | Alembic |
| Testing | pytest + httpx |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/github` | GitHub OAuth callback |
| GET | `/repos` | List connected repositories |
| POST | `/repos/connect` | Connect a GitHub repository |
| POST | `/webhooks/github` | GitHub webhook receiver |
| GET | `/reviews` | List all reviews |
| GET | `/reviews/{id}` | Get review details with findings |
| POST | `/reviews/trigger` | Manually trigger a review on a PR |

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- GitHub OAuth App (for login)
- OpenAI API key (or Ollama for local LLM)

### Setup

```bash
git clone https://github.com/yourusername/AI-Code-Review-Assistant.git
cd AI-Code-Review-Assistant
cp .env.example .env
# Fill in your credentials in .env

# Run everything
docker-compose up --build
```

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:3000

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── config.py          # Environment settings
│   │   ├── database.py        # SQLAlchemy async setup
│   │   ├── models/            # ORM models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API routes
│   │   └── services/          # Business logic (GitHub, AI, webhooks)
│   ├── alembic/               # Database migrations
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js pages
│   │   ├── components/        # React components
│   │   └── lib/               # API client, auth helpers
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── .env.example
```

## License

MIT
