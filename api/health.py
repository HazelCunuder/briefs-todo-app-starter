/**
 * Health Check Module for To-Do API
 * 
 * Provides health check endpoints for monitoring the application state
 * Follows best practices for health checks in containerized environments
 */

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.database import get_db

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus:
    """Represents the health status of a component."""

    def __init__(self, status: str = "healthy", message: str = "", details: Dict[str, Any] = None):
        self.status = status
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        result = {"status": self.status}
        if self.message:
            result["message"] = self.message
        if self.details:
            result["details"] = self.details
        return result


class OverallHealthStatus:
    """Represents the overall health status of the application."""

    def __init__(
        self,
        version: str = "0.1.0",
        environment: str = "development",
    ):
        self.version = version
        self.environment = environment
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.checks: Dict[str, HealthStatus] = {}

    def add_check(self, name: str, status: HealthStatus) -> None:
        self.checks[name] = status

    def get_status(self) -> str:
        """Determine overall status based on all checks."""
        if all(check.status == "healthy" for check in self.checks.values()):
            return "healthy"
        return "unhealthy"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.get_status(),
            "version": self.version,
            "environment": self.environment,
            "timestamp": self.timestamp,
            "checks": {name: check.to_dict() for name, check in self.checks.items()},
        }


def get_health_status(
    db: Session = Depends(get_db),
    version: str = "0.1.0",
    environment: str = "development",
) -> OverallHealthStatus:
    """
    Get the overall health status of the application.
    
    Args:
        db: Database session
        version: Application version
        environment: Environment name
        
    Returns:
        OverallHealthStatus: The health status object
    """
    health = OverallHealthStatus(version=version, environment=environment)

    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health.add_check("database", HealthStatus(status="healthy", message="Database connection OK"))
    except Exception as e:
        health.add_check(
            "database",
            HealthStatus(
                status="unhealthy",
                message="Database connection failed",
                details={"error": str(e)},
            ),
        )

    # Check cache connectivity (if Redis is configured)
    try:
        # Import redis here to avoid dependency issues if not installed
        import redis

        # Try to connect to Redis
        r = redis.Redis(host="redis", port=6379, db=0, socket_timeout=1)
        r.ping()
        health.add_check("cache", HealthStatus(status="healthy", message="Cache connection OK"))
    except ImportError:
        # Redis not installed, skip cache check
        health.add_check("cache", HealthStatus(status="healthy", message="Cache not configured"))
    except Exception as e:
        health.add_check(
            "cache",
            HealthStatus(
                status="unhealthy",
                message="Cache connection failed",
                details={"error": str(e)},
            ),
        )

    return health


@router.get("/", summary="Basic Health Check", description="Returns basic health status")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Basic health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get(
    "/db",
    summary="Database Health Check",
    description="Checks database connectivity",
)
async def database_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Database health check endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Database health status
        
    Raises:
        HTTPException: If database connection fails
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "connection failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )


@router.get(
    "/full",
    summary="Full Health Check",
    description="Performs comprehensive health checks on all components",
)
async def full_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Full health check endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Comprehensive health status
    """
    import os

    version = os.getenv("VERSION", "0.1.0")
    environment = os.getenv("ENVIRONMENT", "development")

    health = get_health_status(db, version=version, environment=environment)

    return health.to_dict()


@router.get(
    "/readiness",
    summary="Readiness Probe",
    description="Kubernetes readiness probe endpoint",
)
async def readiness_probe(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Kubernetes readiness probe.
    
    Args:
        db: Database session
        
    Returns:
        Readiness status
        
    Raises:
        HTTPException: If not ready
    """
    try:
        # Check database
        db.execute(text("SELECT 1"))

        # Check migrations (if needed)
        # This can be expensive, so we skip it for readiness

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )


@router.get(
    "/liveness",
    summary="Liveness Probe",
    description="Kubernetes liveness probe endpoint",
)
async def liveness_probe() -> Dict[str, Any]:
    """
    Kubernetes liveness probe.
    
    Returns:
        Liveness status
    """
    # Liveness probe should be lightweight and not depend on external services
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get(
    "/metrics",
    summary="Prometheus Metrics",
    description="Exposes Prometheus metrics for monitoring",
)
async def metrics_endpoint() -> str:
    """
    Prometheus metrics endpoint.
    
    Returns:
        Prometheus metrics in text format
    """
    try:
        from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

        metrics = generate_latest(REGISTRY)
        return CONTENT_TYPE_LATEST, metrics
    except ImportError:
        # prometheus_client not installed
        return "# prometheus_client not installed\n"
    except Exception as e:
        return f"# Error generating metrics: {e}\n"


# Include router in main app
# This will be imported in main.py
# from api.health import router as health_router
# app.include_router(health_router)
