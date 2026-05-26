"""Pydantic şemaları - API giriş/çıkış sözleşmesi."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class HelpCallCreate(BaseModel):
    """Yeni çağrı oluşturma için giriş şeması."""

    text: str = Field(..., min_length=3, max_length=2000, description="Çağrı metni")
    city: str = Field(..., min_length=2, max_length=64)
    district: Optional[str] = Field(default=None, max_length=128)
    address_note: Optional[str] = Field(default=None, max_length=255)
    people_count: int = Field(default=1, ge=1, le=10000)
    phone: Optional[str] = Field(default=None, max_length=32)
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)
    category: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Manuel kategori override. Verilmezse AI tahmin eder.",
    )


class HelpCallOut(BaseModel):
    """Çağrı çıkış şeması."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    city: str
    district: Optional[str] = None
    address_note: Optional[str] = None
    people_count: int
    phone: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    category: str
    urgency_score: int
    cluster_id: Optional[int] = None
    duplicate_suspected: bool
    similar_count: int
    created_at: datetime


class AnalyzeRequest(BaseModel):
    """Sadece analiz (kaydetmeden) için giriş."""

    text: str = Field(..., min_length=3, max_length=2000)
    city: Optional[str] = Field(default=None, max_length=64)
    district: Optional[str] = Field(default=None, max_length=128)
    people_count: int = Field(default=1, ge=1, le=10000)


class AnalyzeResponse(BaseModel):
    predicted_category: str
    category_scores: dict
    urgency_score: int
    urgency_breakdown: dict
    extracted_keywords: List[str]
    duplicate_candidates: List[HelpCallOut] = []


class DashboardCategoryCount(BaseModel):
    category: str
    count: int


class DashboardCityCount(BaseModel):
    city: str
    count: int


class DashboardStats(BaseModel):
    total_calls: int
    avg_urgency: float
    duplicate_suspected_count: int
    top_urgent_calls: List[HelpCallOut]
    recent_calls: List[HelpCallOut]
    category_distribution: List[DashboardCategoryCount]
    city_distribution: List[DashboardCityCount]


class RetrainResponse(BaseModel):
    status: str
    samples_used: int
    accuracy: float
