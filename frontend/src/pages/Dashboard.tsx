import { useEffect, useState } from "react";
import { api } from "../services/api";
import { CATEGORY_LABELS, type DashboardStats } from "../types";
import { UrgencyBadge } from "../components/Badge";
import { Link } from "react-router-dom";
import { useCallStream } from "../services/useCallStream";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    api
      .dashboard()
      .then(setData)
      .catch((e) => setError(String(e)));
  };

  useEffect(load, []);

  // Yeni çağrı geldiğinde dashboard'u yenile
  const { connected } = useCallStream(() => {
    load();
  });

  if (error)
    return (
      <div>
        <div className="section-label">Panel</div>
        <h2>Panel</h2>
        <div className="disclaimer">Yüklenemedi: {error}</div>
      </div>
    );

  if (!data) return <div style={{ color: "var(--text-dim)" }}>Yükleniyor…</div>;

  const maxCat = Math.max(...data.category_distribution.map((c) => c.count), 1);
  const maxCity = Math.max(...data.city_distribution.map((c) => c.count), 1);

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 6 }}>
        <div>
          <div className="section-label">Genel Bakış</div>
          <h2>
            Operasyon <em>Paneli</em>
          </h2>
        </div>
        <span className={"live-pill " + (connected ? "live-on" : "live-off")} style={{ marginLeft: "auto" }}>
          {connected ? "● CANLI" : "○ KOPUK"}
        </span>
      </div>

      <div className="cards">
        <Card label="Toplam Çağrı" value={data.total_calls} />
        <Card label="Ortalama Aciliyet" value={data.avg_urgency} />
        <Card label="Şüpheli Tekrar" value={data.duplicate_suspected_count} />
        <Card label="Kategori Sayısı" value={data.category_distribution.length} />
      </div>

      <div className="section row">
        <div>
          <div className="section-label">Öncelik</div>
          <h2>En Acil Çağrılar</h2>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Kategori</th>
                <th>Şehir/İlçe</th>
                <th>Aciliyet</th>
              </tr>
            </thead>
            <tbody>
              {data.top_urgent_calls.slice(0, 8).map((c) => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{CATEGORY_LABELS[c.category]}</td>
                  <td>
                    {c.city}
                    {c.district ? ` / ${c.district}` : ""}
                  </td>
                  <td>
                    <UrgencyBadge score={c.urgency_score} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div>
          <div className="section-label">Akış</div>
          <h2>Son Eklenenler</h2>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Metin</th>
                <th>Kategori</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_calls.slice(0, 8).map((c) => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td title={c.text}>
                    {c.text.length > 60 ? c.text.slice(0, 57) + "…" : c.text}
                  </td>
                  <td>{CATEGORY_LABELS[c.category]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="section row">
        <div>
          <div className="section-label">Dağılım</div>
          <h2>Kategorilere Göre</h2>
          <table>
            <tbody>
              {data.category_distribution.map((c) => (
                <tr key={c.category}>
                  <td style={{ width: 160 }}>
                    {CATEGORY_LABELS[c.category as keyof typeof CATEGORY_LABELS] ||
                      c.category}
                  </td>
                  <td>
                    <div className="bar">
                      <span style={{ width: `${(c.count / maxCat) * 100}%` }} />
                    </div>
                  </td>
                  <td style={{ width: 50, textAlign: "right" }}>{c.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div>
          <div className="section-label">Coğrafya</div>
          <h2>Şehir Bazlı</h2>
          <table>
            <tbody>
              {data.city_distribution.map((c) => (
                <tr key={c.city}>
                  <td style={{ width: 160 }}>{c.city}</td>
                  <td>
                    <div className="bar">
                      <span style={{ width: `${(c.count / maxCity) * 100}%` }} />
                    </div>
                  </td>
                  <td style={{ width: 50, textAlign: "right" }}>{c.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="section">
        <Link to="/harita">→ Tümünü haritada gör</Link>
        {"   ·   "}
        <Link to="/yeni">→ Yeni çağrı ekle</Link>
      </div>
    </div>
  );
}

function Card({ label, value }: { label: string; value: number }) {
  return (
    <div className="card">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  );
}
