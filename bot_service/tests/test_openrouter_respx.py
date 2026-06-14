import pytest
import respx
from httpx import Response
from app.services.openrouter_client import chat_completion
from app.core.config import settings


@pytest.mark.asyncio
@respx.mock
async def test_chat_completion_calls_openrouter():
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"

    sample = {
        "choices": [
            {"message": {"content": "Hello from OpenRouter"}}
        ]
    }

    route = respx.post(url).mock(return_value=Response(200, json=sample))

    text = await chat_completion("Hi")

    assert text == "Hello from OpenRouter"
    assert route.called
