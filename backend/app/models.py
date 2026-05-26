"""ORM modelleri.

Tek tablolu MVP: HelpCall. İleride volunteers, teams, assignments eklenebilir.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def utcnow_naive() -> datetime:
    """Python 3.12+ uyumlu naive UTC. SQLAlchemy DateTime (tz=False) için."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class HelpCall(Base):
    """Yardım çağrısı kaydı."""

    __tablename__ = "help_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    district: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    address_note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    people_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    urgency_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)

    cluster_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    duplicate_suspected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    similar_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow_naive, nullable=False, index=True
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "city": self.city,
            "district": self.district,
            "address_note": self.address_note,
            "people_count": self.people_count,
            "phone": self.phone,
            "lat": self.lat,
            "lon": self.lon,
            "category": self.category,
            "urgency_score": self.urgency_score,
            "cluster_id": self.cluster_id,
            "duplicate_suspected": self.duplicate_suspected,
            "similar_count": self.similar_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
