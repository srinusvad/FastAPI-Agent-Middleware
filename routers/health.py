"""
Health check and status endpoints.
Includes liveness, readiness, and detailed health check probes.
"""

from fastapi import APIRouter, Depends, status
from datetime import datetime
from typing import Dict
from schemas.agent import HealthStatus, ReadinessStatus
from dependencies import MockDatabase, get_db

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    summary="Detailed Health Check",
    description="Returns comprehensive health information including system status, version, and timestamp",
)
async def health_check() -> HealthStatus:
    """
    Detailed health check endpoint.
    Returns overall system status with version information.
    """
    return HealthStatus(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
    )


@router.get(
    "/status/ready",
    response_model=ReadinessStatus,
    status_code=status.HTTP_200_OK,
    summary="Kubernetes Readiness Probe",
    description="Returns readiness status for Kubernetes or load balancers to determine if service is ready for traffic",
)
async def readiness_check(db: MockDatabase = Depends(get_db)) -> ReadinessStatus:
    """
    Readiness probe endpoint (Kubernetes-compatible).
    Checks if service is ready to accept traffic by verifying dependencies.
    """
    # Check database health
    db_healthy = await db.health_check()
    
    return ReadinessStatus(
        ready=db_healthy,
        db_healthy=db_healthy,
        timestamp=datetime.now().isoformat(),
    )


@router.get(
    "/status/live",
    status_code=status.HTTP_200_OK,
    summary="Kubernetes Liveness Probe",
    description="Simple liveness probe for Kubernetes health monitoring",
)
async def liveness_check() -> Dict[str, bool]:
    """
    Liveness probe endpoint (Kubernetes-compatible).
    Simple check that the service is alive and responding.
    """
    return {"alive": True}
