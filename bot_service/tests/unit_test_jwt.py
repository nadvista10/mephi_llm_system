import pytest
from jose import jwt
from app.core import jwt as jwt_module
from app.core.config import settings


def test_decode_and_validate_valid_token():
    payload = {"sub": "42", "role": "user"}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

    decoded = jwt_module.decode_and_validate(token)

    assert decoded["sub"] == payload["sub"]
    assert decoded["role"] == payload["role"]


def test_decode_and_validate_invalid_token():
    with pytest.raises(ValueError):
        jwt_module.decode_and_validate("not-a-token")
