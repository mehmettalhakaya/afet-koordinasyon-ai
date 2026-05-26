"""SQLAlchemy veritabanı kurulumu.

SQLite + SQLAlchemy 2.0 stilinde. Tek dosya, lokal, sıfır config.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Veritabanı dosyasını backend/ kökünde tut
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.getenv("AFET_DB_PATH", str(BASE_DIR / "afet.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Tüm ORM modellerinin temel sınıfı."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI bağımlılığı: istek başına bir DB oturumu."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Tabloları oluştur (idempotent)."""
    # Modelleri import ederek metadata'ya kayıt olmalarını sağla
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
