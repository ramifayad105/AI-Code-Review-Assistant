"""
Background worker — processes review jobs from Redis queue.
Run separately from the API: python -m app.worker
"""

import asyncio
import json

import redis.asyncio as redis

from app.config import get_settings
from app.logging_config import get_logger
from app.services.review_pipeline import run_review

settings = get_settings()
logger = get_logger(__name__)

QUEUE_NAME = "review_jobs"
DEAD_LETTER_QUEUE = "review_jobs:dead"
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 5


async def _handle_job(r: redis.Redis, raw: bytes) -> None:
    """Run one review job with retries. Dead-letters after MAX_ATTEMPTS."""
    try:
        job = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Dropping malformed job payload: %r", raw)
        return

    attempts = int(job.get("_attempts", 0))

    for attempt in range(attempts + 1, MAX_ATTEMPTS + 1):
        try:
            logger.info(
                "Processing review for PR #%s on %s (attempt %s/%s)",
                job["pr_number"], job["full_name"], attempt, MAX_ATTEMPTS,
            )
            await run_review(
                repo_id=job["repo_id"],
                owner_id=job["owner_id"],
                pr_number=job["pr_number"],
                pr_title=job["pr_title"],
                pr_author=job["pr_author"],
                commit_sha=job["commit_sha"],
                full_name=job["full_name"],
            )
            logger.info("Done with PR #%s", job["pr_number"])
            return
        except Exception as e:
            logger.warning(
                "Job for PR #%s failed on attempt %s/%s: %s",
                job.get("pr_number"), attempt, MAX_ATTEMPTS, e,
            )
            if attempt < MAX_ATTEMPTS:
                await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)

    # Exhausted retries — push to dead-letter queue for later inspection
    job["_attempts"] = MAX_ATTEMPTS
    await r.rpush(DEAD_LETTER_QUEUE, json.dumps(job))
    logger.error(
        "Job for PR #%s exhausted retries; moved to dead-letter queue",
        job.get("pr_number"),
    )


async def process_jobs():
    """Main loop — pulls jobs from Redis and runs reviews."""
    r = redis.from_url(settings.redis_url)
    logger.info("Listening for jobs on '%s'...", QUEUE_NAME)

    try:
        while True:
            # BLPOP blocks until a job is available (timeout 0 = wait forever)
            result = await r.blpop(QUEUE_NAME, timeout=0)
            if not result:
                continue

            _, raw = result
            await _handle_job(r, raw)
    finally:
        await r.aclose()


if __name__ == "__main__":
    asyncio.run(process_jobs())
