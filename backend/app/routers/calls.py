"""Yardım çağrısı endpointleri.

GET /api/calls           -> liste + filtre
POST /api/calls          -> yeni çağrı (sınıflandır + skor + dedup + WS yayını)
GET /api/calls/{id}      -> tek çağrı
POST /api/retrain        -> modeli yeniden eğit
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.classifier import classifier_service
from ..services.deduplication import find_similar, next_cluster_id
from ..services.geocoding import approximate_coords
from ..services.urgency import compute_urgency
from ..services.ws_manager import manager

router = APIRouter(prefix="/api", tags=["calls"])


@router.get("/calls", response_model=List[schemas.HelpCallOut])
def list_calls(
    city: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    min_urgency: Optional[int] = Query(default=None, ge=0, le=100),
    duplicate_suspected: Optional[bool] = Query(default=None),
    limit: int = Query(default=500, ge=1, le=2000),
    db: Session = Depends(get_db),
):
    q = db.query(models.HelpCall)
    if city:
        q = q.filter(models.HelpCall.city.ilike(city))
    if category:
        q = q.filter(models.HelpCall.category == category)
    if min_urgency is not None:
        q = q.filter(models.HelpCall.urgency_score >= min_urgency)
    if duplicate_suspected is not None:
        q = q.filter(models.HelpCall.duplicate_suspected.is_(duplicate_suspected))
    q = q.order_by(models.HelpCall.urgency_score.desc(), models.HelpCall.created_at.desc())
    return q.limit(limit).all()


@router.get("/calls/{call_id}", response_model=schemas.HelpCallOut)
def get_call(call_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.HelpCall).filter(models.HelpCall.id == call_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Çağrı bulunamadı")
    return obj


@router.post("/calls", response_model=schemas.HelpCallOut, status_code=201)
async def create_call(payload: schemas.HelpCallCreate, db: Session = Depends(get_db)):
    # 1) Sınıflandır
    category, _scores = classifier_service.predict(payload.text)

    # 2) Aciliyet skoru
    urgency, _breakdown = compute_urgency(
        text=payload.text, category=category, people_count=payload.people_count
    )

    # 3) Koordinat: kullanıcı vermemişse demo geocode
    lat, lon = payload.lat, payload.lon
    if lat is None or lon is None:
        coords = approximate_coords(payload.city, payload.district, seed_text=payload.text)
        if coords:
            lat, lon = coords

    # 4) Duplicate / cluster tespiti
    existing = (
        db.query(models.HelpCall)
        .order_by(models.HelpCall.created_at.desc())
        .limit(500)
        .all()
    )
    similar, dup_flag, best_cluster = find_similar(
        new_text=payload.text,
        new_city=payload.city,
        new_district=payload.district,
        existing=existing,
    )
    cluster_id = best_cluster if best_cluster is not None else next_cluster_id(existing)

    obj = models.HelpCall(
        text=payload.text,
        city=payload.city,
        district=payload.district,
        address_note=payload.address_note,
        people_count=payload.people_count,
        phone=payload.phone,
        lat=lat,
        lon=lon,
        category=category,
        urgency_score=urgency,
        cluster_id=cluster_id,
        duplicate_suspected=dup_flag,
        similar_count=len(similar),
    )
    db.add(obj)

    # Benzer çağrıların similar_count'unu güncelle
    if similar:
        ids = [s.id for s in similar]
        db.query(models.HelpCall).filter(models.HelpCall.id.in_(ids)).update(
            {models.HelpCall.similar_count: models.HelpCall.similar_count + 1},
            synchronize_session=False,
        )
    db.commit()
    db.refresh(obj)

    # 5) WebSocket yayını - bağlı tüm istemcilere yeni çağrıyı bildir
    await manager.broadcast({"type": "new_call", "call": obj.to_dict()})

    return obj


@router.post("/retrain", response_model=schemas.RetrainResponse)
def retrain():
    acc, n = classifier_service.retrain()
    return schemas.RetrainResponse(status="ok", samples_used=n, accuracy=acc)
