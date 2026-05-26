"""FastAPI uç nokta entegrasyon testleri."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(synthetic_csv_exists):
    # Modülü burada import et ki conftest fikstürü DB path'i set ettikten sonra olsun
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "AfetKoordinasyonAI"
    assert "disclaimer" in data


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_list_call(client):
    payload = {
        "text": "Hatay Antakya'da enkaz altında 3 kişi var, acil vinç ve sağlık ekibi gerekiyor.",
        "city": "Hatay",
        "district": "Antakya",
        "people_count": 3,
    }
    r = client.post("/api/calls", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["id"] > 0
    assert body["category"] in {"enkaz", "saglik"}
    assert body["urgency_score"] >= 50
    assert body["lat"] is not None and body["lon"] is not None

    r2 = client.get("/api/calls")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


def test_analyze_does_not_persist(client):
    r = client.post(
        "/api/analyze",
        json={
            "text": "Bebek ateşi çok yüksek, doktor lazım.",
            "city": "Gaziantep",
            "people_count": 1,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "predicted_category" in body
    assert "urgency_score" in body
    assert "urgency_breakdown" in body


def test_duplicate_detection(client):
    txt = "Adıyaman Besni'de su tankeri yetişmedi, 10 hane susuz kaldı."
    r1 = client.post(
        "/api/calls",
        json={"text": txt, "city": "Adıyaman", "district": "Besni", "people_count": 10},
    )
    r2 = client.post(
        "/api/calls",
        json={"text": txt, "city": "Adıyaman", "district": "Besni", "people_count": 10},
    )
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r2.json()["duplicate_suspected"] is True


def test_dashboard(client):
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    body = r.json()
    assert body["total_calls"] >= 1
    assert "category_distribution" in body
    assert "city_distribution" in body
