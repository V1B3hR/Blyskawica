"""Worker configuration."""

from __future__ import annotations

from dataclasses import dataclass

from nethical_recon.secrets import get_secrets_manager


@dataclass
class WorkerConfig:
    """Configuration for worker and task execution."""

    # Celery broker settings
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/0"

    # Task execution settings
    task_always_eager: bool = False
    task_eager_propagates: bool = True

    # Worker concurrency
    worker_concurrency: int = 4
    worker_prefetch_multiplier: int = 1

    # Task routing
    task_routes: dict[str, dict[str, str]] | None = None

    # Task time limits (in seconds)
    task_soft_time_limit: int = 3600  # 1 hour
    task_time_limit: int = 7200  # 2 hours

    # Result expiration (in seconds)
    result_expires: int = 86400  # 24 hours

    # Beat schedule settings
    beat_schedule_filename: str = "/tmp/celerybeat-schedule"


def get_worker_config() -> WorkerConfig:
    """Get worker configuration from secrets manager."""
    secrets = get_secrets_manager()

    return WorkerConfig(
        broker_url=secrets.get("CELERY_BROKER_URL", secrets.get("BROKER_URL", "redis://localhost:6379/0")),
        result_backend=secrets.get("CELERY_RESULT_BACKEND", secrets.get("RESULT_BACKEND", "redis://localhost:6379/0")),
        task_always_eager=secrets.get("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true",
        task_eager_propagates=True,
        worker_concurrency=int(secrets.get("WORKER_CONCURRENCY", "4")),
        worker_prefetch_multiplier=int(secrets.get("WORKER_PREFETCH_MULTIPLIER", "1")),
        task_routes=None,
        task_soft_time_limit=int(secrets.get("TASK_SOFT_TIME_LIMIT", "3600")),
        task_time_limit=int(secrets.get("TASK_TIME_LIMIT", "7200")),
        result_expires=int(secrets.get("RESULT_EXPIRES", "86400")),
        beat_schedule_filename=secrets.get("BEAT_SCHEDULE_FILE", "/tmp/celerybeat-schedule"),
    )
