"""Stats endpoint — returns overview numbers for the dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.repository import Repository
from app.models.review import Review
from app.models.finding import Finding
from app.utils.auth import get_current_user

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("")
async def get_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return high-level stats for the current user's repos."""
    # Count repos
    repo_count = await db.scalar(
        select(func.count(Repository.id)).where(Repository.owner_id == user.id)
    )

    # Get repo IDs for filtering
    repo_ids_stmt = select(Repository.id).where(Repository.owner_id == user.id)

    # Count reviews
    review_count = await db.scalar(
        select(func.count(Review.id)).where(
            Review.repository_id.in_(repo_ids_stmt)
        )
    )

    # Count findings by severity
    review_ids_stmt = select(Review.id).where(
        Review.repository_id.in_(repo_ids_stmt)
    )

    severity_rows = await db.execute(
        select(Finding.severity, func.count(Finding.id))
        .where(Finding.review_id.in_(review_ids_stmt))
        .group_by(Finding.severity)
    )
    severity_map = {row[0].value: row[1] for row in severity_rows}

    total_findings = sum(severity_map.values())

    return {
        "repos": repo_count or 0,
        "reviews": review_count or 0,
        "findings": total_findings,
        "by_severity": {
            "critical": severity_map.get("critical", 0),
            "high": severity_map.get("high", 0),
            "medium": severity_map.get("medium", 0),
            "low": severity_map.get("low", 0),
            "info": severity_map.get("info", 0),
        },
    }
