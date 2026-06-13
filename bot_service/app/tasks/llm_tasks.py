from celery import shared_task
import httpx
from app.core.config import settings


@shared_task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str):

    try:
        #openrouter
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
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        # tg
        httpx.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": tg_chat_id,
                "text": answer,
            },
        )

        return {"status": "ok"}

    except Exception as e:
        httpx.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": tg_chat_id,
                "text": "Ошибка при обработке запроса к LLM",
            },
        )

        return {"status": "error", "detail": str(e)}