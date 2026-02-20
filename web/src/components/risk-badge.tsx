const RISK_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  critical: { bg: "bg-red-100", text: "text-red-800", border: "border-red-300" },
  high: { bg: "bg-orange-100", text: "text-orange-800", border: "border-orange-300" },
  medium: { bg: "bg-yellow-100", text: "text-yellow-800", border: "border-yellow-300" },
  low: { bg: "bg-blue-100", text: "text-blue-800", border: "border-blue-300" },
  none: { bg: "bg-green-100", text: "text-green-800", border: "border-green-300" },
};

export default function RiskBadge({ level }: { level: string }) {
  const colors = RISK_COLORS[level] || RISK_COLORS.none;
  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold uppercase ${colors.bg} ${colors.text} ${colors.border}`}
    >
      {level}
    </span>
  );
}
