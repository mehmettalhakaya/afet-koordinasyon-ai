# AfetKoordinasyonAI – Frontend

React + Vite + TypeScript + Leaflet ile yazılmış demo arayüz.

## Hızlı Başlangıç

Önce backend `http://localhost:8000`'de çalışıyor olmalı.

```bash
cd frontend
npm install
npm run dev
```

Tarayıcı: `http://localhost:5173`

Dev sunucusu `/api` ve `/health` isteklerini backend'e proxy'ler
(`vite.config.ts`). Üretimde başka bir host kullanmak için
`VITE_API_BASE` ortam değişkenini kullanın:

```bash
VITE_API_BASE=https://api.example.com npm run build
```

## Sayfalar

- **/dashboard** – Toplam çağrı, en aciller, kategori ve şehir dağılımı
- **/harita** – Leaflet ile aciliyet rengine göre marker'lar
- **/cagrilar** – Filtreli çağrı listesi
- **/yeni** – Yeni çağrı formu (gerçek kişisel bilgi girme)
- **/analiz** – Veritabanına yazmadan canlı analiz demosu

## Yapı

```
src/
  components/Layout.tsx, Badge.tsx
  pages/Dashboard.tsx, MapPage.tsx, CallsPage.tsx, NewCallPage.tsx, AnalyzePage.tsx
  services/api.ts      # fetch tabanlı REST istemcisi
  types/index.ts       # API tipleri ve yardımcılar
```
