import jwt

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_and_verify_password() -> None:
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_verify_legacy_plaintext_password() -> None:
    assert verify_password("secret123", "secret123") is True
    assert verify_password("secret123", "other") is False


def test_create_access_token_contains_claims() -> None:
    token = create_access_token("user-id", extra_claims={"email": "a@example.com"})
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == "user-id"
    assert payload["email"] == "a@example.com"
    assert "exp" in payload


def test_decode_access_token_roundtrip() -> None:
    token = create_access_token("user-id", extra_claims={"email": "a@example.com"})
    payload = decode_access_token(token)
    assert payload["sub"] == "user-id"
    assert payload["email"] == "a@example.com"

