import pytest
import fakeredis.aioredis
from app.infra import redis as redis_module


@pytest.fixture
def fake_redis(monkeypatch):
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    monkeypatch.setattr(
        redis_module,
        "get_redis",
        lambda: fake
    )

    return fake