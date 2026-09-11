"""Tests for GitHub webhook HMAC signature verification."""

import hashlib
import hmac

import app.routers.webhooks as webhooks


def _sign(secret: str, payload: bytes) -> str:
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_valid_signature_passes(monkeypatch):
    secret = "test-secret"
    monkeypatch.setattr(webhooks.settings, "github_webhook_secret", secret)
    payload = b'{"action": "opened"}'
    signature = _sign(secret, payload)
    assert webhooks.verify_signature(payload, signature) is True


def test_wrong_signature_fails(monkeypatch):
    monkeypatch.setattr(webhooks.settings, "github_webhook_secret", "test-secret")
    payload = b'{"action": "opened"}'
    bad = _sign("some-other-secret", payload)
    assert webhooks.verify_signature(payload, bad) is False


def test_tampered_payload_fails(monkeypatch):
    secret = "test-secret"
    monkeypatch.setattr(webhooks.settings, "github_webhook_secret", secret)
    signature = _sign(secret, b'{"action": "opened"}')
    # Payload changed after signing
    assert webhooks.verify_signature(b'{"action": "closed"}', signature) is False


def test_empty_secret_skips_verification(monkeypatch):
    # Dev convenience: no secret configured means verification is skipped
    monkeypatch.setattr(webhooks.settings, "github_webhook_secret", "")
    assert webhooks.verify_signature(b"anything", "sha256=whatever") is True
