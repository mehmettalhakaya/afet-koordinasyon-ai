// leaflet.heat tabanlı ısı haritası katmanı.
// react-leaflet doğrudan desteklemediği için useMap ile manuel ekliyoruz.
import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet.heat";

interface Props {
  // [lat, lon, intensity (0-1)] üçlüleri
  points: Array<[number, number, number]>;
  radius?: number;
  blur?: number;
}

export default function HeatmapLayer({ points, radius = 28, blur = 18 }: Props) {
  const map = useMap();

  useEffect(() => {
    // leaflet.heat global L üzerine heatLayer ekler; tip dosyası yok
    const layer = (L as any).heatLayer(points, {
      radius,
      blur,
      maxZoom: 12,
      max: 1.0,
      gradient: {
        0.2: "#94a3b8",
        0.4: "#facc15",
        0.7: "#ef4444",
        1.0: "#b91c1c",
      },
    });
    layer.addTo(map);
    return () => {
      layer.remove();
    };
  }, [map, points, radius, blur]);

  return null;
}
