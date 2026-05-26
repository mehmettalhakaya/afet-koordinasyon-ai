"""Aciliyet skoru (0-100) - kural tabanlı MVP.

Yaklaşım:
  base 20 puan
  + anahtar kelime ağırlıkları (mahsur=25, kanama=22, ...)
  + kategori ağırlığı (enkaz/sağlık daha yüksek)
  + kişi sayısı bonusu (logaritmik tavanlı)
  -> 0-100 arası clamp.

İleride ML ile değiştirmek için: compute_urgency() imzasını koru,
gövdesini bir regresör çağrısıyla değiştirmek yeterli.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

# Anahtar kelime -> puan (lowercase, Türkçe karakterlere dikkat)
# Aciliyet ifade eden ifadeleri toplar. Çakışma olursa toplanır.
URGENCY_KEYWORDS: Dict[str, int] = {
    # Enkaz / mahsuriyet
    "enkaz": 25,
    "mahsur": 25,
    "altinda": 12,
    "altında": 12,
    "göcuk": 18,
    "göçük": 18,
    "yıkıldı": 20,
    "yikildi": 20,
    # Yaralılık / sağlık
    "kanama": 22,
    "kanıyor": 22,
    "yaralı": 18,
    "yarali": 18,
    "agir yarali": 28,
    "ağır yaralı": 28,
    "nefes alamiyor": 30,
    "nefes alamıyor": 30,
    "bilinci kapalı": 28,
    "bilinci kapali": 28,
    "kalp": 18,
    "kriz": 15,
    # Hassas grup
    "bebek": 22,
    "çocuk": 18,
    "cocuk": 18,
    "yaşlı": 16,
    "yasli": 16,
    "hamile": 20,
    "engelli": 18,
    # Aciliyet kelimeleri
    "acil": 12,
    "ölmek üzere": 30,
    "olmek uzere": 30,
    "hayati tehlike": 28,
    "hayatî tehlike": 28,
    "donuyor": 15,
    "donuyoruz": 15,
    "soğuk": 6,
    "soguk": 6,
    # Temel ihtiyaç
    "su yok": 10,
    "susuz": 10,
    "aç": 8,
    "ac kaldik": 10,
    "aç kaldık": 10,
    "ilaç": 12,
    "ilac": 12,
    "insülin": 22,
    "insulin": 22,
}

CATEGORY_WEIGHT: Dict[str, int] = {
    "enkaz": 25,
    "saglik": 22,
    "kayip_kisi": 18,
    "ilac": 14,
    "barinma": 10,
    "su": 8,
    "gida": 6,
    "elektrik_isinma": 8,
    "ulasim": 6,
    "diger": 2,
}

_WORD_RE = re.compile(r"[\wçğıöşüÇĞİÖŞÜ]+", re.UNICODE)


def _normalize(text: str) -> str:
    return text.lower().strip()


def extract_keywords(text: str) -> List[str]:
    """Metin içinde geçen aciliyet anahtar kelimelerini döndür."""
    norm = _normalize(text)
    hits: List[str] = []
    for kw in URGENCY_KEYWORDS.keys():
        if kw in norm:
            hits.append(kw)
    # Tekilleştir, kısa kelimeleri at
    seen = set()
    out: List[str] = []
    for k in hits:
        if k not in seen and len(k) >= 2:
            seen.add(k)
            out.append(k)
    return out


def _people_bonus(people_count: int) -> int:
    """Kişi sayısı arttıkça artan logaritmik bonus, max 20."""
    if people_count <= 1:
        return 0
    # log2(2)=1 -> 4, log2(10)~3.3 -> 13, log2(50)~5.6 -> 20+
    import math

    raw = int(math.log2(max(people_count, 2)) * 4)
    return min(raw, 20)


def compute_urgency(
    text: str,
    category: str,
    people_count: int = 1,
) -> Tuple[int, Dict]:
    """Aciliyet skoru hesapla ve breakdown döndür.

    Returns:
        (score 0-100, breakdown dict)
    """
    base = 20
    keyword_hits = extract_keywords(text)
    keyword_score = sum(URGENCY_KEYWORDS[k] for k in keyword_hits)
    # Tek bir çağrıda anahtar kelime toplamı 40'ı aşmasın (gürültü sınırı)
    keyword_score = min(keyword_score, 40)

    cat_score = CATEGORY_WEIGHT.get(category, 2)
    people_score = _people_bonus(people_count)

    total = base + keyword_score + cat_score + people_score
    total = max(0, min(100, total))

    breakdown = {
        "base": base,
        "keyword_score": keyword_score,
        "category_weight": cat_score,
        "people_bonus": people_score,
        "matched_keywords": keyword_hits,
        "total": total,
    }
    return total, breakdown


def urgency_band(score: int) -> str:
    """Skoru bantlara ayır."""
    if score >= 80:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 20:
        return "medium"
    return "low"
