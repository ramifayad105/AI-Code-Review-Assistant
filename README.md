# AI Code Review Assistant

Automated code review tool that hooks into GitHub pull requests, runs diffs through GPT-4, and posts findings as inline comments. No manual triggering — connect a repo and it reviews every PR automatically.

## Overview

```
PR opened → GitHub webhook → FastAPI backend → AI analysis → comments posted on PR
                                    │
                                    └── stored in Postgres ← Dashboard reads from here
```

The backend does the heavy lifting. The dashboard is a management layer for connecting repos and browsing past reviews.

## Stack

- **Backend:** FastAPI, SQLAlchemy (async), Alembic
- **Database:** PostgreSQL
- **Cache:** Redis
- **AI:** OpenAI GPT-4 (Ollama supported as local alternative)
- **Auth:** GitHub OAuth → JWT
- **Infra:** Docker Compose
- **Frontend:** React / Next.js (planned)

## Setup

### Requirements

- Python 3.11+
- Docker & Docker Compose
- A GitHub OAuth App ([create one here](https://github.com/settings/applications/new))
- OpenAI API key

### GitHub OAuth App setup

1. Go to GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
2. Set homepage URL to `http://localhost:3000`
3. Set callback URL to `http://localhost:3000/auth/callback`
4. Copy the Client ID and Client Secret into your `.env`

### Running locally

```bash
cp .env.example .env
# Fill in GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, OPENAI_API_KEY

docker-compose up --build
```

API: http://localhost:8000
Docs: http://localhost:8000/docs

Apply database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

## Project structure

```
backend/
├── app/
│   ├── main.py              # App entry, router registration
│   ├── config.py            # Env-based settings
│   ├── database.py          # Async SQLAlchemy engine
│   ├── models/              # ORM models (user, repo, review, finding)
│   ├── routers/             # API endpoints
│   ├── services/            # GitHub client, AI reviewer
│   └── utils/               # JWT auth helpers
├── alembic/                 # Migrations
├── Dockerfile
└── requirements.txt
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/github | OAuth login, returns JWT |
| GET | /auth/me | Current user profile |
| GET | /repos | List connected repos |
| POST | /repos/connect | Register a repo + set up webhook |
| POST | /webhooks/github | Receives PR events from GitHub |
| GET | /reviews | Review history |
| GET | /reviews/:id | Review detail with findings |
| POST | /reviews/trigger | Manually kick off a review |

## Status

Work in progress. Building in phases:

- [x] Project scaffolding + Docker Compose
- [x] Database models + migrations
- [x] GitHub OAuth login
- [ ] Repository connection + webhook setup
- [ ] Webhook processing + AI review pipeline
- [ ] Dashboard (Next.js)
- [ ] Background job queue
- [ ] CI/CD + deployment

## License

MIT
