"""Worker queue module for asynchronous scan execution."""

from nethical_recon.worker.celery_app import celery_app

__all__ = ["celery_app"]
