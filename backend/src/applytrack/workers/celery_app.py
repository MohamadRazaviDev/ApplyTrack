"""Celery app wired to Redis."""

from celery import Celery

from applytrack.core.config import settings

celery_app = Celery(
    "applytrack",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["applytrack.workers.tasks_ai"],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # When True tasks run synchronously inside the API process — handy
    # for local dev if you don't want to spin up a separate worker.
    task_always_eager=settings.celery_always_eager,
)
