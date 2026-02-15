from celery import Celery
from applytrack.core.config import settings

celery_app = Celery(
    "applytrack",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["applytrack.workers.tasks_ai"]
)

celery_app.conf.task_track_started = True
celery_app.conf.task_always_eager = True # For local dev without running separate worker
