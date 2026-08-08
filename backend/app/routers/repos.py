"""Routes for connecting and listing GitHub repositories."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.repository import Repository
from app.services.github import GitHubClient
from app.utils.auth import get_current_user
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/repos", tags=["Repositories"])


class ConnectRepoRequest(BaseModel):
    full_name: str  # format: "owner/repo"


class RepoResponse(BaseModel):
    id: str
    full_name: str
    name: str
    webhook_active: bool

    class Config:
        from_attributes = True


@router.get("", response_model=list[RepoResponse])
async def list_repos(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all repos the current user has connected."""
    stmt = select(Repository).where(Repository.owner_id == user.id)
    result = await db.execute(stmt)
    repos = result.scalars().all()
    return [
        RepoResponse(
            id=str(r.id),
            full_name=r.full_name,
            name=r.name,
            webhook_active=r.webhook_active,
        )
        for r in repos
    ]


@router.post("/connect", response_model=RepoResponse)
async def connect_repo(
    body: ConnectRepoRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Connect a GitHub repo for automated reviews.
    Checks access, saves to DB, and sets up a webhook.
    """
    github = GitHubClient(access_token=user.access_token)

    # Make sure the user actually has access to this repo
    try:
        repo_data = await github.get_repo(body.full_name)
    except Exception:
        raise HTTPException(status_code=404, detail="Repo not found or no access")

    # Don't allow duplicates
    existing = await db.execute(
        select(Repository).where(Repository.github_repo_id == repo_data["id"])
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Repo already connected")

    # Try to set up the webhook (needs admin/write access on the repo)
    webhook_id = None
    webhook_active = False
    try:
        # In production this would be your real domain
        callback = f"https://your-domain.com/webhooks/github"
        hook_data = await github.create_webhook(body.full_name, callback)
        webhook_id = hook_data["id"]
        webhook_active = True
    except Exception:
        # Not a dealbreaker — user might not have admin access
        # They can still trigger reviews manually
        pass

    repo = Repository(
        github_repo_id=repo_data["id"],
        full_name=repo_data["full_name"],
        name=repo_data["name"],
        owner_id=user.id,
        webhook_active=webhook_active,
        webhook_id=webhook_id,
    )
    db.add(repo)
    await db.flush()

    return RepoResponse(
        id=str(repo.id),
        full_name=repo.full_name,
        name=repo.name,
        webhook_active=repo.webhook_active,
    )
