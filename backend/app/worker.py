"""
Background worker — processes review jobs from Redis queue.
Run separately from the API: python -m app.worker
"""

import asyncio
import json

import redis.asyncio as redis

from app.config import get_settings
from app.services.review_pipeline import run_review

settings = get_settings()

QUEUE_NAME = "review_jobs"


async def process_jobs():
    """Main loop — pulls jobs from Redis and runs reviews."""
    r = redis.from_url(settings.redis_url)
    print(f"[worker] Listening for jobs on '{QUEUE_NAME}'...")

    while True:
        # BLPOP blocks until a job is available (timeout 0 = wait forever)
        result = await r.blpop(QUEUE_NAME, timeout=0)
        if not result:
            continue

        _, raw = result
        try:
            job = json.loads(raw)
            print(f"[worker] Processing review for PR #{job['pr_number']} on {job['full_name']}")
            await run_review(
                repo_id=job["repo_id"],
                owner_id=job["owner_id"],
                pr_number=job["pr_number"],
                pr_title=job["pr_title"],
                pr_author=job["pr_author"],
                commit_sha=job["commit_sha"],
                full_name=job["full_name"],
            )
            print(f"[worker] Done with PR #{job['pr_number']}")
        except Exception as e:
            print(f"[worker] Job failed: {e}")


if __name__ == "__main__":
    asyncio.run(process_jobs())
