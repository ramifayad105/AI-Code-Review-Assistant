"""Central logging configuration.

Call configure_logging() once at process startup (API and worker both do this).
Use get_logger(__name__) everywhere else instead of print().
"""

import logging
import sys

from app.config import get_settings

settings = get_settings()

_configured = False


def configure_logging() -> None:
    """Set up root logging. Idempotent — safe to call more than once."""
    global _configured
    if _configured:
        return

    level = logging.DEBUG if settings.debug else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers if uvicorn already added some
    root.handlers = [handler]

    # Quiet down noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger, ensuring logging is configured first."""
    configure_logging()
    return logging.getLogger(name)
