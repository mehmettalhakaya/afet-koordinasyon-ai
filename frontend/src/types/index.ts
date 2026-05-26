// API tipleri (backend pydantic şemalarıyla eşleşir)

export type Category =
  | "enkaz"
  | "saglik"
  | "su"
  | "gida"
  | "barinma"
  | "ilac"
  | "ulasim"
  | "kayip_kisi"
  | "elektrik_isinma"
  | "diger";

export interface HelpCall {
  id: number;
  text: string;
  city: string;
  district: string | null;
  address_note: string | null;
  people_count: number;
  phone: string | null;
  lat: number | null;
  lon: number | null;
  category: Category;
  urgency_score: number;
  cluster_id: number | null;
  duplicate_suspected: boolean;
  similar_count: number;
  created_at: string;
}

export interface HelpCallCreate {
  text: string;
  city: string;
  district?: string;
  address_note?: string;
  people_count: number;
  phone?: string;
  lat?: number;
  lon?: number;
}

export interface AnalyzeResponse {
  predicted_category: Category;
  category_scores: Record<string, number>;
  urgency_score: number;
  urgency_breakdown: {
    base: number;
    keyword_score: number;
    category_weight: number;
    people_bonus: number;
    matched_keywords: string[];
    total: number;
  };
  extracted_keywords: string[];
  duplicate_candidates: HelpCall[];
}

export interface DashboardStats {
  total_calls: number;
  avg_urgency: number;
  duplicate_suspected_count: number;
  top_urgent_calls: HelpCall[];
  recent_calls: HelpCall[];
  category_distribution: { category: string; count: number }[];
  city_distribution: { city: string; count: number }[];
}

export interface CallFilters {
  city?: string;
  category?: Category;
  min_urgency?: number;
  duplicate_suspected?: boolean;
}

export const CATEGORY_LABELS: Record<Category, string> = {
  enkaz: "Enkaz",
  saglik: "Sağlık",
  su: "Su",
  gida: "Gıda",
  barinma: "Barınma",
  ilac: "İlaç",
  ulasim: "Ulaşım",
  kayip_kisi: "Kayıp Kişi",
  elektrik_isinma: "Elektrik/Isınma",
  diger: "Diğer",
};

export function urgencyBand(score: number): "critical" | "high" | "medium" | "low" {
  if (score >= 80) return "critical";
  if (score >= 50) return "high";
  if (score >= 20) return "medium";
  return "low";
}

export function urgencyColor(score: number): string {
  const b = urgencyBand(score);
  if (b === "critical") return "#b91c1c";
  if (b === "high") return "#ef4444";
  if (b === "medium") return "#facc15";
  return "#94a3b8";
}
