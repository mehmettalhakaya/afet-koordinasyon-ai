# AfetKoordinasyonAI – Frontend

Bu klasör, AfetKoordinasyonAI projesinin React + Vite + TypeScript tabanlı kullanıcı arayüzüdür. Arayüz; operasyon paneli, çağrı listesi, yeni çağrı formu, analiz demosu ve harita görünümünden oluşur.

> Canlı demo: https://afet-koordinasyon-ai.vercel.app/

---

## Teknoloji Yığını

- React 18
- TypeScript
- Vite
- React Router
- React Leaflet
- Leaflet
- react-leaflet-cluster
- leaflet.heat
- Fetch API
- WebSocket

---

## Hızlı Başlangıç

Backend'in `http://localhost:8000` adresinde çalıştığından emin olun.

```bash
cd frontend
npm install
npm run dev
```

Tarayıcı:

```text
http://localhost:5173
```

Vite geliştirme sunucusu şu yolları backend'e proxy'ler:

- `/api` → `http://localhost:8000`
- `/health` → `http://localhost:8000`
- `/ws` → `ws://localhost:8000`

---

## Komutlar

| Komut | Açıklama |
|---|---|
| `npm run dev` | Geliştirme sunucusunu başlatır |
| `npm run build` | Production build üretir |
| `npm run build:strict` | TypeScript build + Vite build çalıştırır |
| `npm run preview` | Build çıktısını lokal önizler |
| `npm run lint` | TypeScript kontrolü yapar |

---

## Sayfalar

| Route | Açıklama |
|---|---|
| `/dashboard` | Operasyon paneli; toplam çağrı, ortalama aciliyet, en acil çağrılar, son çağrılar, kategori ve şehir dağılımları |
| `/harita` | Leaflet haritası; marker, heatmap ve ikili görünüm |
| `/cagrilar` | Çağrı listesi; şehir, kategori, minimum aciliyet ve tekrar şüphesi filtresi |
| `/yeni` | Demo çağrı oluşturma formu |
| `/analiz` | Veritabanına yazmadan sınıflandırma, aciliyet ve benzerlik analizi |

Kök route `/dashboard` sayfasına yönlendirilir.

---

## Klasör Yapısı

```text
frontend/
├── src/
│   ├── components/
│   │   ├── Badge.tsx          # Aciliyet rozeti
│   │   ├── HeatmapLayer.tsx   # Leaflet heatmap katmanı
│   │   └── Layout.tsx         # Ana sayfa düzeni ve navigasyon
│   ├── pages/
│   │   ├── AnalyzePage.tsx    # Kaydetmeden analiz demosu
│   │   ├── CallsPage.tsx      # Filtreli çağrı listesi
│   │   ├── Dashboard.tsx      # Operasyon paneli
│   │   ├── MapPage.tsx        # Harita, marker cluster, heatmap
│   │   └── NewCallPage.tsx    # Yeni çağrı formu
│   ├── services/
│   │   ├── api.ts             # Fetch tabanlı REST istemcisi
│   │   └── useCallStream.ts   # WebSocket hook'u
│   ├── types/
│   │   └── index.ts           # API tipleri, kategori label'ları, aciliyet yardımcıları
│   ├── App.tsx
│   └── main.tsx
├── vercel.json
├── vite.config.ts
├── Dockerfile
└── package.json
```

---

## API Bağlantısı

REST istemcisi `src/services/api.ts` içinde tanımlıdır.

Varsayılan davranış:

```ts
const BASE = import.meta.env.VITE_API_BASE ?? "";
```

Lokal geliştirmede `BASE` boş kalır ve Vite proxy devreye girer.

Production build için ayrı API host'u kullanılacaksa:

```bash
VITE_API_BASE=https://api.example.com npm run build
```

Mevcut Vercel yapılandırmasında `/api/*` ve `/health` istekleri Render backend servisine rewrite edilir.

---

## WebSocket Akışı

Hook:

```text
src/services/useCallStream.ts
```

Bağlantı yolu:

```text
/ws/calls
```

Özellikler:

- `new_call` mesajlarını dinler.
- Bağlantı durumunu `connected` olarak döndürür.
- 25 saniyede bir ping gönderir.
- Bağlantı koparsa 2 saniye sonra yeniden bağlanmayı dener.

Kullanıldığı yerler:

- Dashboard: Yeni çağrı geldiğinde istatistikleri yeniden yükler.
- Harita: Yeni çağrıyı mevcut listeye ekler.

Production dağıtımda WebSocket proxy/host davranışı ayrıca test edilmelidir. Gerekirse REST API base URL'den ayrı bir `VITE_WS_BASE` benzeri ortam değişkeni eklenebilir.

---

## Harita Görünümü

Sayfa:

```text
src/pages/MapPage.tsx
```

Özellikler:

- Türkiye merkezli Leaflet haritası.
- Aciliyet skoruna göre marker boyutu ve rengi.
- Marker cluster görünümü.
- Heatmap görünümü.
- Marker + heatmap birlikte gösterim modu.
- Popup içinde kategori, şehir/ilçe, metin, kişi sayısı, cluster ve tekrar şüphesi bilgileri.

Konumlar demo amaçlı yaklaşık koordinatlardır.

---

## Dashboard

Sayfa:

```text
src/pages/Dashboard.tsx
```

Gösterilen veriler:

- Toplam çağrı.
- Ortalama aciliyet.
- Tekrar şüphesi sayısı.
- En acil çağrılar.
- Son eklenen çağrılar.
- Kategori dağılımı.
- Şehir dağılımı.

Veri kaynağı:

```text
GET /api/dashboard
```

---

## Çağrı Listesi

Sayfa:

```text
src/pages/CallsPage.tsx
```

Filtreler:

- Şehir.
- Kategori.
- Minimum aciliyet.
- Sadece tekrar şüphesi olan çağrılar.

Veri kaynağı:

```text
GET /api/calls
```

---

## Yeni Çağrı Formu

Sayfa:

```text
src/pages/NewCallPage.tsx
```

Alanlar:

- Çağrı metni.
- Şehir.
- İlçe.
- Demo adres notu.
- Etkilenen kişi sayısı.
- Opsiyonel kategori override.

Form gönderildiğinde:

```text
POST /api/calls
```

Backend sınıflandırma, aciliyet skoru, koordinat üretimi, duplicate/cluster analizi ve WebSocket yayını yapar.

---

## Analiz Demo

Sayfa:

```text
src/pages/AnalyzePage.tsx
```

Bu ekran çağrıyı veritabanına yazmadan analiz eder.

Döndürdüğü bilgiler:

- Tahmini kategori.
- Aciliyet skoru.
- Skor bileşenleri.
- Yakalanan anahtar kelimeler.
- Kategori olasılıkları.
- Benzer çağrı adayları.

Veri kaynağı:

```text
POST /api/analyze
```

---

## Vercel Dağıtımı

`frontend/vercel.json` Vercel için yapılandırılmıştır:

- Framework: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Install command: `npm install`
- `/api/*` rewrite: Render backend API
- `/health` rewrite: Render backend health endpoint

Dağıtım için tipik akış:

1. Vercel'de proje kök dizini olarak `frontend` seçilir.
2. Build command `npm run build` olur.
3. Output directory `dist` olur.
4. Backend URL'i rewrite veya ortam değişkeni ile tanımlanır.

---

## Docker

Frontend image oluşturma:

```bash
cd frontend
docker build -t afet-frontend .
docker run --rm -p 5173:80 afet-frontend
```

Full-stack için kök dizinden:

```bash
docker compose up --build
```

---

## Sorumlu Kullanım

Arayüzde gerçek kimlik, telefon veya açık adres girilmemelidir. Bu proje yalnızca eğitim, demo ve portföy amacıyla kullanılmalıdır. Gerçek acil durumda 112 aranmalı ve resmi kurum duyuruları takip edilmelidir.
