# Deploy Rehberi — Vercel + Render

> Projeyi sıfırdan canlıya çıkarmak için adım adım kılavuz.
> Tahmini süre: **20-30 dakika**, ücret: **$0** (her iki servisin free tier'ı).

## Mimari

```
İnternet
   │
   ▼
┌──────────────┐    HTTPS    ┌─────────────────────┐
│   Vercel     │◀───────────▶│  Render             │
│              │             │                     │
│ Vite + React │   /api/*    │ FastAPI + sklearn   │
│ Static CDN   │   /ws/*     │ + SQLite + .pkl     │
│              │             │ + Persistent Disk   │
└──────────────┘             └─────────────────────┘
       │                            │
       └── kullanıcı browser ───────┘
```

- **Frontend:** Vercel — statik build, anlık CDN, push'a otomatik deploy.
- **Backend:** Render — Python web servisi, WebSocket destekli, 1GB persistent disk SQLite + model pickle için.

---

## Ön hazırlık

1. **GitHub repo** oluştur ve projeyi pushla:

   ```powershell
   cd $HOME\Desktop\afet-koordinasyon-ai
   git init
   git add .
   git commit -m "Initial commit"
   # github.com/new'de elle oluştur, sonra:
   git remote add origin https://github.com/<kullanici>/afet-koordinasyon-ai.git
   git branch -M main
   git push -u origin main
   ```

2. Hesap aç (her ikisi de GitHub ile giriş kabul ediyor, ekstra kayıt yok):
   - <https://render.com>
   - <https://vercel.com>

---

## 1. Backend → Render

### a. Blueprint'ten kur

1. Render dashboard'da **"New +" → "Blueprint"** seç.
2. GitHub repo'nu bağla → repo'yu seç.
3. Render `render.yaml` dosyasını otomatik bulur, **"Apply"**'a bas.
4. Service ismi: `afet-koordinasyon-ai-backend` (otomatik).
5. **Disk** oluşturulur (1GB free).

### b. İlk build

İlk build 5-8 dakika sürer (numpy/scikit-learn indirme + sentetik veri üretme).
Logda şu satırı görmen lazım:

```
INFO Sınıflandırıcı eğitildi (acc=0.85x, n=240)
Application startup complete.
```

### c. URL'i not et

Service üst kısmında URL: `https://afet-koordinasyon-ai-backend.onrender.com` (veya benzeri).
Bunu **kopyala**, frontend için lazım.

Test et:

```
https://<senin-url>.onrender.com/        → JSON çıkar (ilk istek ~30 sn cold start)
https://<senin-url>.onrender.com/docs    → Swagger UI
https://<senin-url>.onrender.com/health  → {"status":"ok",...}
```

### d. CORS env var (Vercel deploy'undan sonra)

Vercel URL'ini bulduktan sonra, Render service → **Environment** → `CORS_ORIGINS`'e
`https://<vercel-projen>.vercel.app` ekle.

(`.vercel.app` subdomain'leri zaten regex'le otomatik kabul ediliyor; bu adımı atlasan da çalışır.)

---

## 2. Frontend → Vercel

### a. Backend URL'ini ayarla

`frontend/vercel.json`'u aç, **AFET-BACKEND-URL** placeholder'ını gerçek Render URL'inle değiştir:

```json
"rewrites": [
  { "source": "/api/(.*)", "destination": "https://afet-koordinasyon-ai-backend.onrender.com/api/$1" },
  { "source": "/health",   "destination": "https://afet-koordinasyon-ai-backend.onrender.com/health" }
]
```

Commit + push.

### b. Vercel'de import et

1. Vercel dashboard → **"Add New… > Project"**.
2. GitHub repo'nu seç.
3. **Root Directory:** `frontend`
4. **Framework Preset:** Vite (otomatik bulur)
5. **Environment Variables** (önemli, WebSocket için):
   - `VITE_WS_BASE` = `wss://afet-koordinasyon-ai-backend.onrender.com/ws/calls`
   - (`/api` için env'e gerek yok — `vercel.json` rewrite'ı halleder)
6. **"Deploy"** bas. ~1 dakika.

### c. Test et

URL'in `https://<proje-adi>.vercel.app`. Aç:

- `/dashboard` → kartlar yüklenmeli, **● CANLI** rozeti yeşil olmalı.
- `/harita` → marker'lar gözükmeli, cluster çalışmalı.
- `/analiz` → form çalışmalı, sınıflandırma + breakdown dönmeli.
- `/yeni` → çağrı oluştur, **diğer sekmedeki dashboard otomatik güncellenmeli** (WS testi).

---

## 3. CI rozeti (opsiyonel)

`README.md`'nin başına ekle:

```markdown
![CI](https://github.com/<kullanıcı>/afet-koordinasyon-ai/actions/workflows/ci.yml/badge.svg)
[![Demo](https://img.shields.io/badge/demo-vercel-c9f06b)](https://<proje-adi>.vercel.app)
```

GitHub Actions zaten `.github/workflows/ci.yml`'de hazır; ilk push'ta otomatik koşar.

---

## Sorun giderme

### Render cold start çok yavaş (~30 sn)

Free tier 15 dk idle sonra uyur. Çözümler:

- **UptimeRobot** (ücretsiz) ile 14 dk'da bir `/health` ping at, uyutma.
- **Render Starter plan** ($7/ay, hep uyanık).
- Frontend'e "ısınıyor, lütfen bekleyin..." mesajı eklenebilir.

### "CORS error" konsola düşüyor

Render → Environment → `CORS_ORIGINS=https://<vercel-domain>.vercel.app` ekle, redeploy.
Veya backend zaten `*.vercel.app` regex ile kabul ediyor — Vercel URL'ini kontrol et.

### WebSocket bağlanmıyor (`● CANLI` kırmızı kalıyor)

- Vercel env'de `VITE_WS_BASE` doğru ayarlı mı? `wss://...` (ws değil) olmalı.
- Render service'in URL'i HTTPS olmalı; otomatik öyle.
- Browser console'da `WebSocket connection failed` görürsen URL'i kontrol et.

### Veri kalıcı değil

Render free tier disk düşmemiş olmalı. Service → Settings → Disks → mount path `/var/data` var mı?
Yoksa Blueprint'i tekrar uygula.

---

## Maliyet özeti

| Servis | Plan | Aylık | Limit |
|---|---|---|---|
| Vercel Hobby | Free | $0 | 100GB bandwidth, sınırsız deploy |
| Render Free | Free | $0 | 750 saat web service, 1GB disk, 15dk idle uyku |
| **Toplam** | | **$0** | Demo için fazlasıyla yeter |

Render uyumasını istemezsen → Starter $7/ay. Bütçe yoksa UptimeRobot ile uyutmama yeterli.
