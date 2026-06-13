import httpx
from typing import Any
from app.core.config import settings


class OpenRouterError(Exception):
    pass


def chat_completion(prompt: str, timeout: int = 60) -> str:
    try:
        response = httpx.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": settings.OPENROUTER_SITE_URL,
                "X-Title": settings.OPENROUTER_APP_NAME,
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )

        response.raise_for_status()
        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            raise OpenRouterError("Unexpected OpenRouter response format")

    except httpx.HTTPError as e:
        raise OpenRouterError(str(e))
