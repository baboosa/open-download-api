from celery import Celery
from open_download_api.settings import settings

celery_app = Celery(
    "open_download_api",
    broker=f"redis://{settings.redis_host}:{settings.redis_port}/{settings.celery_broker_db}",
    backend=f"redis://{settings.redis_host}:{settings.redis_port}/{settings.celery_broker_db}",
    include=["open_download_api.tasks.download_task"],
)