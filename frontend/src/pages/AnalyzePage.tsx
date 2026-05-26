import { useState } from "react";
import { api } from "../services/api";
import {
  type AnalyzeResponse,
  CATEGORY_LABELS,
  type Category,
} from "../types";
import { UrgencyBadge } from "../components/Badge";

export default function AnalyzePage() {
  const [text, setText] = useState(
    "Hatay Antakya'da enkaz altında 4 kişi var, sağlık ekibi ve vinç acil."
  );
  const [city, setCity] = useState("Hatay");
  const [district, setDistrict] = useState("Antakya");
  const [people, setPeople] = useState(4);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.analyze({
        text,
        city: city || undefined,
        district: district || undefined,
        people_count: people,
      });
      setResult(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="section-label">Hızlı Test</div>
      <h2>
        Analiz <em>Demo</em>
      </h2>
      <p style={{ color: "var(--text-dim)", marginTop: 0, marginBottom: 18, fontSize: 13 }}>
        Metni veritabanına yazmadan sınıflandır, aciliyet skorunu hesapla, benzer çağrıları getir.
      </p>

      <div className="form-grid">
        <label className="full">
          Metin
          <textarea
            rows={4}
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </label>
        <label>
          Şehir
          <input value={city} onChange={(e) => setCity(e.target.value)} />
        </label>
        <label>
          İlçe
          <input value={district} onChange={(e) => setDistrict(e.target.value)} />
        </label>
        <label>
          Kişi Sayısı
          <input
            type="number"
            min={1}
            value={people}
            onChange={(e) => setPeople(Number(e.target.value))}
          />
        </label>
        <div style={{ alignSelf: "end" }}>
          <button onClick={run} disabled={loading || text.length < 3}>
            {loading ? "Analiz ediliyor…" : "Analiz Et →"}
          </button>
        </div>
      </div>

      {error && <div className="disclaimer" style={{ marginTop: 18 }}>{error}</div>}

      {result && (
        <div className="section">
          <div className="row">
            <div className="card">
              <div className="label">Tahmini Kategori</div>
              <div className="value" style={{ fontFamily: "'Instrument Serif', serif" }}>
                {CATEGORY_LABELS[result.predicted_category as Category] ??
                  result.predicted_category}
              </div>
              <div style={{ marginTop: 10 }}>
                <UrgencyBadge score={result.urgency_score} />
              </div>
            </div>
            <div className="card">
              <div className="label">Aciliyet Skoru Dağılımı</div>
              <ul style={{ paddingLeft: 16, margin: "10px 0", color: "var(--text-dim)", fontSize: 14, lineHeight: 1.9 }}>
                <li>Taban: {result.urgency_breakdown.base}</li>
                <li>Anahtar kelimeler: {result.urgency_breakdown.keyword_score}</li>
                <li>Kategori ağırlığı: {result.urgency_breakdown.category_weight}</li>
                <li>Kişi sayısı bonusu: {result.urgency_breakdown.people_bonus}</li>
                <li style={{ color: "var(--accent)", fontWeight: 700 }}>
                  Toplam: {result.urgency_breakdown.total}
                </li>
              </ul>
            </div>
          </div>

          <div className="section">
            <div className="section-label">NLP</div>
            <h2>Anahtar Kelimeler</h2>
            {result.extracted_keywords.length === 0 ? (
              <span style={{ color: "var(--text-dim)" }}>Belirgin anahtar kelime yok.</span>
            ) : (
              result.extracted_keywords.map((k) => (
                <span key={k} className="kw">
                  {k}
                </span>
              ))
            )}
          </div>

          <div className="section">
            <div className="section-label">Model</div>
            <h2>Kategori Olasılıkları</h2>
            <table>
              <tbody>
                {Object.entries(result.category_scores)
                  .sort((a, b) => b[1] - a[1])
                  .map(([cat, p]) => (
                    <tr key={cat}>
                      <td style={{ width: 160 }}>
                        {CATEGORY_LABELS[cat as Category] ?? cat}
                      </td>
                      <td>
                        <div className="bar">
                          <span style={{ width: `${p * 100}%` }} />
                        </div>
                      </td>
                      <td style={{ width: 60, textAlign: "right" }}>
                        {(p * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {result.duplicate_candidates.length > 0 && (
            <div className="section">
              <div className="section-label">Dedup</div>
              <h2>Benzer Çağrılar</h2>
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Şehir/İlçe</th>
                    <th>Aciliyet</th>
                    <th>Metin</th>
                  </tr>
                </thead>
                <tbody>
                  {result.duplicate_candidates.map((c) => (
                    <tr key={c.id}>
                      <td>{c.id}</td>
                      <td>
                        {c.city}
                        {c.district ? ` / ${c.district}` : ""}
                      </td>
                      <td>
                        <UrgencyBadge score={c.urgency_score} />
                      </td>
                      <td>
                        {c.text.length > 80 ? c.text.slice(0, 77) + "…" : c.text}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
