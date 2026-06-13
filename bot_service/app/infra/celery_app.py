from bot_service.app.infra.celery_app import Celery
from app.core.config import settings


celery_app = Celery(
    "bot_service",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.llm_tasks"],
)

celery_app.autodiscover_tasks(["app.tasks"])


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)