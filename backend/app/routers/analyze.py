"""Veritabanına yazmadan analiz endpoint'i.

UI'daki "Analiz Demo" sayfası için: kullanıcı bir metin girer,
sistem ne yapacağını gösterir ama kaydetmez.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.classifier import classifier_service
from ..services.deduplication import find_similar
from ..services.urgency import compute_urgency

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=schemas.AnalyzeResponse)
def analyze(payload: schemas.AnalyzeRequest, db: Session = Depends(get_db)):
    category, scores = classifier_service.predict(payload.text)
    urgency, breakdown = compute_urgency(
        text=payload.text, category=category, people_count=payload.people_count
    )

    candidates: list = []
    if payload.city:
        existing = (
            db.query(models.HelpCall)
            .order_by(models.HelpCall.created_at.desc())
            .limit(500)
            .all()
        )
        similar, _, _ = find_similar(
            new_text=payload.text,
            new_city=payload.city,
            new_district=payload.district,
            existing=existing,
        )
        id_to_call = {c.id: c for c in existing}
        for s in similar[:5]:
            call = id_to_call.get(s.id)
            if call:
                candidates.append(call)

    return schemas.AnalyzeResponse(
        predicted_category=category,
        category_scores=scores,
        urgency_score=urgency,
        urgency_breakdown=breakdown,
        extracted_keywords=breakdown.get("matched_keywords", []),
        duplicate_candidates=candidates,
    )
