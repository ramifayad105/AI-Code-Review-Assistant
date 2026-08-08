"""
Review pipeline — orchestrates the full flow:
fetch diff → AI analysis → store findings → post comments.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.review import Review, ReviewStatus
from app.models.finding import Finding, Severity, FindingCategory
from app.services.github import GitHubClient
from app.services.ai_reviewer import AIReviewer


async def run_review(
    repo_id: str,
    owner_id: str,
    pr_number: int,
    pr_title: str,
    pr_author: str,
    commit_sha: str,
    full_name: str,
):
    """
    Runs the full review pipeline. Called as a background task.
    Gets its own DB session since it runs outside the request lifecycle.
    """
    async with AsyncSessionLocal() as db:
        # Get the repo owner's access token for GitHub API calls
        stmt = select(User).where(User.id == UUID(owner_id))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return

        # Create a review record
        review = Review(
            repository_id=UUID(repo_id),
            pr_number=pr_number,
            pr_title=pr_title,
            pr_author=pr_author,
            commit_sha=commit_sha,
            status=ReviewStatus.IN_PROGRESS,
        )
        db.add(review)
        await db.flush()

        try:
            # 1. Fetch the diff from GitHub
            github = GitHubClient(access_token=user.access_token)
            diff = await github.get_pr_diff(full_name, pr_number)

            # 2. Send to AI for analysis
            reviewer = AIReviewer()
            ai_result = await reviewer.review_diff(diff, pr_title)

            # 3. Store findings in DB
            review.summary = ai_result.get("summary", "")
            for f in ai_result.get("findings", []):
                finding = Finding(
                    review_id=review.id,
                    file_path=f["file_path"],
                    line_number=f["line_number"],
                    severity=Severity(f["severity"]),
                    category=FindingCategory(f["category"]),
                    title=f["title"],
                    description=f["description"],
                    suggestion=f.get("suggestion"),
                    code_snippet=f.get("code_snippet"),
                )
                db.add(finding)

            # 4. Post comments on the PR
            if ai_result.get("findings"):
                comments = []
                for f in ai_result["findings"]:
                    body = (
                        f"**{f['severity'].upper()}** — {f['title']}\n\n"
                        f"{f['description']}\n\n"
                    )
                    if f.get("suggestion"):
                        body += f"**Suggestion:** {f['suggestion']}"
                    comments.append({
                        "path": f["file_path"],
                        "line": f["line_number"],
                        "body": body,
                    })

                await github.post_review(
                    full_name=full_name,
                    pr_number=pr_number,
                    body=f"## AI Code Review\n\n{review.summary}",
                    comments=comments,
                )

            review.status = ReviewStatus.COMPLETED
            review.completed_at = datetime.utcnow()

        except Exception as e:
            review.status = ReviewStatus.FAILED
            review.summary = f"Review failed: {str(e)}"

        await db.commit()
