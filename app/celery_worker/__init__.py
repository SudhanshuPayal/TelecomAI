from celery import Celery
from ..config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Define the Celery instance here
celery = Celery(
    __name__,
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['app.celery_worker.celery_worker'] # Point to the file containing tasks
)

# Import tasks *after* the celery object is defined.
# This registers the tasks with the celery instance.
from . import celery_worker

__all__ = ['celery', 'celery_worker']