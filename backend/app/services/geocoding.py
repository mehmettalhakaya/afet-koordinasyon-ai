"""Demo amaçlı yaklaşık koordinat sözlüğü.

Bu gerçek bir geocoding servisi DEĞİLDİR.
Sadece harita üzerinde marker gösterebilmek için şehir/ilçe bazlı
yaklaşık merkez koordinatlar barındırır. Gerçek sistemde Nominatim,
Mapbox veya yerli bir geocoder kullanılmalıdır.
"""
from __future__ import annotations

import random
from typing import Optional, Tuple

# Yaklaşık il merkezleri (kabaca - demo için)
CITY_CENTERS = {
    "hatay": (36.2025, 36.1606),
    "kahramanmaraş": (37.5847, 36.9264),
    "kahramanmaras": (37.5847, 36.9264),
    "adıyaman": (37.7648, 38.2786),
    "adiyaman": (37.7648, 38.2786),
    "gaziantep": (37.0660, 37.3833),
    "malatya": (38.3552, 38.3095),
    "osmaniye": (37.0682, 36.2475),
    "diyarbakır": (37.9144, 40.2306),
    "diyarbakir": (37.9144, 40.2306),
    "adana": (37.0000, 35.3213),
    "şanlıurfa": (37.1671, 38.7955),
    "sanliurfa": (37.1671, 38.7955),
    "kilis": (36.7184, 37.1212),
    "elazığ": (38.6810, 39.2264),
    "elazig": (38.6810, 39.2264),
    "istanbul": (41.0082, 28.9784),
}

# Bazı ilçeler için ufak ofset sözlüğü (zorunlu değil)
DISTRICT_OFFSET = {
    ("hatay", "antakya"): (36.2065, 36.1611),
    ("hatay", "iskenderun"): (36.5810, 36.1717),
    ("hatay", "defne"): (36.1980, 36.1900),
    ("kahramanmaras", "onikişubat"): (37.6105, 36.9381),
    ("kahramanmaras", "dulkadiroğlu"): (37.5750, 36.9450),
    ("kahramanmaras", "elbistan"): (38.2078, 37.1908),
    ("gaziantep", "şahinbey"): (37.0606, 37.3672),
    ("gaziantep", "nurdağı"): (37.1786, 36.7308),
    ("gaziantep", "islahiye"): (37.0297, 36.6356),
    ("adıyaman", "merkez"): (37.7648, 38.2786),
    ("adıyaman", "besni"): (37.6925, 37.8639),
    ("malatya", "yeşilyurt"): (38.2989, 38.2400),
    ("malatya", "battalgazi"): (38.3919, 38.3461),
}


def _key(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    return s.strip().lower()


def approximate_coords(
    city: str,
    district: Optional[str] = None,
    seed_text: Optional[str] = None,
    jitter: float = 0.04,
) -> Optional[Tuple[float, float]]:
    """Şehir/ilçe için yaklaşık koordinat döndür. Bilinmiyorsa None.

    Aynı metin -> aynı koordinat olsun diye seed_text bazlı deterministik jitter.
    """
    city_k = _key(city) or ""
    district_k = _key(district)

    base: Optional[Tuple[float, float]] = None
    if district_k and (city_k, district_k) in DISTRICT_OFFSET:
        base = DISTRICT_OFFSET[(city_k, district_k)]
    elif city_k in CITY_CENTERS:
        base = CITY_CENTERS[city_k]

    if base is None:
        return None

    # Marker'ların çakışmaması için küçük deterministik jitter
    rng = random.Random((seed_text or city_k) + (district_k or ""))
    dlat = (rng.random() - 0.5) * jitter
    dlon = (rng.random() - 0.5) * jitter
    return (base[0] + dlat, base[1] + dlon)
