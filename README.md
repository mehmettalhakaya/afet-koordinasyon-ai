# AfetKoordinasyonAI

> Afet anında gelen yardım çağrılarını analiz eden, kategorilere ayıran,
> aciliyet puanı veren, benzer çağrıları gruplayan ve harita üzerinde gösteren
> **eğitim/demo amaçlı** web uygulaması.
>
> Türkçe NLP · FastAPI · React + Leaflet · scikit-learn · SQLite

---

## ⚠️ Önemli Uyarı

Bu proje **GERÇEK acil durumlarda kullanılacak resmi bir koordinasyon sistemi
DEĞİLDİR**. Sadece eğitim, demo, araştırma ve portföy amaçlıdır.

- Tüm veriler **sentetiktir**: gerçek kişi, gerçek telefon, gerçek adres içermez.
- Üretimde kullanılmamalı, ilan edilmemeli, resmi bir kanal olarak sunulmamalıdır.
- **Gerçek acil durumda lütfen 112'yi arayın. AFAD ve Kızılay gibi resmi
  kurumları takip edin.**

Bu uyarı arayüzün her sayfasında üst kısımda da gösterilir.

---

## İçindekiler

1. [Özellikler](#özellikler)
2. [Mimari](#mimari)
3. [Kurulum](#kurulum)
4. [Backend Çalıştırma](#backend-çalıştırma)
5. [Frontend Çalıştırma](#frontend-çalıştırma)
6. [Sentetik Veri Üretimi](#sentetik-veri-üretimi)
7. [Docker ile Çalıştırma](#docker-ile-çalıştırma)
8. [API Endpointleri](#api-endpointleri)
9. [AI/NLP Yaklaşımı](#ainlp-yaklaşımı)
10. [Aciliyet Skoru Mantığı](#aciliyet-skoru-mantığı)
11. [Duplicate / Cluster Mantığı](#duplicate--cluster-mantığı)
12. [Benzer Açık Kaynak Projelerden Öğrenilenler](#benzer-açık-kaynak-projelerden-öğrenilenler)
13. [Geliştirme Fikirleri](#geliştirme-fikirleri)
14. [Portföyde Nasıl Sunulur?](#portföyde-nasıl-sunulur)
15. [Ekran Görüntüleri](#ekran-görüntüleri)

---

## Özellikler

- 📝 **Yardım çağrısı girişi** – Metin + şehir + ilçe + kişi sayısı (telefon ve gerçek adres istenmez).
- 🏷️ **Türkçe çağrı sınıflandırma** – 10 kategori: `enkaz, saglik, su, gida, barinma, ilac, ulasim, kayip_kisi, elektrik_isinma, diger`.
- 🚨 **0-100 aciliyet skoru** – Anahtar kelime + kategori ağırlığı + kişi sayısı bonusu.
- 🔁 **Duplicate / cluster tespiti** – TF-IDF cosine + şehir/ilçe yerel boost.
- 🗺️ **Türkiye haritası** – Leaflet üzerinde aciliyet rengine göre marker'lar, popup detay.
- 📊 **Dashboard** – Toplam çağrı, ortalama aciliyet, kategori/şehir dağılımı, son eklenenler, en aciller, şüpheli tekrar.
- 🧪 **"Analiz Et" demo** – Veritabanına yazmadan tahmin, skor ve benzerleri canlı göster.
- ♻️ **Modeli yeniden eğitme** – `POST /api/retrain` ile tek tıkta retrain.
- ✅ **Pytest testleri** – 16+ test, urgency, classifier ve API endpoint kapsamı.
- 🔴 **Gerçek zamanlı WebSocket akışı** – Yeni çağrı eklendiğinde dashboard ve harita anlık güncellenir (manuel reload yok).
- 🗂️ **Marker clustering** – Yakın marker'lar otomatik gruplanır, zoom yapılınca açılır (`react-leaflet-cluster`).
- 🔥 **Heatmap (yoğunluk haritası)** – Çağrıların yoğunlaştığı bölgeler ısı renkleriyle görünür (`leaflet.heat`). Marker/Heatmap/İkisi geçişi.
- ✅ **GitHub Actions CI** – Push'ta otomatik pytest (Python 3.11+3.12 matrix) + frontend type-check + build.

---

## Mimari

```
┌──────────────────────────────┐         ┌──────────────────────────────┐
│  Frontend (Vite + React + TS)│  HTTP   │ Backend (FastAPI + SQLAlchemy)│
│  - Dashboard / Map / Forms   │ ──────▶ │ - /api/calls /analyze /dashboard│
│  - Leaflet (OSM tiles)       │         │ - TF-IDF + LogReg classifier │
│  - React Router              │         │ - Urgency rule engine        │
└──────────────────────────────┘         │ - Cosine dedup               │
                                         └──────────────┬───────────────┘
                                                        │
                                                  SQLite (afet.db)
                                                  + classifier.pkl
                                                  + synthetic_calls.csv
```

**Tek tablolu MVP** (`help_calls`). Çağrı geldiğinde:
1. Sınıflandırıcı kategoriyi tahmin eder.
2. Kural tabanlı aciliyet skoru hesaplanır.
3. TF-IDF cosine ile son 500 çağrıya karşı benzerlik bakılır.
4. Benzer varsa `cluster_id` paylaşılır, çok benzerse `duplicate_suspected=True`.
5. Koordinat verilmediyse şehir/ilçe için yaklaşık demo koordinat üretilir.

---

## Kurulum

Gereksinimler:
- Python 3.10+
- Node.js 18+
- (Opsiyonel) Docker + docker-compose

```bash
git clone <bu-repo>
cd afet-koordinasyon-ai
```

## Backend Çalıştırma

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python -m data.generate_synthetic_data        # 240 sentetik çağrı üret
uvicorn app.main:app --reload --port 8000
```

API hazır: <http://localhost:8000>
Swagger: <http://localhost:8000/docs>

Testler:

```bash
pytest
```

## Frontend Çalıştırma

```bash
cd frontend
npm install
npm run dev
```

Açılış: <http://localhost:5173>

Dev sunucusu `/api` ve `/health` isteklerini backend'e proxy'ler.

## Sentetik Veri Üretimi

```bash
cd backend
python -m data.generate_synthetic_data            # varsayılan 240
python -m data.generate_synthetic_data --n 500    # daha fazla
```

Üretilen dosya: `backend/data/synthetic_calls.csv`

Sentetik veri:
- 8 şehir × birkaç ilçe (Hatay, Kahramanmaraş, Adıyaman, Gaziantep, Malatya, Osmaniye, Diyarbakır, Adana)
- 10 kategoriye dengesiz dağılmış (enkaz/sağlık daha sık)
- Gerçek kişi/telefon/adres yok

## Docker ile Çalıştırma

Tek komutla backend + frontend:

```bash
docker compose up --build
```

- Frontend: <http://localhost:5173>
- Backend:  <http://localhost:8000>

> Önce lokal Python+Node ile çalıştırıp doğrulamanız önerilir.

---

## API Endpointleri

| Method | Path | Açıklama |
|---|---|---|
| GET | `/` | Servis adı, versiyon, uyarı |
| GET | `/health` | Sağlık + sınıflandırıcı durumu |
| GET | `/api/calls` | Filtreli liste (`city`, `category`, `min_urgency`, `duplicate_suspected`, `limit`) |
| GET | `/api/calls/{id}` | Tek çağrı |
| POST | `/api/calls` | Yeni çağrı (sınıflandır + skor + dedup) |
| POST | `/api/analyze` | DB'ye yazmadan analiz |
| GET | `/api/dashboard` | Panel istatistikleri |
| POST | `/api/retrain` | Modeli yeniden eğit |
| WS  | `/ws/calls` | Yeni çağrı broadcast akışı (gerçek zamanlı) |

Örnek istek:

```bash
curl -X POST http://localhost:8000/api/calls \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hatay Antakya da enkaz altında 3 kişi var, vinç ve sağlık ekibi gerekiyor.",
    "city": "Hatay",
    "district": "Antakya",
    "people_count": 3
  }'
```

---

## AI/NLP Yaklaşımı

MVP, hızlı çalışsın diye **klasik ML** ile başlatıldı:

- **Vektörleştirme:** `TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True)` – Türkçeyi yeterince yakalar.
- **Model:** `LogisticRegression(max_iter=1000, C=2.0, class_weight="balanced")` – yorumlanabilir ve hızlı.
- **Eğitim verisi:** `backend/data/synthetic_calls.csv` (240 örnek).
- **Servis:** İlk istekte pickle'lanır (`data/classifier.pkl`). `POST /api/retrain` ile yenilenir.

Doğruluk sentetik veri üzerinde ~0.85+ civarında. **Bu, abartılı bir sayı değildir** çünkü veriler şablon tabanlıdır - gerçek dünya verisinde değişir; "Geliştirme Fikirleri" bölümüne bakın.

İleri yönlü tasarım:
- `classifier_service.predict()` imzası multi-label'a yakın (her kategoriye olasılık döner).
- `OneVsRestClassifier(LinearSVC)` ile multi-label'a geçiş trivial.
- Türkçe transformer (BERTurk) entegrasyonu README'de "geliştirme fikri" olarak listelendi.

---

## Aciliyet Skoru Mantığı

`backend/app/services/urgency.py` içindeki kural-tabanlı motor:

```
score = clamp_0_100(
    20                           # taban
  + min(40, Σ anahtar_kelime_ağırlıkları)
  + kategori_ağırlığı            # enkaz/saglik > su/gida
  + min(20, ⌊log2(people_count) * 4⌋)
)
```

Bantlar:
- **80-100** → ÇOK ACİL (kırmızı koyu)
- **50-79**  → YÜKSEK (kırmızı)
- **20-49**  → ORTA (sarı)
- **0-19**   → DÜŞÜK (gri)

Anahtar kelime ağırlıkları örneği: `mahsur=25`, `kanama=22`, `nefes alamıyor=30`,
`bebek=22`, `çocuk=18`, `acil=12`...

`POST /api/analyze` cevabında `urgency_breakdown` ile **her bileşen ayrı
gösterilir** – kullanıcı puanın neden o olduğunu anlayabilir (yorumlanabilirlik).

---

## Duplicate / Cluster Mantığı

`backend/app/services/deduplication.py`:

1. Yeni çağrı geldiğinde son 500 çağrı çekilir.
2. Birleştirilmiş corpus üzerinde TF-IDF + cosine similarity hesaplanır.
3. Eşikler:
   - **Şüpheli tekrar:** cosine ≥ 0.78
   - **Aynı cluster:** cosine ≥ 0.55
4. **Yerel boost:** Şehir + ilçe eşleşirse eşikler 0.08 düşer (aynı yerden gelen aynı içerik daha kolay duplicate sayılır).
5. En benzerin `cluster_id`'si yeni çağrıya verilir; yoksa yeni cluster açılır.
6. Benzer çağrıların `similar_count` alanları +1 artırılır.

---

## Benzer Açık Kaynak Projelerden Öğrenilenler

Geliştirmeye başlamadan önce incelenen açık kaynak referansları
(yalnızca fikir/mimari, kod kopyalanmadı):

- **DisasterConnect** – gönüllü/kaynak eşleştirme; bizde MVP dışı, "geliştirme fikri".
- **Turkey-Earthquake-2023-GeoData** – jeo-veri snapshot'ı; bizde Leaflet ile statik OSM yeterli.
- **DisasterTechCrew / awesome-disastertech** – ekosistem haritası, hangi alanların eksik olduğunu göstermesi açısından faydalı.
- **CrisisNLP, HumAID, crisis_nlp_progress** – kriz tweet sınıflandırma literatürü; ngram + linear classifier'ın güçlü baseline olduğunu doğruluyor.
- **Humanitarian-Data-Classification** – fastText ile kategori atama; benzer bir yaklaşımı sklearn ile yaptık.
- **Conflict-Crisis-Mapping-Project** – Ushahidi tarzı UI yaklaşımı; renkli marker + popup paterni bu projelerde yaygın.

**Çıkarımlar:**
- Çoğu projede aciliyet skoru ya yok ya çok basit – burada açıkça yazılı kurallarla yaptık.
- Türkçe NLP yetersiz – sentetik Türkçe veri ve TF-IDF baseline ile bu boşluğu doldurduk.
- Çoğu repo testsiz – pytest ile kapatıldı.
- Çoğu repo "tek koşuluk dataset" – burada `/api/retrain` ile canlı yeniden eğitme var.

---

## Geliştirme Fikirleri

İleri seviye, MVP dışı:

- 🔌 **Gerçek zamanlı WebSocket çağrı akışı** – yeni çağrıları push ile yay.
- 🤖 **Transformer tabanlı Türkçe model** – BERTurk fine-tune ile sınıflandırma.
- 🏷️ **Multi-label sınıflandırma** – bir çağrı aynı anda hem `enkaz` hem `saglik` olabilir.
- 🚗 **Gönüllü/ekip atama optimizasyonu** – kapasite vs talep eşleştirme.
- 🗺️ **Rota optimizasyonu** – araç başına çağrı sıralaması (TSP/VRP yaklaşımı).
- 📱 **Offline-first mobil uygulama** – ağ yokken bile çağrı al, sonra senkronize et.
- 🚨 **Yanlış bilgi / anomali tespiti** – spike anomalileri, çelişen çağrılar.
- 🔗 **AFAD / Kızılay / belediye entegrasyon taslağı** – salt teorik, kurumsal API'ler.
- 🔐 **Rol bazlı admin paneli** – operatör, koordinatör, gönüllü rolleri (RBAC).
- 🧠 **Yaklaşık komşu arama** – FAISS / hnswlib ile dedup'u büyük veride hızlı yap.

---

## Portföyde Nasıl Sunulur?

1. **README başlangıcı** – problem + demo amacı + ekran görüntüsü.
2. **GIF demo** – yeni çağrı oluştur, harita üzerinde marker beliriyor, dashboard güncelleniyor.
3. **Tech stack rozeti** – FastAPI · React · scikit-learn · Leaflet · SQLite · pytest · Docker.
4. **Vurgulanacaklar:**
   - Türkçe NLP üzerinde çalışıyorsun (yerel problem).
   - Sınıflandırma + aciliyet skoru + dedup üç ayrı problem; her birini ayrı servis olarak çözmüşsün.
   - 16+ test, modüler kod, Docker.
   - "Demo / gerçek değil" şeffaflığı – sorumlu mühendislik vurgusu.
5. **CV satırı önerisi:**
   *"AfetKoordinasyonAI – Türkçe afet çağrılarını TF-IDF + Logistic
   Regression ile sınıflandıran, kural-tabanlı aciliyet skoru üreten ve
   cosine benzerlikle duplicate tespiti yapan FastAPI + React + Leaflet
   tabanlı demo platform. Pytest testli, Docker'lı, açık kaynak."*
6. **Mülakat anlatımı:**
   - Neden TF-IDF + LogReg? (Hız, yorumlanabilirlik, baseline.)
   - Neden kural-tabanlı urgency? (ML için etiketli veri yok, deterministik.)
   - Multi-label'a nasıl geçilir? (predict_proba zaten dağılım dönüyor, eşik koy.)
   - Üretime nasıl gider? (Postgres, Celery, Redis cache, monitoring, RBAC.)

---

## Ekran Görüntüleri

> Aşağıdaki yerlere `docs/` klasörüne PNG/GIF koyup linkle:

- `docs/dashboard.png` – Panel görünümü
- `docs/map.png` – Harita üzerinde renkli marker'lar
- `docs/new_call.png` – Yeni çağrı formu
- `docs/analyze.png` – Analiz demo (skor breakdown + benzer çağrılar)
- `docs/demo.gif` – Uçtan uca akış

```markdown
![Dashboard](docs/dashboard.png)
![Harita](docs/map.png)
![Analiz](docs/analyze.png)
```

---

## Lisans

MIT. Sentetik veriler bu repo ile birlikte üretilir ve özgürce kullanılabilir.

---

## Tekrar Hatırlatma

Bu proje **GERÇEK acil durumlarda kullanılmamalıdır**. Acil durumda
**112**'yi arayın, AFAD ve Kızılay'ı takip edin.
