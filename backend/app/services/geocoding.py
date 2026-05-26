"""Demo amaçlı yaklaşık koordinat sözlüğü.

Bu gerçek bir geocoding servisi DEĞİLDİR.
Sadece harita üzerinde marker gösterebilmek için il/ilçe bazlı yaklaşık
merkez koordinatlar barındırır. Gerçek sistemde Nominatim, Mapbox veya
yerli bir geocoder kullanılmalıdır.

Türkiye'nin 81 ilinin tamamı + bazı ilçe ofsetleri (deprem bölgesi odaklı).
"""
from __future__ import annotations

import random
from typing import Optional, Tuple

# Türkiye 81 il merkezi (yaklaşık) - demo amaçlı.
# Hem Türkçe karakterli hem ASCII varyantı, hem küçük harfli giriş için.
CITY_CENTERS: dict[str, tuple[float, float]] = {
    # Deprem bölgesi (ilçe ofsetleri olan iller)
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
    # Diğer iller (alfabetik)
    "afyonkarahisar": (38.7569, 30.5387),
    "afyon": (38.7569, 30.5387),
    "ağrı": (39.7191, 43.0503),
    "agri": (39.7191, 43.0503),
    "aksaray": (38.3687, 34.0370),
    "amasya": (40.6499, 35.8353),
    "ankara": (39.9334, 32.8597),
    "antalya": (36.8969, 30.7133),
    "ardahan": (41.1105, 42.7022),
    "artvin": (41.1828, 41.8183),
    "aydın": (37.8560, 27.8416),
    "aydin": (37.8560, 27.8416),
    "balıkesir": (39.6484, 27.8826),
    "balikesir": (39.6484, 27.8826),
    "bartın": (41.6358, 32.3375),
    "bartin": (41.6358, 32.3375),
    "batman": (37.8812, 41.1351),
    "bayburt": (40.2549, 40.2228),
    "bilecik": (40.1450, 29.9793),
    "bingöl": (38.8854, 40.4986),
    "bingol": (38.8854, 40.4986),
    "bitlis": (38.4001, 42.1095),
    "bolu": (40.7392, 31.6112),
    "burdur": (37.7203, 30.2900),
    "bursa": (40.1885, 29.0610),
    "çanakkale": (40.1553, 26.4142),
    "canakkale": (40.1553, 26.4142),
    "çankırı": (40.6013, 33.6134),
    "cankiri": (40.6013, 33.6134),
    "çorum": (40.5499, 34.9533),
    "corum": (40.5499, 34.9533),
    "denizli": (37.7765, 29.0864),
    "düzce": (40.8438, 31.1565),
    "duzce": (40.8438, 31.1565),
    "edirne": (41.6818, 26.5623),
    "erzincan": (39.7464, 39.4914),
    "erzurum": (39.9000, 41.2700),
    "eskişehir": (39.7767, 30.5206),
    "eskisehir": (39.7767, 30.5206),
    "giresun": (40.9128, 38.3895),
    "gümüşhane": (40.4386, 39.5086),
    "gumushane": (40.4386, 39.5086),
    "hakkari": (37.5744, 43.7408),
    "iğdır": (39.9237, 44.0450),
    "igdir": (39.9237, 44.0450),
    "isparta": (37.7648, 30.5566),
    "istanbul": (41.0082, 28.9784),
    "i̇stanbul": (41.0082, 28.9784),
    "izmir": (38.4192, 27.1287),
    "i̇zmir": (38.4192, 27.1287),
    "karabük": (41.2061, 32.6204),
    "karabuk": (41.2061, 32.6204),
    "karaman": (37.1759, 33.2287),
    "kars": (40.6013, 43.0975),
    "kastamonu": (41.3887, 33.7827),
    "kayseri": (38.7312, 35.4787),
    "kırıkkale": (39.8468, 33.5153),
    "kirikkale": (39.8468, 33.5153),
    "kırklareli": (41.7333, 27.2167),
    "kirklareli": (41.7333, 27.2167),
    "kırşehir": (39.1425, 34.1709),
    "kirsehir": (39.1425, 34.1709),
    "kocaeli": (40.8533, 29.8815),
    "konya": (37.8746, 32.4932),
    "kütahya": (39.4242, 29.9833),
    "kutahya": (39.4242, 29.9833),
    "manisa": (38.6191, 27.4289),
    "mardin": (37.3212, 40.7245),
    "mersin": (36.8121, 34.6415),
    "muğla": (37.2153, 28.3636),
    "mugla": (37.2153, 28.3636),
    "muş": (38.7432, 41.5065),
    "mus": (38.7432, 41.5065),
    "nevşehir": (38.6939, 34.6857),
    "nevsehir": (38.6939, 34.6857),
    "niğde": (37.9667, 34.6833),
    "nigde": (37.9667, 34.6833),
    "ordu": (40.9839, 37.8764),
    "rize": (41.0201, 40.5234),
    "sakarya": (40.7569, 30.3786),
    "samsun": (41.2867, 36.3300),
    "siirt": (37.9444, 41.9333),
    "sinop": (42.0231, 35.1531),
    "sivas": (39.7477, 37.0179),
    "şırnak": (37.5164, 42.4611),
    "sirnak": (37.5164, 42.4611),
    "tekirdağ": (40.9833, 27.5167),
    "tekirdag": (40.9833, 27.5167),
    "tokat": (40.3167, 36.5500),
    "trabzon": (41.0027, 39.7168),
    "tunceli": (39.1080, 39.5483),
    "uşak": (38.6823, 29.4082),
    "usak": (38.6823, 29.4082),
    "van": (38.4942, 43.3800),
    "yalova": (40.6500, 29.2667),
    "yozgat": (39.8200, 34.8050),
    "zonguldak": (41.4564, 31.7987),
}

# Bazı ilçeler için ufak ofset sözlüğü (deprem bölgesi odaklı)
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
