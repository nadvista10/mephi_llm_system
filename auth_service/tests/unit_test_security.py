import pytest

from app.core import security


def test_hash_and_verify_password():
    password = "S3cret!Pass"
    hashed = security.hash_password(password)

    assert hashed != password
    assert security.verify_password(password, hashed)
    assert not security.verify_password("wrong", hashed)


def test_create_and_decode_token():
    data = {"sub": "123", "role": "user"}
    token = security.create_access_token(data)

    payload = security.decode_token(token)

    assert "sub" in payload
    assert "role" in payload
    assert "iat" in payload
    assert "exp" in payload

    assert payload["sub"] == data["sub"]
    assert payload["role"] == data["role"]
