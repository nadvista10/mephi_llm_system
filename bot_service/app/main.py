from fastapi import FastAPI
import asyncio
import logging
from app.infra.celery_app import celery_app
from app.bot.dispatcher import dp, bot


app = FastAPI(title="Bot Service")


@app.on_event("startup")
async def on_startup():
    if getattr(bot, "token", None):
        print("Starting aiogram polling, bot token present")
        print("bot.token=", getattr(bot, "token", None))
        loop = asyncio.get_event_loop()
        app.state._bot_polling_task = loop.create_task(
            dp.start_polling(bot, skip_updates=True)
        )
        print("Started aiogram polling task")
    else:
        print("Bot token not configured; skipping aiogram polling startup")


@app.on_event("shutdown")
async def on_shutdown():
    try:
        await dp.stop_polling()
    except Exception:
        pass
    try:
        await bot.session.close()
    except Exception:
        pass
    task = getattr(app.state, "_bot_polling_task", None)
    if task:
        task.cancel()


@app.get("/health")
async def health():
    return {"status": "ok"}