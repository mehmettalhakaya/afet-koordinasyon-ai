import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { CATEGORY_LABELS, type HelpCall } from "../types";
import { UrgencyBadge } from "../components/Badge";

// Türkiye'nin 81 ili, alfabetik.
const CITIES = [
  "Adana",
  "Adıyaman",
  "Afyonkarahisar",
  "Ağrı",
  "Aksaray",
  "Amasya",
  "Ankara",
  "Antalya",
  "Ardahan",
  "Artvin",
  "Aydın",
  "Balıkesir",
  "Bartın",
  "Batman",
  "Bayburt",
  "Bilecik",
  "Bingöl",
  "Bitlis",
  "Bolu",
  "Burdur",
  "Bursa",
  "Çanakkale",
  "Çankırı",
  "Çorum",
  "Denizli",
  "Diyarbakır",
  "Düzce",
  "Edirne",
  "Elazığ",
  "Erzincan",
  "Erzurum",
  "Eskişehir",
  "Gaziantep",
  "Giresun",
  "Gümüşhane",
  "Hakkari",
  "Hatay",
  "Iğdır",
  "Isparta",
  "İstanbul",
  "İzmir",
  "Kahramanmaraş",
  "Karabük",
  "Karaman",
  "Kars",
  "Kastamonu",
  "Kayseri",
  "Kilis",
  "Kırıkkale",
  "Kırklareli",
  "Kırşehir",
  "Kocaeli",
  "Konya",
  "Kütahya",
  "Malatya",
  "Manisa",
  "Mardin",
  "Mersin",
  "Muğla",
  "Muş",
  "Nevşehir",
  "Niğde",
  "Ordu",
  "Osmaniye",
  "Rize",
  "Sakarya",
  "Samsun",
  "Şanlıurfa",
  "Siirt",
  "Sinop",
  "Sivas",
  "Şırnak",
  "Tekirdağ",
  "Tokat",
  "Trabzon",
  "Tunceli",
  "Uşak",
  "Van",
  "Yalova",
  "Yozgat",
  "Zonguldak",
];

export default function NewCallPage() {
  const navigate = useNavigate();
  const [text, setText] = useState("");
  const [city, setCity] = useState("Hatay");
  const [district, setDistrict] = useState("");
  const [addressNote, setAddressNote] = useState("");
  const [peopleCount, setPeopleCount] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [created, setCreated] = useState<HelpCall | null>(null);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.createCall({
        text,
        city,
        district: district || undefined,
        address_note: addressNote || undefined,
        people_count: peopleCount,
      });
      setCreated(res);
      setText("");
      setDistrict("");
      setAddressNote("");
      setPeopleCount(1);
    } catch (err) {
      setError(String(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="section-label">Yeni Kayıt</div>
      <h2>
        <em>Çağrı</em> Oluştur
      </h2>
      <p style={{ color: "var(--text-dim)", marginTop: 0, marginBottom: 18, fontSize: 13 }}>
        Demo amaçlı çağrı oluştur. Telefon ve gerçek kimlik bilgisi girme.
      </p>

      <form onSubmit={submit} className="form-grid">
        <label className="full">
          Çağrı Metni
          <textarea
            rows={4}
            value={text}
            required
            minLength={3}
            placeholder="Örn: Hatay Antakya'da enkaz altında 3 kişi var, vinç ve sağlık ekibi gerekiyor."
            onChange={(e) => setText(e.target.value)}
          />
        </label>

        <label>
          Şehir
          <select value={city} onChange={(e) => setCity(e.target.value)}>
            {CITIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>

        <label>
          İlçe (opsiyonel)
          <input
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            placeholder="örn: Antakya"
          />
        </label>

        <label className="full">
          Adres Notu (opsiyonel — gerçek adres girme)
          <input
            value={addressNote}
            onChange={(e) => setAddressNote(e.target.value)}
            placeholder="Mahalle açıklaması (demo)"
          />
        </label>

        <label>
          Etkilenen Kişi Sayısı
          <input
            type="number"
            min={1}
            value={peopleCount}
            onChange={(e) => setPeopleCount(Number(e.target.value))}
          />
        </label>

        <div style={{ alignSelf: "end" }}>
          <button type="submit" disabled={submitting || text.length < 3}>
            {submitting ? "Gönderiliyor…" : "Çağrı Oluştur →"}
          </button>
        </div>
      </form>

      {error && (
        <div className="disclaimer" style={{ marginTop: 18 }}>
          Hata: {error}
        </div>
      )}

      {created && (
        <div className="card" style={{ marginTop: 24, maxWidth: 760 }}>
          <div className="label">Oluşturuldu · #{created.id}</div>
          <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <UrgencyBadge score={created.urgency_score} />
            <span style={{ color: "var(--text-dim)", fontSize: 13 }}>
              <strong style={{ color: "var(--text)" }}>Kategori:</strong> {CATEGORY_LABELS[created.category]}
            </span>
          </div>
          <div style={{ marginTop: 8, color: "var(--text-dim)", fontSize: 12 }}>
            Cluster: {created.cluster_id ?? "-"} · Benzer: {created.similar_count}
            {created.duplicate_suspected ? " · ⚠ tekrar şüphesi" : ""}
          </div>
          <button style={{ marginTop: 14 }} onClick={() => navigate("/harita")}>
            Haritada Gör →
          </button>
        </div>
      )}
    </div>
  );
}
