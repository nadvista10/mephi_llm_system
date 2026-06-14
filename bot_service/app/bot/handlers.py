import traceback
from aiogram import Router, types
from aiogram.filters import Command
from app.infra.redis import get_redis
from app.core.jwt import decode_and_validate
from app.tasks.llm_tasks import llm_request
import asyncio
from kombu.exceptions import OperationalError


router = Router()


def _token_key(user_id: int) -> str:
    return f"token_{user_id}"


@router.message(Command("token"))
async def set_token(message: types.Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Использование: /token <JWT>")
        return

    token = args[1]
    user_id = message.from_user.id

    try:
        #validate JWT
        payload = decode_and_validate(token)

        if "sub" not in payload:
            await message.answer("Невалидный токен")
            return

        # save to redis
        redis = get_redis()
        await redis.set(_token_key(user_id), token)

        await message.answer("Токен сохранён")

    except Exception:
        await message.answer("Невалидный или истёкший токен")


@router.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    redis = get_redis()

    # get token
    token = await redis.get(_token_key(user_id))

    if not token:
        await message.answer(
            "Вы не авторизованы.\n"
            "Получите JWT в Auth Service и отправьте его командой /token"
        )
        return

    # validate token
    try:
        payload = decode_and_validate(token)
    except Exception:
        await message.answer(
            "Токен недействителен или истёк\n"
            "Обновите его через /token"
        )
        return

    try:
        llm_request.delay(user_id, text)
    except Exception as exc:
        traceback.print_exc()
        await message.answer(
                "Сервис очередей недоступен — попробуйте позже."
            )
        return

    await message.answer("Запрос принят, обрабатываю...")