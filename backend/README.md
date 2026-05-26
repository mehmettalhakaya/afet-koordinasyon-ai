# AfetKoordinasyonAI – Backend

FastAPI + SQLAlchemy + scikit-learn ile yazılmış REST API.

## Hızlı Başlangıç

```bash
cd backend

# 1. Sanal ortam ve bağımlılıklar
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt

# 2. Sentetik veri üret (modelin eğitilebilmesi için)
python -m data.generate_synthetic_data

# 3. API'yi başlat
uvicorn app.main:app --reload --port 8000
```

`http://localhost:8000/docs` adresinde otomatik Swagger UI hazır.

İlk istekte uygulama:
- Tabloları oluşturur (`afet.db`)
- Sınıflandırıcıyı eğitir (`data/classifier.pkl`)
- DB boşsa CSV'den seed çeker

## Testler

```bash
pytest
```

## API Endpoint Özeti

| Endpoint | Açıklama |
|---|---|
| `GET /` | Sağlık + uyarı bilgisi |
| `GET /health` | Sınıflandırıcı durumu |
| `GET /api/calls` | Liste + filtre (city, category, min_urgency, duplicate_suspected) |
| `POST /api/calls` | Yeni çağrı oluştur (sınıflandır + skor + dedup) |
| `GET /api/calls/{id}` | Tek çağrı |
| `POST /api/analyze` | Sadece analiz, kaydetmez |
| `GET /api/dashboard` | Panel istatistikleri |
| `POST /api/retrain` | Modeli yeniden eğit |

## Servis Katmanı

- `services/classifier.py` – TF-IDF + Logistic Regression pipeline, pickle cache
- `services/urgency.py` – Kural tabanlı 0-100 aciliyet skoru
- `services/deduplication.py` – TF-IDF cosine + şehir/ilçe yerel boost
- `services/geocoding.py` – Demo amaçlı yaklaşık koordinatlar
- `services/dashboard.py` – SQL agregasyonlu istatistikler

## Uyarı

Bu sistem GERÇEK acil durumlarda kullanılacak resmi koordinasyon sistemi
**değildir**. Eğitim, demo ve araştırma amaçlıdır. Acil durumda 112'yi
arayın, AFAD ve Kızılay gibi kurumları takip edin.
