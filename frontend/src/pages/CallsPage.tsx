import { useEffect, useMemo, useState } from "react";
import { api } from "../services/api";
import {
  CATEGORY_LABELS,
  type Category,
  type HelpCall,
} from "../types";
import { UrgencyBadge } from "../components/Badge";

const CATS: { value: Category | ""; label: string }[] = [
  { value: "", label: "Hepsi" },
  ...(Object.entries(CATEGORY_LABELS) as [Category, string][]).map(([v, l]) => ({
    value: v,
    label: l,
  })),
];

export default function CallsPage() {
  const [calls, setCalls] = useState<HelpCall[]>([]);
  const [city, setCity] = useState("");
  const [category, setCategory] = useState<Category | "">("");
  const [minUrgency, setMinUrgency] = useState<number | "">("");
  const [dupOnly, setDupOnly] = useState(false);
  const [loading, setLoading] = useState(false);

  const load = () => {
    setLoading(true);
    api
      .listCalls({
        city: city || undefined,
        category: category || undefined,
        min_urgency: minUrgency === "" ? undefined : Number(minUrgency),
        duplicate_suspected: dupOnly ? true : undefined,
      })
      .then(setCalls)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const totalUrg = useMemo(
    () =>
      calls.length === 0
        ? 0
        : Math.round(
            calls.reduce((s, c) => s + c.urgency_score, 0) / calls.length
          ),
    [calls]
  );

  return (
    <div>
      <div className="section-label">Liste</div>
      <h2>
        <em>Çağrılar</em>
      </h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: 10,
          margin: "14px 0",
        }}
      >
        <input
          placeholder="Şehir (örn: Hatay)"
          value={city}
          onChange={(e) => setCity(e.target.value)}
        />
        <select value={category} onChange={(e) => setCategory(e.target.value as Category)}>
          {CATS.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
        <input
          type="number"
          min={0}
          max={100}
          placeholder="Min aciliyet"
          value={minUrgency}
          onChange={(e) =>
            setMinUrgency(e.target.value === "" ? "" : Number(e.target.value))
          }
        />
        <label
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: "var(--bg2)",
            padding: "0 14px",
            borderRadius: "var(--radius)",
            border: "1px solid var(--border)",
            fontSize: 12,
            color: "var(--text-dim)",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            fontWeight: 600,
          }}
        >
          <input
            type="checkbox"
            checked={dupOnly}
            style={{ width: "auto", accentColor: "var(--accent)" }}
            onChange={(e) => setDupOnly(e.target.checked)}
          />
          Tekrar şüphesi
        </label>
        <button onClick={load} disabled={loading}>
          {loading ? "Yükleniyor…" : "Filtrele →"}
        </button>
      </div>

      <p style={{ color: "var(--text-dim)", fontSize: 12, marginBottom: 10 }}>
        {calls.length} sonuç · ort. aciliyet {totalUrg}
      </p>

      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Kategori</th>
            <th>Şehir/İlçe</th>
            <th>Kişi</th>
            <th>Aciliyet</th>
            <th>Cluster</th>
            <th>Metin</th>
          </tr>
        </thead>
        <tbody>
          {calls.map((c) => (
            <tr key={c.id}>
              <td>{c.id}</td>
              <td>{CATEGORY_LABELS[c.category]}</td>
              <td>
                {c.city}
                {c.district ? ` / ${c.district}` : ""}
              </td>
              <td>{c.people_count}</td>
              <td>
                <UrgencyBadge score={c.urgency_score} />
              </td>
              <td>
                {c.cluster_id ?? "-"}
                {c.duplicate_suspected ? <span className="dup"> ⚠</span> : null}
              </td>
              <td title={c.text}>
                {c.text.length > 80 ? c.text.slice(0, 77) + "…" : c.text}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
