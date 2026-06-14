import httpx
from typing import Any
from app.core.config import settings


class OpenRouterError(Exception):
    pass


async def chat_completion(prompt: str, timeout: int = 60) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": settings.OPENROUTER_SITE_URL,
                    "X-Title": settings.OPENROUTER_APP_NAME,
                },
                json={
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            
            # Извлекаем текст ответа
            return data["choices"][0]["message"]["content"]
            
        except httpx.TimeoutException:
            raise OpenRouterError("OpenRouter API timeout")
        except httpx.HTTPStatusError as e:
            raise OpenRouterError(f"OpenRouter API error: {e.response.status_code}")
        except Exception as e:
            raise OpenRouterError(f"OpenRouter API error: {str(e)}")
