# Итоговый проект. Двухсервисная система LLM-консультаций

Архитектура:
- Auth service - регистрация, логин, JWT. 
- Bot service - Telegram-бот, очередь задач через RabbitMQ и Celery, Redis для хранения токенов и кеша.

Быстрый запуск (docker)
1. Убедитесь, что Docker запущен.
2. В корне проекта:

```
docker compose up --build
```

Тесты
- Запуск тестов для сервиса:

```
cd auth_service
pytest -q

cd bot_service
pytest -q
```

Переменные окружения
- Каждая служба читает переменные окружения.
- Важно: не забудьте определить `JWT_SECRET`, `REDIS_URL`, `RABBITMQ_URL`, `TELEGRAM_BOT_TOKEN`, `OPENROUTER_API_KEY`.

Скриншоты

- **RabbitMQ (граф очереди):** [![RabbitMQ](Screenshots/Rabbit.png)](Screenshots/Rabbit.png)
- **Чат бота:** [![Чат](Screenshots/Chat.png)](Screenshots/Chat.png)
- **Тесты бота:** [![Bot Tests](Screenshots/Bot%20Tests.png)](Screenshots/Bot%20Tests.png)
- **Тесты auth_service:** [![Auth Tests](Screenshots/Auth%20Tests.png)](Screenshots/Auth%20Tests.png)
- **Регистрация:** [![Register](Screenshots/Register.png)](Screenshots/Register.png)
- **Логин:** [![Login](Screenshots/Login.png)](Screenshots/Login.png)
- **Информация о пользователе (me):** [![Me](Screenshots/Me.png)](Screenshots/Me.png)