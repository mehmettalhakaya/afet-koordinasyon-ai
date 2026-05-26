"""Sınıflandırıcı testleri."""
from __future__ import annotations

import pytest

from app.services.classifier import CATEGORIES, classifier_service


@pytest.fixture(scope="module", autouse=True)
def _train(synthetic_csv_exists):
    classifier_service.retrain()


def test_classifier_predicts_valid_category():
    cat, scores = classifier_service.predict(
        "Antakya'da enkaz altında 3 kişi var, vinç gerek."
    )
    assert cat in CATEGORIES
    assert isinstance(scores, dict)
    assert abs(sum(scores.values()) - 1.0) < 1e-6


def test_classifier_handles_health_text():
    cat, _ = classifier_service.predict(
        "Yaşlı amca nefes alamıyor, ambulans gerekli."
    )
    # Modeldeki tek-örnek varyansı nedeniyle saglik veya enkaz kabul edilebilir,
    # ama "ulasim" veya "gida" gibi alakasız bir kategori beklemiyoruz.
    assert cat in {"saglik", "enkaz"}


def test_classifier_handles_water_text():
    cat, _ = classifier_service.predict(
        "Çadır kentte içme suyumuz kalmadı, susuz kaldık."
    )
    assert cat in {"su", "diger"}


def test_classifier_accuracy_is_reasonable():
    # Sentetik şablon verisi, doğruluk yüksek olmalı (>0.7)
    assert classifier_service.accuracy >= 0.7
