"""Authentication routes — GitHub OAuth login flow."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.github import GitHubClient
from app.utils.auth import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# --- Request/Response schemas ---


class GitHubLoginRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    email: str | None
    avatar_url: str | None

    class Config:
        from_attributes = True


# --- Routes ---


@router.post("/github", response_model=TokenResponse)
async def github_login(
    request: GitHubLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    GitHub OAuth callback.

    Flow:
    1. Frontend redirects user to GitHub's OAuth page
    2. GitHub redirects back to frontend with a `code`
    3. Frontend sends the code here
    4. We exchange it for a GitHub access token
    5. Fetch user profile from GitHub
    6. Create or update user in our database
    7. Return our own JWT token
    """
    # Exchange code for GitHub token
    github = GitHubClient()
    token_data = await github.exchange_code_for_token(request.code)

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Invalid OAuth code")

    # Fetch GitHub user profile
    github = GitHubClient(access_token=access_token)
    github_user = await github.get_user()

    # Create or update user in DB
    stmt = select(User).where(User.github_id == github_user["id"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        # Update existing user
        user.access_token = access_token
        user.username = github_user["login"]
        user.avatar_url = github_user.get("avatar_url")
    else:
        # Create new user
        user = User(
            github_id=github_user["id"],
            username=github_user["login"],
            email=github_user.get("email"),
            avatar_url=github_user.get("avatar_url"),
            access_token=access_token,
        )
        db.add(user)

    await db.flush()

    # Return our JWT
    jwt_token = create_access_token(str(user.id))
    return TokenResponse(access_token=jwt_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
    )
