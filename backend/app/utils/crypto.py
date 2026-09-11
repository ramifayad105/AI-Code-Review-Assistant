"""Symmetric encryption for secrets stored at rest (GitHub access tokens).

Uses Fernet (AES-128-CBC + HMAC). The key comes from settings.token_encryption_key.
If no key is configured, tokens are stored/read as plaintext so local dev still
works — a warning is logged once. Set TOKEN_ENCRYPTION_KEY in any real deployment.
"""

from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)

# Prefix marks a value as encrypted by this module so we can safely handle
# tokens that were stored before encryption was enabled.
_PREFIX = "enc::"


@lru_cache
def _fernet() -> Fernet | None:
    settings = get_settings()
    key = settings.token_encryption_key.strip()
    if not key:
        logger.warning(
            "TOKEN_ENCRYPTION_KEY not set — GitHub tokens stored unencrypted. "
            "Set it before deploying to production."
        )
        return None
    try:
        return Fernet(key.encode())
    except (ValueError, TypeError) as e:
        raise RuntimeError(
            "TOKEN_ENCRYPTION_KEY is invalid. Generate one with: "
            'python -c "from cryptography.fernet import Fernet; '
            'print(Fernet.generate_key().decode())"'
        ) from e


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token for storage. Returns plaintext unchanged if no key set."""
    if not plaintext:
        return plaintext
    f = _fernet()
    if f is None:
        return plaintext
    return _PREFIX + f.encrypt(plaintext.encode()).decode()


def decrypt_token(stored: str) -> str:
    """Decrypt a stored token. Handles legacy plaintext values transparently."""
    if not stored or not stored.startswith(_PREFIX):
        # Legacy plaintext token (stored before encryption was enabled)
        return stored
    f = _fernet()
    if f is None:
        # Key was removed after values were encrypted — nothing we can do
        raise RuntimeError(
            "Found an encrypted token but TOKEN_ENCRYPTION_KEY is not set."
        )
    try:
        return f.decrypt(stored[len(_PREFIX):].encode()).decode()
    except InvalidToken as e:
        raise RuntimeError("Failed to decrypt token — wrong encryption key?") from e
