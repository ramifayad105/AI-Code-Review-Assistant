"""Middleware for rate limiting and error handling."""

import time
from collections import defaultdict

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter.
    Tracks requests per IP and blocks if they exceed the limit.
    In production you'd use Redis for this (works across multiple instances).
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0  # 1 minute

        # Clean old entries
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if now - t < window
        ]

        # Check limit
        if len(self.requests[client_ip]) >= self.rpm:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Try again in a minute."},
            )

        # Record this request
        self.requests[client_ip].append(now)
        return await call_next(request)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catches unhandled exceptions and returns clean JSON errors."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            raise  # Let FastAPI handle these normally
        except Exception as e:
            # Log it (in production use proper logging)
            print(f"[error] Unhandled: {type(e).__name__}: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
