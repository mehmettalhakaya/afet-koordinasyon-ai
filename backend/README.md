# AfetKoordinasyonAI – Backend

Bu klasör, AfetKoordinasyonAI projesinin FastAPI tabanlı backend servisidir. Yardım çağrısı kayıtlarını alır, Türkçe NLP sınıflandırması yapar, aciliyet skoru üretir, benzer/tekrar çağrıları tespit eder, dashboard istatistikleri sağlar ve yeni çağrıları WebSocket üzerinden yayınlar.

> Bu servis eğitim/demo amaçlıdır. Gerçek afet koordinasyonu veya resmi acil durum kullanımı için tasarlanmamıştır.

---

## Teknoloji Yığını

- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Pydantic v2
- scikit-learn
- pandas / numpy
- Pytest
- WebSocket

---

## Klasör Yapısı

```text
backend/
├── app/
│   ├── routers/
│   │   ├── analyze.py       # Kaydetmeden analiz endpointi
│   │   ├── calls.py         # Çağrı CRUD, retrain ve çağrı oluşturma
│   │   └── dashboard.py     # Dashboard istatistikleri
│   ├── services/
│   │   ├── classifier.py    # TF-IDF + Logistic Regression sınıflandırıcı
│   │   ├── dashboard.py     # SQL agregasyonları
│   │   ├── deduplication.py # TF-IDF cosine duplicate/cluster tespiti
│   │   ├── geocoding.py     # Demo koordinat üretimi
│   │   ├── urgency.py       # Kural tabanlı aciliyet motoru
│   │   └── ws_manager.py    # WebSocket bağlantı yöneticisi
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── data/
│   ├── generate_synthetic_data.py
│   ├── synthetic_calls.csv      # Komutla üretilir
│   └── classifier.pkl           # İlk eğitimde oluşur
├── tests/
├── Dockerfile
├── pytest.ini
└── requirements.txt
```

---

## Hızlı Başlangıç

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python -m data.generate_synthetic_data
uvicorn app.main:app --reload --port 8000
```

Adresler:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Başlangıçta Ne Olur?

Uygulama açılırken `lifespan` içinde şu adımlar çalışır:

1. SQLite tabloları oluşturulur.
2. `data/classifier.pkl` varsa sınıflandırıcı diskten yüklenir.
3. Model dosyası yoksa `data/synthetic_calls.csv` üzerinden yeniden eğitim yapılır.
4. Veritabanı boşsa sentetik CSV'den demo kayıtları seed edilir.

---

## Ortam Değişkenleri

| Değişken | Açıklama | Varsayılan |
|---|---|---|
| `AFET_DB_PATH` | SQLite dosya yolu | `backend/afet.db` |
| `CORS_ORIGINS` | Virgülle ayrılmış izinli frontend origin listesi | Lokal Vite originleri + Vercel regex |

Örnek:

```bash
CORS_ORIGINS=https://afet-koordinasyon-ai.vercel.app uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Sentetik Veri Üretimi

```bash
cd backend
python -m data.generate_synthetic_data
python -m data.generate_synthetic_data --n 500
```

Üretilen dosya:

```text
backend/data/synthetic_calls.csv
```

Sentetik veri:

- Tamamen yapaydır.
- Gerçek kişi, telefon veya açık adres içermez.
- Model eğitimi ve arayüz demosu için kullanılır.

---

## API Endpointleri

| Method | Path | Açıklama |
|---|---|---|
| GET | `/` | Servis adı, sürüm, demo uyarısı, docs ve WS yolu |
| GET | `/health` | Servis durumu, model durumu, accuracy, örnek sayısı, WS istemci sayısı |
| GET | `/api/calls` | Çağrı listesi ve filtreleme |
| GET | `/api/calls/{id}` | Tek çağrı detayı |
| POST | `/api/calls` | Yeni çağrı oluşturma; sınıflandırma, aciliyet skoru, dedup ve WS yayını çalışır |
| POST | `/api/analyze` | Çağrıyı veritabanına yazmadan analiz eder |
| GET | `/api/dashboard` | Dashboard istatistikleri |
| POST | `/api/retrain` | Sınıflandırıcıyı yeniden eğitir |
| WS | `/ws/calls` | Yeni çağrı canlı yayın akışı |

---

## Çağrı Oluşturma

```bash
curl -X POST http://localhost:8000/api/calls \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hatay Antakya'da enkaz altında 3 kişi var, sağlık ekibi ve vinç gerekiyor.",
    "city": "Hatay",
    "district": "Antakya",
    "people_count": 3
  }'
```

Özet işlem sırası:

1. Kategori manuel verilmediyse classifier tahmin yapar.
2. `compute_urgency()` aciliyet skorunu ve breakdown bilgisini üretir.
3. Koordinat yoksa demo geocoding çalışır.
4. Son 500 çağrıya karşı duplicate/cluster analizi yapılır.
5. Kayıt oluşturulur.
6. Yeni kayıt WebSocket istemcilerine yayınlanır.

---

## Kaydetmeden Analiz

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bebek ateşi çok yüksek, doktor ve ilaç gerekiyor.",
    "city": "Hatay",
    "district": "Defne",
    "people_count": 2
  }'
```

Bu endpoint şunları döndürür:

- Tahmini kategori.
- Kategori olasılıkları.
- Aciliyet skoru.
- Skor breakdown bilgisi.
- Yakalanan anahtar kelimeler.
- Benzer çağrı adayları.

Veritabanına kayıt yapmaz.

---

## Sınıflandırıcı

Servis: `app/services/classifier.py`

Model yaklaşımı:

```text
TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
+
LogisticRegression(max_iter=1000, C=2.0, class_weight="balanced")
```

Desteklenen kategoriler:

```text
enkaz, saglik, su, gida, barinma, ilac, ulasim, kayip_kisi, elektrik_isinma, diger
```

Model dosyası:

```text
backend/data/classifier.pkl
```

Yeniden eğitim:

```bash
curl -X POST http://localhost:8000/api/retrain
```

---

## Aciliyet Motoru

Servis: `app/services/urgency.py`

Skor formülü:

```text
skor = 20
     + min(40, eşleşen anahtar kelime puanları)
     + kategori ağırlığı
     + logaritmik kişi sayısı bonusu
```

Bantlar:

| Skor | Anlam |
|---:|---|
| 80-100 | Çok acil |
| 50-79 | Yüksek |
| 20-49 | Orta |
| 0-19 | Düşük |

Bu motor bilinçli olarak açıklanabilir tutulmuştur. `POST /api/analyze` cevabında her bileşen ayrı döner.

---

## Duplicate / Cluster Tespiti

Servis: `app/services/deduplication.py`

- Yeni çağrı, son 500 çağrı ile karşılaştırılır.
- Benzerlik için TF-IDF + cosine similarity kullanılır.
- `SIMILAR_THRESHOLD = 0.55`
- `DUPLICATE_THRESHOLD = 0.78`
- Aynı şehir/ilçe eşleşmesinde `LOCAL_BOOST = 0.08` kadar eşik düşürülür.
- Benzer çağrı varsa cluster paylaşılır; yoksa yeni cluster açılır.

---

## WebSocket

Endpoint:

```text
/ws/calls
```

Mesaj örnekleri:

```json
{ "type": "hello", "msg": "WebSocket bagli" }
```

```json
{ "type": "new_call", "call": { "id": 1, "text": "..." } }
```

```json
{ "type": "ping" }
```

```json
{ "type": "pong" }
```

Frontend, yeni çağrı geldiğinde dashboard ve harita verilerini güncellemek için bu akışı kullanır.

---

## Testler

```bash
cd backend
pytest
pytest -v
```

Test kapsamı:

- Aciliyet skoru.
- Sınıflandırıcı servisi.
- API endpointleri.
- Çağrı oluşturma ve analiz akışı.

---

## Docker

Backend image oluşturma:

```bash
cd backend
docker build -t afet-backend .
docker run --rm -p 8000:8000 afet-backend
```

Full-stack çalıştırma için kök dizinden:

```bash
docker compose up --build
```

---

## Render Dağıtımı

Kök dizindeki `render.yaml`, backend için Render Blueprint yapılandırması içerir.

Notlar:

- Free plan idle olduğunda uyuyabilir.
- Kalıcı disk yoksa SQLite ve `classifier.pkl` cold start sonrası yeniden oluşabilir.
- Demo için kabul edilebilir; üretim için Postgres, kalıcı disk ve gözlemleme önerilir.

---

## Üretime Taşıma İçin Eksikler

Bu backend üretim sistemi değildir. Üretim senaryosu için en azından şu başlıklar gerekir:

- Postgres veya benzeri kalıcı veritabanı.
- Kimlik doğrulama ve yetkilendirme.
- RBAC.
- Loglama ve monitoring.
- Rate limit.
- Audit log.
- Kişisel veri politikası.
- Gelişmiş veri doğrulama.
- Kuyruk sistemi: Celery/RQ/Redis.
- Vektör arama: pgvector, FAISS veya hnswlib.

---

## Güvenlik ve Sorumlu Kullanım

Bu backend gerçek afet koordinasyonu için kullanılamaz. Gerçek acil durumlarda 112 aranmalı ve resmi kurum duyuruları takip edilmelidir.
