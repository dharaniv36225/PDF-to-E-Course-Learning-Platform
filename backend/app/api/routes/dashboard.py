"""Dashboard and search routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardStats, SearchResponse
from app.services.dashboard_service import DashboardService
from app.services.search_service import SearchService

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> DashboardStats:
    return DashboardStats.model_validate(DashboardService(db).get_stats(current_user.id))


@router.get("/search", response_model=SearchResponse, tags=["search"])
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    course_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SearchResponse:
    return SearchResponse.model_validate(SearchService(db).search(current_user.id, q, course_id))
