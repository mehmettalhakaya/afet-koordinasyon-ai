"""Test fikstürleri.

Her test için ayrı geçici SQLite DB kullanır; sınıflandırıcıyı sentetik
veriyle eğitir (model dosyası yoksa).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# backend kökünü PYTHONPATH'e ekle
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(scope="session", autouse=True)
def _set_test_db():
    """Tüm test session'ı için ayrı SQLite dosyası."""
    import tempfile
    import shutil

    db_dir = Path(tempfile.mkdtemp(prefix="afet_test_"))
    os.environ["AFET_DB_PATH"] = str(db_dir / "test.db")
    yield
    shutil.rmtree(db_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def synthetic_csv_exists():
    """Eğer CSV yoksa testleri çalıştırmadan önce üret."""
    csv_path = BACKEND_DIR / "data" / "synthetic_calls.csv"
    if not csv_path.exists():
        from data.generate_synthetic_data import gen