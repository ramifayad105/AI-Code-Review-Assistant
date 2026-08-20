"""Redis-based job queue for review tasks."""

import json

import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()

QUEUE_NAME = "review_jobs"


async def enqueue_review(
    repo_id: str,
    owner_id: str,
    pr_number: int,
    pr_title: str,
    pr_author: str,
    commit_sha: str,
    full_name: str,
):
    """Push a review job onto the Redis queue."""
    r = redis.from_url(settings.redis_url)
    job = json.dumps({
        "repo_id": repo_id,
        "owner_id": owner_id,
        "pr_number": pr_number,
        "pr_title": pr_title,
        "pr_author": pr_author,
        "commit_sha": commit_sha,
        "full_name": full_name,
    })
    await r.rpush(QUEUE_NAME, job)
    await r.aclose()
