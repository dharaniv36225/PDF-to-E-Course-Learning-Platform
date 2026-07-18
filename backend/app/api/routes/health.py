"""Health and readiness routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ai.llm import get_llm
from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@router.get("/health/ready")
def readiness(db: Session = Depends(get_db)) -> dict:
    checks = {"database": False, "llm": False}
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:  # noqa: BLE001
        checks["database"] = False
    checks["llm"] = get_llm().available
    status = "ok" if all(checks.values()) else "degraded"
    return {"status": status, "checks": checks}
