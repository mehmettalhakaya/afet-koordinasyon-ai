"""Dashboard endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services.dashboard import collect_stats

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    return collect_stats(db)
