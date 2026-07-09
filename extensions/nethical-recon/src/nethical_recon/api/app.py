"""FastAPI application factory."""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from .config import APIConfig
from .models import HealthResponse
from .routers import (
    active_recon_router,
    attack_surface_router,
    auth_router,
    enrichment_router,
    findings_router,
    jobs_router,
    reports_router,
    runs_router,
    security_testing_router,
    targets_router,
    visualization_router,
)

# Thread pool for blocking operations in health checks
_health_check_executor = ThreadPoolExecutor(max_workers=4)


def create_app(config: APIConfig | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if config is None:
        config = APIConfig.from_env()

    app = FastAPI(
        title=config.title,
        description=config.description,
        version=config.version,
        docs_url=f"{config.api_prefix}/docs",
        redoc_url=f"{config.api_prefix}/redoc",
        openapi_url=f"{config.api_prefix}/openapi.json",
    )

    # CORS middleware
    if config.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=config.cors_allow_credentials,
            allow_methods=config.cors_allow_methods or ["*"],
            allow_headers=config.cors_allow_headers or ["*"],
        )

    # Metrics middleware
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        """Middleware to track API request metrics."""
        from nethical_recon.observability import get_logger, increment_counter, observe_value

        start_time = time.time()

        # Get logger with request context
        logger = get_logger(__name__, path=request.url.path, method=request.method)
        logger.debug("api request received")

        try:
            response = await call_next(request)

            # Track metrics
            duration = time.time() - start_time
            observe_value("api_request_duration", duration, {"method": request.method, "endpoint": request.url.path})
            increment_counter(
                "api_requests_total",
                {"method": request.method, "endpoint": request.url.path, "status_code": str(response.status_code)},
            )

            logger.info("api request completed", status_code=response.status_code, duration=duration)
            return response
        except Exception as e:
            logger.error("api request failed", error=str(e), exc_info=True)
            increment_counter(
                "api_requests_total", {"method": request.method, "endpoint": request.url.path, "status_code": "500"}
            )
            raise

    # Metrics endpoint
    @app.get("/metrics", tags=["observability"])
    async def metrics():
        """Prometheus metrics endpoint."""
        from nethical_recon.observability.metrics import get_metrics

        metrics_data = get_metrics()
        return Response(content=metrics_data, media_type="text/plain")

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health_check():
        """Health check endpoint with timeouts to prevent blocking."""
        from nethical_recon.core.storage import get_database

        # Check database connection with timeout
        db_status = "healthy"
        try:

            async def check_db():
                """Check database connection in async context."""
                db = get_database()
                with db.session():
                    pass
                return "healthy"

            db_status = await asyncio.wait_for(check_db(), timeout=3.0)
        except asyncio.TimeoutError:
            db_status = "timeout"
        except Exception as e:
            db_status = "unhealthy"

        # Check worker connection with timeout
        worker_status = "unknown"
        try:

            async def check_worker():
                """Check worker/Celery connection in async context."""
                from celery import Celery

                from nethical_recon.worker.config import WorkerConfig

                worker_config = WorkerConfig.from_env()
                celery_app = Celery(broker=worker_config.broker_url, backend=worker_config.result_backend)

                # Run blocking Celery inspect in thread pool
                loop = asyncio.get_event_loop()
                stats = await loop.run_in_executor(
                    _health_check_executor, lambda: celery_app.control.inspect(timeout=2.0).stats()
                )

                return "healthy" if stats else "unhealthy"

            worker_status = await asyncio.wait_for(check_worker(), timeout=3.0)
        except asyncio.TimeoutError:
            worker_status = "timeout"
        except Exception as e:
            worker_status = "unhealthy"

        # Determine overall status
        overall_status = "healthy" if db_status == "healthy" and worker_status == "healthy" else "degraded"

        return HealthResponse(
            status=overall_status,
            version=config.version,
            timestamp=datetime.now(timezone.utc),
            database=db_status,
            worker=worker_status,
        )

    # Version endpoint
    @app.get("/version", tags=["health"])
    async def version():
        """Get API version."""
        return {"version": config.version, "api_prefix": config.api_prefix}

    # Register routers with API prefix
    app.include_router(auth_router, prefix=config.api_prefix)
    app.include_router(targets_router, prefix=config.api_prefix)
    app.include_router(jobs_router, prefix=config.api_prefix)
    app.include_router(runs_router, prefix=config.api_prefix)
    app.include_router(findings_router, prefix=config.api_prefix)
    app.include_router(reports_router, prefix=config.api_prefix)
    app.include_router(attack_surface_router, prefix=config.api_prefix)
    app.include_router(enrichment_router, prefix=config.api_prefix)
    app.include_router(active_recon_router, prefix=config.api_prefix)
    app.include_router(visualization_router, prefix=config.api_prefix)
    app.include_router(security_testing_router, prefix=config.api_prefix)

    # Exception handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    return app
