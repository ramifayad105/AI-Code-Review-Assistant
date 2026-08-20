"""Webhook endpoint — receives events from GitHub."""

import hashlib
import hmac

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.repository import Repository
from app.services.queue import enqueue_review

settings = get_settings()
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def verify_signature(payload: bytes, signature: str) -> bool:
    """Check that the webhook actually came from GitHub using HMAC."""
    if not settings.github_webhook_secret or settings.github_webhook_secret == "your-webhook-secret":
        return True  # skip verification in dev
    expected = hmac.new(
        settings.github_webhook_secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


@router.post("/github")
async def github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Receives pull_request events from GitHub.
    Pushes review job to Redis queue for the worker to pick up.
    """
    # Verify it's legit
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()

    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Bad signature")

    event_type = request.headers.get("X-GitHub-Event", "")
    payload = await request.json()

    # GitHub sends a ping when webhook is first created
    if event_type == "ping":
        return {"status": "pong"}

    # We only care about pull requests
    if event_type != "pull_request":
        return {"status": "ignored", "event": event_type}

    # Only review on open or new commits pushed
    action = payload.get("action")
    if action not in ("opened", "synchronize"):
        return {"status": "ignored", "action": action}

    # Make sure this repo is registered with us
    repo_github_id = payload["repository"]["id"]
    stmt = select(Repository).where(Repository.github_repo_id == repo_github_id)
    result = await db.execute(stmt)
    repo = result.scalar_one_or_none()

    if not repo:
        return {"status": "ignored", "reason": "repo not registered"}

    # Push to Redis queue (worker picks it up)
    pr_data = payload["pull_request"]
    await enqueue_review(
        repo_id=str(repo.id),
        owner_id=str(repo.owner_id),
        pr_number=pr_data["number"],
        pr_title=pr_data["title"],
        pr_author=pr_data["user"]["login"],
        commit_sha=pr_data["head"]["sha"],
        full_name=repo.full_name,
    )

    return {"status": "review_queued", "pr": pr_data["number"]}
