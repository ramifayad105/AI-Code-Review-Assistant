"""Tests for token encryption/decryption at rest."""

import pytest
from cryptography.fernet import Fernet

import app.utils.crypto as crypto


@pytest.fixture
def with_key(monkeypatch):
    """Configure a real Fernet key and reset the cached instance."""
    key = Fernet.generate_key().decode()
    monkeypatch.setattr(crypto.get_settings(), "token_encryption_key", key)
    crypto._fernet.cache_clear()
    yield key
    crypto._fernet.cache_clear()


@pytest.fixture
def without_key(monkeypatch):
    """Simulate no encryption key configured (dev mode)."""
    monkeypatch.setattr(crypto.get_settings(), "token_encryption_key", "")
    crypto._fernet.cache_clear()
    yield
    crypto._fernet.cache_clear()


def test_roundtrip_with_key(with_key):
    original = "gho_supersecrettoken123"
    encrypted = crypto.encrypt_token(original)
    assert encrypted != original
    assert encrypted.startswith("enc::")
    assert crypto.decrypt_token(encrypted) == original


def test_encrypt_is_nondeterministic(with_key):
    # Fernet includes a random IV, so two encryptions differ
    a = crypto.encrypt_token("same-value")
    b = crypto.encrypt_token("same-value")
    assert a != b
    assert crypto.decrypt_token(a) == crypto.decrypt_token(b) == "same-value"


def test_no_key_stores_plaintext(without_key):
    original = "gho_token"
    stored = crypto.encrypt_token(original)
    assert stored == original
    assert crypto.decrypt_token(stored) == original


def test_decrypt_legacy_plaintext_with_key(with_key):
    # A token stored before encryption was enabled has no prefix
    assert crypto.decrypt_token("legacy-plaintext-token") == "legacy-plaintext-token"


def test_empty_token_passthrough(with_key):
    assert crypto.encrypt_token("") == ""
    assert crypto.decrypt_token("") == ""
