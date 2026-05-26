import { useEffect, useMemo, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import L from "leaflet";
import { api } from "../services/api";
import { useCallStream } from "../services/useCallStream";
import { CATEGORY_LABELS, type HelpCall, urgencyColor } from "../types";
import { UrgencyBadge } from "../components/Badge";
import HeatmapLayer from "../components/HeatmapLayer";

const TURKEY_CENTER: [number, number] = [38.5, 36.5];

type ViewMode = "markers" | "heatmap" | "both";

function urgencyDivIcon(score: number): L.DivIcon {
  const color = urgencyColor(score);
  const size = 14 + Math.round(score / 8);
  return L.divIcon({
    className: "afet-marker",
    html: `<div style="
      width:${size}px;height:${size}px;border-radius:50%;
      background:${color};border:2px solid #0a0a0b;
      box-shadow:0 0 0 1px ${color}, 0 2px 8px rgba(0,0,0,0.6);
      "></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
}

export default function MapPage() {
  const [calls, setCalls] = useState<HelpCall[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<ViewMode>("markers");

  useEffect(() => {
    api
      .listCalls()
      .then(setCalls)
      .catch((e) => setError(String(e)));
  }, []);

  const { connected } = useCallStream((newCall) => {
    setCalls((prev) => {
      const idx = prev.findIndex((c) => c.id === newCall.id);
      if (idx >= 0) {
        const copy = [...prev];
        copy[idx] = newCall;
        return copy;
      }
      return [newCall, ...prev];
    });
  });

  const positioned = useMemo(
    () => calls.filter((c) => c.lat != null && c.lon != null),
    [calls]
  );

  const heatPoints = useMemo(
    () =>
      positioned.map(
        (c) =>
          [c.lat as number, c.lon as number, c.urgency_score / 100] as [
            number,
            number,
            number
          ]
      ),
    [positioned]
  );

  if (error) return <div className="disclaimer">Harita yüklenemedi: {error}</div>;

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap", marginBottom: 6 }}>
        <div>
          <div className="section-label">Coğrafi Görünüm</div>
          <h2>
            <em>Harita</em>
          </h2>
        </div>

        <span className={"live-pill " + (connected ? "live-on" : "live-off")}>
          {connected ? "● CANLI" : "○ KOPUK"}
        </span>

        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          {(["markers", "heatmap", "both"] as ViewMode[]).map((m) => (
            <button
              key={m}
              onClick={() => setView(m)}
              style={
                view === m
                  ? {}
                  : {
                      background: "transparent",
                      color: "var(--text-dim)",
                      border: "1px solid var(--border)",
                    }
              }
            >
              {m === "markers" ? "Marker" : m === "heatmap" ? "Heatmap" : "İkisi"}
            </button>
          ))}
        </div>
      </div>

      <p style={{ color: "var(--text-dim)", marginTop: 0, marginBottom: 14, fontSize: 13 }}>
        Yakın marker'lar otomatik kümelenir · Yeni çağrı eklenince anlık güncellenir · Konumlar demo amaçlı yaklaşık koordinatlardır.
      </p>

      <div className="map-wrap">
        <MapContainer
          center={TURKEY_CENTER}
          zoom={6}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {(view === "heatmap" || view === "both") && heatPoints.length > 0 && (
            <HeatmapLayer points={heatPoints} />
          )}

          {(view === "markers" || view === "both") && (
            <MarkerClusterGroup
              chunkedLoading
              showCoverageOnHover={false}
              spiderfyOnMaxZoom
              maxClusterRadius={50}
            >
              {positioned.map((c) => (
                <Marker
                  key={c.id}
                  position={[c.lat as number, c.lon as number]}
                  icon={urgencyDivIcon(c.urgency_score)}
                >
                  <Popup>
                    <div style={{ minWidth: 220, fontSize: 13 }}>
                      <strong>#{c.id} · {CATEGORY_LABELS[c.category]}</strong>
                      <div style={{ margin: "8px 0" }}>
                        <UrgencyBadge score={c.urgency_score} />
                      </div>
                      <div>
                        <b>Şehir/İlçe:</b> {c.city}
                        {c.district ? ` / ${c.district}` : ""}
                      </div>
                      <div style={{ marginTop: 4 }}>
                        {c.text.length > 140 ? c.text.slice(0, 137) + "…" : c.text}
                      </div>
                      <div style={{ marginTop: 4, color: "var(--text-dim)", fontSize: 12 }}>
                        Kişi: {c.people_count} · Benzer: {c.similar_count}
                        {c.duplicate_suspected ? " · ⚠ tekrar şüphesi" : ""}
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MarkerClusterGroup>
          )}
        </MapContainer>
      </div>

      <p style={{ color: "var(--text-dim)", fontSize: 12, marginTop: 10 }}>
        Toplam {calls.length} çağrı yüklendi · {positioned.length} koordinatlı.
      </p>
    </div>
  );
}
