"""GitHub API client — handles OAuth, user info, repo operations, and webhooks."""

import httpx

from app.config import get_settings

settings = get_settings()

GITHUB_API = "https://api.github.com"


class GitHubClient:
    """Wraps the GitHub REST API. Pass an access_token for authenticated requests."""

    def __init__(self, access_token: str = ""):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def exchange_code_for_token(self, code: str) -> dict:
        """Trade an OAuth code for an access token."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://github.com/login/oauth/access_token",
                json={
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_user(self) -> dict:
        """Fetch the authenticated user's profile."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{GITHUB_API}/user", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_repo(self, full_name: str) -> dict:
        """Get repo details. Raises on 404 or no access."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API}/repos/{full_name}", headers=self.headers
            )
            resp.raise_for_status()
            return resp.json()

    async def create_webhook(self, full_name: str, callback_url: str) -> dict:
        """Register a webhook on the repo for pull_request events."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GITHUB_API}/repos/{full_name}/hooks",
                headers=self.headers,
                json={
                    "name": "web",
                    "active": True,
                    "events": ["pull_request"],
                    "config": {
                        "url": callback_url,
                        "content_type": "json",
                        "secret": settings.github_webhook_secret,
                    },
                },
            )
            resp.raise_for_status()
            return resp.json()
