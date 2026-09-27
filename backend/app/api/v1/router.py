"""API v1 Router"""
from fastapi import APIRouter
from app.api.v1.endpoints import incidents, evidence, metrics, approvals, audit

api_router = APIRouter()

api_router.include_router(
    metrics.router,
    prefix="/incidents/metrics",
    tags=["metrics"]
)

api_router.include_router(
    incidents.router,
    prefix="/incidents",
    tags=["incidents"]
)

api_router.include_router(
    evidence.router,
    prefix="/evidence",
    tags=["evidence"]
)

api_router.include_router(
    approvals.router,
    prefix="/approvals",
    tags=["approvals"]
)

api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["audit"]
)
