import { urgencyBand } from "../types";

export function UrgencyBadge({ score }: { score: number }) {
  const band = urgencyBand(score);
  const label =
    band === "critical"
      ? "ÇOK ACİL"
      : band === "high"
      ? "YÜKSEK"
      : band === "medium"
      ? "ORTA"
      : "DÜŞÜK";
  return (
    <span className={`badge badge-${band}`}>
      {label} · {score}
    </span>
  );
}
