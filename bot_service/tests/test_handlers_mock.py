import asyncio
import pytest
from types import SimpleNamespace
import fakeredis.aioredis


class FakeMessage:
    def __init__(self, user_id: int, text: str):
        self.from_user = SimpleNamespace(id=user_id)
        self.text = text
        self._answers = []

    async def answer(self, text: str):
        self._answers.append(text)

    @property
    def answers(self):
        return self._answers


@pytest.mark.asyncio
async def test_token_command_saves_token(monkeypatch):
    from app.bot import handlers
    from jose import jwt
    from app.core.config import settings

    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    monkeypatch.setattr(handlers, "get_redis", lambda: fake)

    payload = {"sub": "1", "role": "user"}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

    msg = FakeMessage(user_id=1, text=f"/token {token}")

    await handlers.set_token(msg)

    stored = await fake.get("token_1")
    assert stored == token


@pytest.mark.asyncio
async def test_handle_no_token_does_not_call_celery(monkeypatch):
    from app.bot import handlers

    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(handlers, "get_redis", lambda: fake)

    called = False

    async def fake_delay(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(handlers.llm_request, "delay", fake_delay)

    msg = FakeMessage(user_id=2, text="hello")

    await handlers.handle_message(msg)

    assert not called
    assert any("Вы не авторизованы" in a for a in msg.answers)


@pytest.mark.asyncio
async def test_handle_with_token_calls_celery(monkeypatch):
    from app.bot import handlers
    from jose import jwt
    from app.core.config import settings

    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(handlers, "get_redis", lambda: fake)

    payload = {"sub": "3", "role": "user"}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    await fake.set("token_3", token)

    captured = {}

    def fake_delay(user_id, text):
        captured["args"] = (user_id, text)

    monkeypatch.setattr(handlers.llm_request, "delay", fake_delay)

    msg = FakeMessage(user_id=3, text="Tell me something")

    await handlers.handle_message(msg)

    assert captured.get("args") == (3, "Tell me something")
    assert any("Запрос принят" in a for a in msg.answers)
