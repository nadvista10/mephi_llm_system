import asyncio

from celery import shared_task
import httpx
from app.core.config import settings
from app.services.openrouter_client import chat_completion, OpenRouterError


@shared_task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str):
    try:
        answer = asyncio.run(chat_completion(prompt))

        # send to telegram
        httpx.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": tg_chat_id, "text": answer},
        )

        return {"status": "ok"}

    except OpenRouterError as e:
        httpx.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": tg_chat_id, "text": "Ошибка при обработке запроса к LLM"},
        )
        return {"status": "error", "detail": str(e)}

    except Exception as e:
        return {"status": "error", "detail": str(e)}