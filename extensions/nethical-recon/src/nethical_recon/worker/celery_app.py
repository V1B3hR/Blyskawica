"""Celery application for worker queue."""

from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from nethical_recon.worker.config import get_worker_config

# Get configuration
config = get_worker_config()

# Create Celery app
celery_app = Celery(
    "nethical_recon",
    broker=config.broker_url,
    backend=config.result_backend,
    include=["nethical_recon.worker.tasks"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=config.task_time_limit,
    task_soft_time_limit=config.task_soft_time_limit,
    result_expires=config.result_expires,
    worker_prefetch_multiplier=config.worker_prefetch_multiplier,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Beat schedule
    beat_schedule={
        # Example: Run baseline update daily at 2 AM UTC
        "update-baselines-daily": {
            "task": "nethical_recon.worker.tasks.update_baselines",
            "schedule": crontab(hour=2, minute=0),
            "options": {"expires": 3600},
        },
        # Example: Clean up old results weekly
        "cleanup-old-results": {
            "task": "nethical_recon.worker.tasks.cleanup_old_results",
            "schedule": crontab(day_of_week=0, hour=3, minute=0),
            "options": {"expires": 7200},
        },
    },
    beat_schedule_filename=config.beat_schedule_filename,
)

# Enable eager mode for testing
if config.task_always_eager:
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
