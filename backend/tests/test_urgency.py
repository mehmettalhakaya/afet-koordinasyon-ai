"""Aciliyet skorlama testleri."""
from __future__ import annotations

from app.services.urgency import (
    compute_urgency,
    extract_keywords,
    urgency_band,
)


def test_baseline_urgency_is_low():
    score, br = compute_urgency("Yardım lütfen.", category="diger", people_count=1)
    assert 0 <= score <= 100
    assert score < 50
    assert br["base"] == 20


def test_enkaz_with_keywords_is_high():
    text = "Antakya'da enkaz altında mahsur kalan 4 kişi var, kanama ve yaralı var."
    score, br = compute_urgency(text, category="enkaz", people_count=4)
    assert score >= 70
    assert "enkaz" in br["matched_keywords"]
    assert br["category_weight"] >= 20


def test_more_people_increases_score():
    base, _ = compute_urgency("Su lazım.", category="su", people_count=1)
    big, _ = compute_urgency("Su lazım.", category="su", people_count=50)
    assert big > base


def test_score_is_clamped_0_100():
    text = "enkaz mahsur kanama nefes alamıyor bebek çocuk yaralı ağır yaralı bilinci kapalı"
    score, _ = compute_urgency(text, category="enkaz", people_count=1000)
    assert 0 <= score <= 100


def test_extract_keywords_finds_known_terms():
    kws = extract_keywords("Acil enkaz altında mahsur bir bebek var.")
    assert "enkaz" in kws
    assert "mahsur" in kws
    assert "bebek" in kws
    assert "acil" in kws


def test_urgency_band():
    assert urgency_band(90) == "critical"
    assert urgency_band(60) == "high"
    assert urgency_band(30) == "medium"
    assert urgency_band(5) == "low"
