"""Sentetik (yapay) Türkçe afet çağrısı veri üretici.

UYARI: Buradaki veriler tamamen YAPAYDIR.
  - Gerçek kişi, gerçek telefon, gerçek adres İÇERMEZ.
  - Sadece eğitim ve demo amacıyla, sınıflandırma modelinin eğitilmesi
    ve UI'ın somut bir veri üzerinde gösterilebilmesi için kullanılır.

Kullanım:
    cd backend
    python -m data.generate_synthetic_data         # data/synthetic_calls.csv üretir
    python -m data.generate_synthetic_data --n 400 # daha fazla örnek
"""
from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple

OUT_PATH = Path(__file__).resolve().parent / "synthetic_calls.csv"

# Şehir -> ilçeler (yaklaşık, demo amaçlı)
CITY_DISTRICTS: Dict[str, List[str]] = {
    "Hatay": ["Antakya", "Defne", "İskenderun", "Samandağ", "Arsuz", "Kırıkhan"],
    "Kahramanmaraş": ["Onikişubat", "Dulkadiroğlu", "Elbistan", "Türkoğlu", "Pazarcık"],
    "Adıyaman": ["Merkez", "Besni", "Kahta", "Gölbaşı"],
    "Gaziantep": ["Şahinbey", "Şehitkamil", "Nurdağı", "İslahiye", "Nizip"],
    "Malatya": ["Battalgazi", "Yeşilyurt", "Doğanşehir", "Akçadağ"],
    "Osmaniye": ["Merkez", "Düziçi", "Kadirli", "Bahçe"],
    "Diyarbakır": ["Bağlar", "Yenişehir", "Kayapınar", "Sur"],
    "Adana": ["Seyhan", "Yüreğir", "Çukurova", "Sarıçam"],
}

# Kategori şablonları (Türkçe).
# `{n}` -> kişi sayısı, `{c}` -> şehir, `{d}` -> ilçe.
TEMPLATES: Dict[str, List[str]] = {
    "enkaz": [
        "{c} {d}'da enkaz altında {n} kişi var, acil vinç ve arama kurtarma ekibi lazım.",
        "Bina yıkıldı, {d} bölgesinde {n} kişi mahsur kaldı. Ses geliyor.",
        "{c} {d} mahallesinde göçük altında aile var, {n} kişi içeride.",
        "Enkaz altından sesler duyuyoruz, {n} kişilik aile, {d} adres tarif edebilirim.",
        "Apartman çöktü, {c} {d}, yaklaşık {n} kişi mahsur durumda, müdahale gerekli.",
        "Çatı çöktü {c} ilçesinde, {n} yaralı enkaz altında olabilir.",
        "Komşumuzun evi yıkıldı {c} {d}, içeride çocuklu aile var, {n} kişi mahsur.",
    ],
    "saglik": [
        "{c} {d}'de yaralı var, acil sağlık ekibi lazım, kanama duruyor değil.",
        "Yaşlı amca nefes alamıyor, {c} {d}, ambulans gerekli.",
        "Hamile kadın sancılanıyor, {c} {d} mahallesinde, doktor lazım.",
        "{n} kişi yaralı, kırık ve kanama var {c} ilçesinde, sağlık ekibi yönlendirin.",
        "Bilinci kapalı bir erkek var çadır kentte, {c} {d}, müdahale gerek.",
        "Bebek ateşi çok yüksek, {c} {d}, doktor veya sağlıkçı gerekli.",
        "Kalp krizi geçiriyor olabilir, {c} {d}, ambulans çağırın lütfen.",
        "Yaralılar var, ilk yardım eksik, {c} {d}, sağlık ekibi rica ediyoruz.",
    ],
    "su": [
        "{c} {d} çadır alanında 3 gündür su yok, susuz kaldık.",
        "İçme suyu bitti {c} {d}, {n} kişilik gruba acil su lazım.",
        "Su kuyruğu çok uzun, ulaşamıyoruz {c} ilçesinde, su tankeri yönlendirin.",
        "Çocuklar susuz, {c} {d} mahallesinde temiz suya ihtiyaç var.",
        "Şebeke suyu akmıyor, {c} {d}, içme suyu desteği lazım.",
        "{c} {d} köyünde su yok, {n} hane susuz durumda.",
    ],
    "gida": [
        "{c} {d}'de yemek dağıtımı bize ulaşmadı, aç kaldık {n} kişiyiz.",
        "Bebek maması bitti {c} {d}, acil mama desteği lazım.",
        "{c} {d} çadır alanında {n} kişilik gruba sıcak yemek gerekli.",
        "Yiyecek paketi bulamıyoruz, {c} {d}, dağıtım noktası kalabalık.",
        "Ekmek ve kuru gıda lazım {c} {d}, çocuklar aç.",
        "Mama ve bezimiz bitti {c} ilçesinde, bebeklere yardım gerek.",
    ],
    "barinma": [
        "{c} {d}'de çadır yok, {n} kişi açıkta kalıyor.",
        "Soğukta çadırsız aileyiz {c} {d}, barınma yeri lazım.",
        "Konteyner bekliyoruz {c} {d}, {n} kişi yıkık binada uyuyor.",
        "Çadırımız yırtıldı, {c} {d}, yeni barınak gerekli.",
        "Battaniye ve çadır lazım {c} {d}, açıkta yatıyoruz.",
        "{c} ilçesinde {n} aileye sığınak gerekli, geçici yerleşim alanı yok.",
    ],
    "ilac": [
        "Babamın tansiyon ilacı bitti, {c} {d}, eczaneye ulaşamıyoruz.",
        "İnsülin lazım {c} {d}, şeker hastası amca için acil.",
        "{c} {d}'de kalp ilacı bulamıyoruz, eczane kapalı.",
        "Astım spreyi bitti, {c} {d}, çocuk için ilaç gerek.",
        "Reçeteli ilaç eksik {c} ilçesinde, sağlık ekibinden destek bekliyoruz.",
        "Antibiyotik ve ağrı kesici lazım {c} {d}, yaralı için.",
    ],
    "ulasim": [
        "{c} {d}'ye giden yol kapalı, ekipler ulaşamıyor.",
        "Köprü çöktü {c}, ulaşım sağlanamıyor, alternatif yol lazım.",
        "Yol enkaz dolu {c} {d}, iş makinesi gerek.",
        "Otobüs bulamadık {c} {d}, tahliye için araç lazım.",
        "Akaryakıt yok {c}, ulaşım durdu, yakıt desteği gerek.",
        "Tahliye edilmemiz lazım {c} {d}, {n} kişiyiz, ulaşım yok.",
    ],
    "kayip_kisi": [
        "Annem kayıp, {c} {d}'de en son görüldü, telefonu çekmiyor.",
        "Kardeşim depremden beri ulaşılamıyor, {c} {d}, bilgisi olan?",
        "{c} {d} mahallesinden tanıdığım iki kişi kayıp.",
        "Komşumuz enkazdan çıktı ama nereye götürüldüğünü bulamıyoruz, {c} {d}.",
        "Çocuk kayıp, {c} {d}, 8 yaşında, lütfen yardım edin.",
        "Yaşlı dedemize ulaşamıyoruz, {c} {d}'de yaşıyordu.",
    ],
    "elektrik_isinma": [
        "{c} {d}'de elektrik yok 2 gündür, sobamız bile yanmıyor.",
        "Doğalgaz kesik {c} {d}, donuyoruz çocuklarla.",
        "{n} hane elektriksiz {c} ilçesinde, jeneratör gerek.",
        "Soba odun bitmiş {c} {d}, ısınma desteği lazım.",
        "Soğuk hava çadırı donduruyor, {c} {d}, ısıtıcı gerek.",
        "Elektrik direği devrildi, {c} {d}, mahalleyi karanlık bastı.",
    ],
    "diger": [
        "{c} {d}'de psikolojik destek lazım, çocuklar travmatik.",
        "Hijyen malzemesi eksik {c} {d}, ped, sabun, deterjan lazım.",
        "Tuvalet yetersiz {c} {d} çadır kentinde, sağlık riski var.",
        "Bilgi alamıyoruz {c}, koordinasyon bilgisi paylaşın.",
        "Gönüllüye ihtiyaç var {c} {d}, eli iş tutan herkes lazım.",
        "Çöp birikti çadır alanda {c} {d}, hijyen sorun.",
    ],
}


def _people_count_for(category: str) -> int:
    """Kategoriye göre makul bir kişi sayısı üret."""
    if category in {"enkaz", "saglik", "kayip_kisi"}:
        return random.choices([1, 2, 3, 4, 5, 6, 8, 10, 15], k=1)[0]
    if category in {"barinma", "gida", "su", "elektrik_isinma"}:
        return random.choices([3, 4, 5, 6, 8, 10, 12, 20, 30, 50], k=1)[0]
    return random.choices([1, 1, 2, 3, 5, 8], k=1)[0]


def _approximate_coord(city: str, district: str, salt: str) -> Tuple[float, float]:
    """Demo amaçlı yaklaşık koordinat (jitter ile)."""
    # geocoding modülünü kullanmadan basit fallback:
    base = {
        "Hatay": (36.2025, 36.1606),
        "Kahramanmaraş": (37.5847, 36.9264),
        "Adıyaman": (37.7648, 38.2786),
        "Gaziantep": (37.0660, 37.3833),
        "Malatya": (38.3552, 38.3095),
        "Osmaniye": (37.0682, 36.2475),
        "Diyarbakır": (37.9144, 40.2306),
        "Adana": (37.0000, 35.3213),
    }.get(city, (39.0, 35.0))
    rng = random.Random(city + district + salt)
    dlat = (rng.random() - 0.5) * 0.08
    dlon = (rng.random() - 0.5) * 0.08
    return (base[0] + dlat, base[1] + dlon)


def generate(n: int = 240, seed: int = 42) -> List[dict]:
    random.seed(seed)
    cities = list(CITY_DISTRICTS.keys())
    categories = list(TEMPLATES.keys())

    rows: List[dict] = []
    base_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=2)
    for i in range(n):
        # Kategori dengesini hafifçe ağırlıklı yap (enkaz/saglik daha çok)
        category = random.choices(
            categories,
            weights=[3, 3, 2, 2, 2, 2, 2, 2, 2, 1],  # CATEGORIES sırasına bağlı
            k=1,
        )[0]
        city = random.choice(cities)
        district = random.choice(CITY_DISTRICTS[city])
        people = _people_count_for(category)
        template = random.choice(TEMPLATES[category])
        text = template.format(c=city, d=district, n=people)
        # Kasıtlı varyasyon: bazı çağrılara "lütfen"/"acil"/"yardım edin" ekle
        if random.random() < 0.25:
            text = "ACİL: " + text
        if random.random() < 0.2:
            text = text + " Lütfen yardım edin."
        lat, lon = _approximate_coord(city, district, salt=str(i))
        created_at = base_time + timedelta(minutes=random.randint(0, 60 * 48))

        rows.append(
            {
                "id": i + 1,
                "text": text,
                "city": city,
                "district": district,
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "people_count": people,
                "label": category,
                "created_at": created_at.isoformat(timespec="seconds"),
            }
        )
    return rows


def write_csv(rows: List[dict], path: Path = OUT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "text",
        "city",
        "district",
        "lat",
        "lon",
        "people_count",
        "label",
        "created_at",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sentetik afet çağrısı üretici (demo)")
    parser.add_argument("--n", type=int, default=240, help="Üretilecek satır sayısı")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()
    rows = generate(n=args.n, seed=args.seed)
    write_csv(rows, args.out)
    print(f"OK: {len(rows)} satır yazıldı -> {args.out}")


if __name__ == "__main__":
    main()
