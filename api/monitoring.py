/**
 * Monitoring Module for To-Do API
 * 
 * Provides Prometheus metrics and monitoring utilities
 * Follows best practices for application monitoring
 */

from datetime import datetime
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)


# ============================================================================
# Metrics Definitions
# ============================================================================

# HTTP Request Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status_code", "environment"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status_code"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0],
)

HTTP_REQUEST_SIZE_BYTES = Summary(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "path"],
)

HTTP_RESPONSE_SIZE_BYTES = Summary(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "path", "status_code"],
)

# Database Metrics
DB_QUERY_COUNT = Counter(
    "db_query_count_total",
    "Total number of database queries",
    ["operation", "table", "status"],
)

DB_QUERY_DURATION_SECONDS = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

DB_CONNECTION_POOL_SIZE = Gauge(
    "db_connection_pool_size",
    "Current database connection pool size",
)

DB_CONNECTION_POOL_CHECKOUTS = Counter(
    "db_connection_pool_checkouts_total",
    "Total database connection pool checkouts",
)

DB_CONNECTION_POOL_CHECKINS = Counter(
    "db_connection_pool_checkins_total",
    "Total database connection pool checkins",
)

# Business Metrics
TODO_CREATED_TOTAL = Counter(
    "todo_created_total",
    "Total number of todos created",
    ["user_id"],
)

TODO_UPDATED_TOTAL = Counter(
    "todo_updated_total",
    "Total number of todos updated",
    ["user_id", "status"],
)

TODO_DELETED_TOTAL = Counter(
    "todo_deleted_total",
    "Total number of todos deleted",
    ["user_id"],
)

TODO_COMPLETED_TOTAL = Counter(
    "todo_completed_total",
    "Total number of todos completed",
    ["user_id"],
)

# Active Todos Gauge
TODO_ACTIVE_COUNT = Gauge(
    "todo_active_count",
    "Current number of active (incomplete) todos",
    ["user_id"],
)

# Error Metrics
ERROR_COUNT = Counter(
    "error_count_total",
    "Total number of errors",
    ["error_type", "endpoint", "method"],
)

# Cache Metrics
CACHE_HITS_TOTAL = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    ["cache_key"],
)

CACHE_MISSES_TOTAL = Counter(
    "cache_misses_total",
    "Total number of cache misses",
    ["cache_key"],
)

CACHE_LATENCY_SECONDS = Histogram(
    "cache_latency_seconds",
    "Cache operation latency in seconds",
    ["operation", "cache_key"],
    buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1],
)

# System Metrics
APP_START_TIME = Gauge(
    "app_start_time_seconds",
    "Application start time in Unix timestamp",
)

APP_UPTIME_SECONDS = Gauge(
    "app_uptime_seconds",
    "Application uptime in seconds",
)

APP_INFO = Gauge(
    "app_info",
    "Application information",
    ["version", "environment", "python_version"],
)


# ============================================================================
# Middleware
# ============================================================================

class MonitoringMiddleware:
    """FastAPI middleware for monitoring HTTP requests."""

    def __init__(
        self,
        app: FastAPI,
        environment: str = "development",
        exclude_paths: Optional[list] = None,
    ):
        self.app = app
        self.environment = environment
        self.exclude_paths = exclude_paths or ["/health", "/health/", "/metrics", "/docs", "/openapi.json"]

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process a request and track metrics."""
        method = request.method
        path = request.url.path

        # Skip monitoring for excluded paths
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)

        # Track request start time
        start_time = datetime.utcnow()

        try:
            response = await call_next(request)
        except Exception as e:
            # Track error
            ERROR_COUNT.labels(
                error_type=type(e).__name__,
                endpoint=path,
                method=method,
            ).inc()
            raise
        finally:
            # Calculate duration
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Get status code
            status_code = getattr(response, "status_code", 500)

            # Track metrics
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                path=path,
                status_code=str(status_code),
                environment=self.environment,
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                path=path,
                status_code=str(status_code),
            ).observe(duration)

            # Track request/response sizes
            request_size = int(request.headers.get("content-length", 0))
            HTTP_REQUEST_SIZE_BYTES.labels(method=method, path=path).observe(request_size)

            response_size = 0
            if hasattr(response, "headers") and "content-length" in response.headers:
                response_size = int(response.headers["content-length"])
            HTTP_RESPONSE_SIZE_BYTES.labels(
                method=method,
                path=path,
                status_code=str(status_code),
            ).observe(response_size)

        return response


# ============================================================================
# Database Monitoring
# ============================================================================

class DatabaseMonitor:
    """Monitor database operations."""

    @staticmethod
    def track_query(
        operation: str,
        table: str,
        duration: float,
        success: bool = True,
    ) -> None:
        """Track a database query."""
        status = "success" if success else "failure"
        DB_QUERY_COUNT.labels(operation=operation, table=table, status=status).inc()
        DB_QUERY_DURATION_SECONDS.labels(operation=operation, table=table).observe(duration)

    @staticmethod
    def set_pool_size(size: int) -> None:
        """Set the current connection pool size."""
        DB_CONNECTION_POOL_SIZE.set(size)

    @staticmethod
    def track_pool_checkout() -> None:
        """Track a connection pool checkout."""
        DB_CONNECTION_POOL_CHECKOUTS.inc()

    @staticmethod
    def track_pool_checkin() -> None:
        """Track a connection pool checkin."""
        DB_CONNECTION_POOL_CHECKINS.inc()


# ============================================================================
# Business Metrics Trackers
# ============================================================================

class TodoMetrics:
    """Track todo-related metrics."""

    @staticmethod
    def track_created(user_id: Optional[str] = None) -> None:
        """Track todo creation."""
        TODO_CREATED_TOTAL.labels(user_id=user_id or "anonymous").inc()

    @staticmethod
    def track_updated(user_id: Optional[str] = None, status: Optional[str] = None) -> None:
        """Track todo update."""
        TODO_UPDATED_TOTAL.labels(user_id=user_id or "anonymous", status=status or "unknown").inc()

    @staticmethod
    def track_deleted(user_id: Optional[str] = None) -> None:
        """Track todo deletion."""
        TODO_DELETED_TOTAL.labels(user_id=user_id or "anonymous").inc()

    @staticmethod
    def track_completed(user_id: Optional[str] = None) -> None:
        """Track todo completion."""
        TODO_COMPLETED_TOTAL.labels(user_id=user_id or "anonymous").inc()

    @staticmethod
    def set_active_count(user_id: Optional[str] = None, count: int = 0) -> None:
        """Set the active todo count."""
        TODO_ACTIVE_COUNT.labels(user_id=user_id or "anonymous").set(count)


# ============================================================================
# Cache Monitoring
# ============================================================================

class CacheMonitor:
    """Monitor cache operations."""

    @staticmethod
    def track_hit(cache_key: str) -> None:
        """Track a cache hit."""
        CACHE_HITS_TOTAL.labels(cache_key=cache_key).inc()

    @staticmethod
    def track_miss(cache_key: str) -> None:
        """Track a cache miss."""
        CACHE_MISSES_TOTAL.labels(cache_key=cache_key).inc()

    @staticmethod
    def track_latency(operation: str, cache_key: str, duration: float) -> None:
        """Track cache operation latency."""
        CACHE_LATENCY_SECONDS.labels(operation=operation, cache_key=cache_key).observe(duration)


# ============================================================================
# System Monitoring
# ============================================================================

class SystemMonitor:
    """Monitor system-level metrics."""

    @staticmethod
    def set_start_time() -> None:
        """Set the application start time."""
        import time
        APP_START_TIME.set(time.time())

    @staticmethod
    def update_uptime() -> None:
        """Update the application uptime."""
        import time
        start_time = APP_START_TIME._value.get()
        if start_time:
            APP_UPTIME_SECONDS.set(time.time() - start_time)

    @staticmethod
    def set_app_info(version: str, environment: str, python_version: str) -> None:
        """Set application information."""
        APP_INFO.labels(version=version, environment=environment, python_version=python_version).set(1)


# ============================================================================
# Metrics Endpoint
# ============================================================================

async def metrics_endpoint() -> tuple:
    """
    Prometheus metrics endpoint.
    
    Returns:
        Tuple of (content_type, metrics_text)
    """
    metrics = generate_latest(REGISTRY)
    return CONTENT_TYPE_LATEST, metrics


# ============================================================================
# Utility Functions
# ============================================================================

def get_metrics_summary() -> Dict[str, Any]:
    """
    Get a summary of all metrics.
    
    Returns:
        Dictionary containing metric summaries
    """
    return {
        "http": {
            "requests_total": HTTP_REQUESTS_TOTAL._value.get(),
            "request_duration": HTTP_REQUEST_DURATION_SECONDS._sum.get(),
        },
        "database": {
            "query_count": DB_QUERY_COUNT._value.get(),
            "query_duration": DB_QUERY_DURATION_SECONDS._sum.get(),
        },
        "todos": {
            "created": TODO_CREATED_TOTAL._value.get(),
            "updated": TODO_UPDATED_TOTAL._value.get(),
            "deleted": TODO_DELETED_TOTAL._value.get(),
            "completed": TODO_COMPLETED_TOTAL._value.get(),
        },
        "errors": ERROR_COUNT._value.get(),
    }


def reset_metrics() -> None:
    """Reset all metrics (useful for testing)."""
    HTTP_REQUESTS_TOTAL.reset()
    HTTP_REQUEST_DURATION_SECONDS.reset()
    HTTP_REQUEST_SIZE_BYTES.reset()
    HTTP_RESPONSE_SIZE_BYTES.reset()
    DB_QUERY_COUNT.reset()
    DB_QUERY_DURATION_SECONDS.reset()
    DB_CONNECTION_POOL_SIZE.reset()
    DB_CONNECTION_POOL_CHECKOUTS.reset()
    DB_CONNECTION_POOL_CHECKINS.reset()
    TODO_CREATED_TOTAL.reset()
    TODO_UPDATED_TOTAL.reset()
    TODO_DELETED_TOTAL.reset()
    TODO_COMPLETED_TOTAL.reset()
    TODO_ACTIVE_COUNT.reset()
    ERROR_COUNT.reset()
    CACHE_HITS_TOTAL.reset()
    CACHE_MISSES_TOTAL.reset()
    CACHE_LATENCY_SECONDS.reset()


# ============================================================================
# Initialization
# ============================================================================

def init_monitoring(app: FastAPI, environment: str = "development") -> None:
    """
    Initialize monitoring for the FastAPI application.
    
    Args:
        app: FastAPI application
        environment: Environment name
    """
    import sys
    import time

    # Set application start time
    SystemMonitor.set_start_time()

    # Set application info
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    SystemMonitor.set_app_info(
        version="0.1.0",
        environment=environment,
        python_version=python_version,
    )

    # Add middleware
    app.add_middleware(MonitoringMiddleware, environment=environment)

    # Add metrics endpoint
    @app.get("/metrics", tags=["monitoring"])
    async def metrics():
        return await metrics_endpoint()

    # Add health check endpoint (if not already added)
    if not any(route.path == "/health" for route in app.routes):
        @app.get("/health", tags=["health"])
        async def health():
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "uptime": time.time() - SystemMonitor.APP_START_TIME._value.get(),
            }

    # Start background task to update uptime
    @app.on_event("startup")
    async def startup_event():
        import asyncio
        asyncio.create_task(update_uptime_background())


async def update_uptime_background() -> None:
    """Background task to update uptime metric."""
    import asyncio
    while True:
        SystemMonitor.update_uptime()
        await asyncio.sleep(15)
