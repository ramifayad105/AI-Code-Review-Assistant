"""Routes for browsing review history and findings."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.review import Review
from app.models.repository import Repository
from app.utils.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


class FindingOut(BaseModel):
    id: str
    file_path: str
    line_number: int
    severity: str
    category: str
    title: str
    description: str
    suggestion: str | None
    code_snippet: str | None

    class Config:
        from_attributes = True


class ReviewOut(BaseModel):
    id: str
    pr_number: int
    pr_title: str
    pr_author: str
    status: str
    summary: str | None
    created_at: str
    completed_at: str | None
    repo_full_name: str

    class Config:
        from_attributes = True


class ReviewDetailOut(ReviewOut):
    findings: list[FindingOut] = []


@router.get("", response_model=list[ReviewOut])
async def list_reviews(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all reviews across the user's connected repos."""
    stmt = (
        select(Review)
        .join(Repository)
        .where(Repository.owner_id == user.id)
        .order_by(Review.created_at.desc())
    )
    result = await db.execute(stmt)
    reviews = result.scalars().all()

    # Need repo full_name for display
    repo_ids = {r.repository_id for r in reviews}
    repos_stmt = select(Repository).where(Repository.id.in_(repo_ids))
    repos_result = await db.execute(repos_stmt)
    repo_map = {r.id: r.full_name for r in repos_result.scalars().all()}

    return [
        ReviewOut(
            id=str(r.id),
            pr_number=r.pr_number,
            pr_title=r.pr_title,
            pr_author=r.pr_author,
            status=r.status.value if hasattr(r.status, "value") else r.status,
            summary=r.summary,
            created_at=r.created_at.isoformat(),
            completed_at=r.completed_at.isoformat() if r.completed_at else None,
            repo_full_name=repo_map.get(r.repository_id, ""),
        )
        for r in reviews
    ]


@router.get("/{review_id}", response_model=ReviewDetailOut)
async def get_review(
    review_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single review with all its findings."""
    stmt = (
        select(Review)
        .options(selectinload(Review.findings))
        .join(Repository)
        .where(Review.id == review_id, Repository.owner_id == user.id)
    )
    result = await db.execute(stmt)
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Get repo name
    repo_stmt = select(Repository).where(Repository.id == review.repository_id)
    repo_result = await db.execute(repo_stmt)
    repo = repo_result.scalar_one()

    return ReviewDetailOut(
        id=str(review.id),
        pr_number=review.pr_number,
        pr_title=review.pr_title,
        pr_author=review.pr_author,
        status=review.status.value if hasattr(review.status, "value") else review.status,
        summary=review.summary,
        created_at=review.created_at.isoformat(),
        completed_at=review.completed_at.isoformat() if review.completed_at else None,
        repo_full_name=repo.full_name,
        findings=[
            FindingOut(
                id=str(f.id),
                file_path=f.file_path,
                line_number=f.line_number,
                severity=f.severity.value if hasattr(f.severity, "value") else f.severity,
                category=f.category.value if hasattr(f.category, "value") else f.category,
                title=f.title,
                description=f.description,
                suggestion=f.suggestion,
                code_snippet=f.code_snippet,
            )
            for f in review.findings
        ],
    )
