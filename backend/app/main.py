"""AfetKoordinasyonAI - FastAPI ana uygulama.

UYARI: Bu sistem GERÇEK acil durumlarda kullanılacak resmi bir koordinasyon
sistemi DEĞİLDİR. Eğitim, demo ve araştırma amaçlıdır.
Acil durumda lütfen 112'yi arayın ve AFAD/Kızılay gibi resmi kurumları takip edin.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import SessionLocal, init_db
from .routers import analyze as analyze_router
from .routers import calls as calls_router
from .routers import dashboard as dashboard_router
from .services.classifier import classifier_service
from .services.ws_manager import manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("afet")

DEMO_DISCLAIMER = (
    "DEMO sistemi - gerçek afetlerde 112'yi arayın, AFAD ve Kızılay'ı takip edin."
)


def _seed_from_csv_if_empty() -> None:
    """DB boşsa sentetik CSV'yi yükle (varsa). Geliştirme rahatı için."""
    from . import models

    csv_path = Path(__file__).resolve().parent.parent / "data" / "synthetic_calls.csv"
    if not csv_path.exists():
        logger.info("Sentetik CSV bulunamadı, seed atlandı: %s", csv_path)
        return

    db: Session = SessionLocal()
    try:
        if db.query(models.HelpCall).count() > 0:
            return
        import csv
        from datetime import datetime

        from .models import utcnow_naive
        from .services.geocoding import approximate_coords
        from .services.urgency import compute_urgency

        added = 0
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = (row.get("text") or "").strip()
                if not text:
                    continue
                city = (row.get("city") or "").strip()
                district = (row.get("district") or "").strip() or None
                category = (row.get("label") or "diger").strip()
                try:
                    people = int(row.get("people_count") or 1)
                except ValueError:
                    people = 1
                lat = row.get("lat")
                lon = row.get("lon")
                try:
                    lat_f = float(lat) if lat else None
                    lon_f = float(lon) if lon else None
                except ValueError:
                    lat_f, lon_f = None, None
                if lat_f is None or lon_f is None:
                    coords = approximate_coords(city, district, seed_text=text)
                    if coords:
                        lat_f, lon_f = coords
                urgency, _ = compute_urgency(text=text, category=category, people_count=people)

                created_str = row.get("created_at")
                try:
                    created_at = (
                        datetime.fromisoformat(created_str) if created_str else utcnow_naive()
                    )
                except ValueError:
                    created_at = utcnow_naive()

                obj = models.HelpCall(
                    text=text,
                    city=city,
                    district=district,
                    people_count=people,
                    lat=lat_f,
                    lon=lon_f,
                    category=category,
                    urgency_score=urgency,
                    cluster_id=None,
                    duplicate_suspected=False,
                    similar_count=0,
                    created_at=created_at,
                )
                db.add(obj)
                added += 1
        db.commit()
        logger.info("Seed tamamlandi: %d kayit eklendi.", added)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        classifier_service.load_or_train()
    except FileNotFoundError as e:
        logger.warning("Siniflandirici egitilemedi: %s", e)
    _seed_from_csv_if_empty()
    yield


app = FastAPI(
    title="AfetKoordinasyonAI",
    description=(
        "Afet aninda gelen yardim cagrilarini analiz eden egitim/demo amacli sistem. "
        + DEMO_DISCLAIMER
    ),
    version="0.2.0",
    lifespan=lifespan,
)

# CORS: lokal dev + production Vercel domain'i icin
# Production'da CORS_ORIGINS env var'i virgulle ayrilmis liste olarak ayarla:
#   CORS_ORIGINS=https://afet.vercel.app,https://afetkoordinasyon.com
import os as _os
_extra_origins = [
    o.strip() for o in _os.getenv("CORS_ORIGINS", "").split(",") if o.strip()
]
_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _extra_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # tum Vercel preview URL'lerine izin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calls_router.router)
app.include_router(dashboard_router.router)
app.include_router(analyze_router.router)


@app.websocket("/ws/calls")
async def ws_calls(websocket: WebSocket):
    """Yeni cagri broadcast'lerini almak icin WebSocket.

    Mesaj formati:
        {"type": "new_call", "call": {...HelpCallOut...}}
        {"type": "ping"}                     # istemci ping
        {"type": "pong"}                     # sunucu pong yaniti
    """
    await manager.connect(websocket)
    try:
        # Hosgeldin mesaji
        await websocket.send_json({"type": "hello", "msg": "WebSocket bagli"})
        while True:
            # Istemci ping atarsa pong don. Veri tuketmek WS'in acik kalmasi icin
            msg = await websocket.receive_text()
            if msg:
                try:
                    import json
                    data = json.loads(msg)
                    if data.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                except Exception:
                    pass
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket)


@app.get("/")
def root():
    return {
        "name": "AfetKoordinasyonAI",
        "version": "0.2.0",
        "status": "ok",
        "disclaimer": DEMO_DISCLAIMER,
        "docs": "/docs",
        "ws": "/ws/calls",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "classifier_ready": classifier_service.is_ready(),
        "classifier_accuracy": classifier_service.accuracy,
        "samples_used": classifier_service.samples_used,
        "ws_clients": len(manager.active),
    }
