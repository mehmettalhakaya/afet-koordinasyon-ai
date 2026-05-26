// REST istemcisi - tek dosyalı, fetch tabanlı.
// Backend dev'de http://localhost:8000, Vite proxy /api'yi oraya yönlendiriyor.
import type {
  AnalyzeResponse,
  CallFilters,
  DashboardStats,
  HelpCall,
  HelpCallCreate,
} from "../types";

const BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API hatası ${res.status}: ${text || res.statusText}`);
  }
  return (await res.json()) as T;
}

export const api = {
  listCalls: (filters: CallFilters = {}) => {
    const params = new URLSearchParams();
    if (filters.city) params.set("city", filters.city);
    if (filters.category) params.set("category", filters.category);
    if (filters.min_urgency != null)
      params.set("min_urgency", String(filters.min_urgency));
    if (filters.duplicate_suspected != null)
      params.set("duplicate_suspected", String(filters.duplicate_suspected));
    const q = params.toString();
    return request<HelpCall[]>(`/api/calls${q ? "?" + q : ""}`);
  },

  getCall: (id: number) => request<HelpCall>(`/api/calls/${id}`),

  createCall: (payload: HelpCallCreate) =>
    request<HelpCall>("/api/calls", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  analyze: (payload: {
    text: string;
    city?: string;
    district?: string;
    people_count?: number;
  }) =>
    request<AnalyzeResponse>("/api/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  dashboard: () => request<DashboardStats>("/api/dashboard"),

  retrain: () =>
    request<{ status: string; samples_used: number; accuracy: number }>("/api/retrain", {
      method: "POST",
    }),
};
