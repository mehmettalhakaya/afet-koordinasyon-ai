"""Dashboard istatistik servisi."""
from __future__ import annotations

from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models


def collect_stats(db: Session, top_n: int = 10) -> dict:
    total = db.query(func.count(models.HelpCall.id)).scalar() or 0
    avg_urg = db.query(func.avg(models.HelpCall.urgency_score)).scalar() or 0.0
    dup_count = (
        db.query(func.count(models.HelpCall.id))
        .filter(models.HelpCall.duplicate_suspected.is_(True))
        .scalar()
        or 0
    )

    top_urgent = (
        db.query(models.HelpCall)
        .order_by(models.HelpCall.urgency_score.desc(), models.HelpCall.created_at.desc())
        .limit(top_n)
        .all()
    )
    recent = (
        db.query(models.HelpCall)
        .order_by(models.HelpCall.created_at.desc())
        .limit(top_n)
        .all()
    )

    cat_rows = (
        db.query(models.HelpCall.category, func.count(models.HelpCall.id))
        .group_by(models.HelpCall.category)
        .order_by(func.count(models.HelpCall.id).desc())
        .all()
    )
    city_rows = (
        db.query(models.HelpCall.city, func.count(models.HelpCall.id))
        .group_by(models.HelpCall.city)
        .order_by(func.count(models.HelpCall.id).desc())
        .all()
    )

    return {
        "total_calls": int(total),
        "avg_urgency": round(float(avg_urg), 2),
        "duplicate_suspected_count": int(dup_count),
        "top_urgent_calls": top_urgent,
        "recent_calls": recent,
        "category_distribution": [
            {"category": c, "count": int(n)} for c, n in cat_rows
        ],
        "city_distribution": [
            {"city": c, "count": int(n)} for c, n in city_rows
        ],
    }
