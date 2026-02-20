function getColor(score: number): string {
  if (score >= 80) return "#ef4444";
  if (score >= 60) return "#f97316";
  if (score >= 40) return "#eab308";
  if (score >= 20) return "#3b82f6";
  return "#22c55e";
}

export default function RiskMeter({ score }: { score: number }) {
  const color = getColor(score);
  const rotation = (score / 100) * 180 - 90; // -90 to 90 degrees

  return (
    <div className="flex flex-col items-center">
      <div className="relative h-24 w-48 overflow-hidden">
        {/* Background arc */}
        <div className="absolute inset-0 rounded-t-full border-8 border-b-0 border-gray-200" />
        {/* Colored fill */}
        <div
          className="absolute inset-0 rounded-t-full border-8 border-b-0"
          style={{
            borderColor: color,
            clipPath: `polygon(0 100%, 0 0, ${score}% 0, ${score}% 100%)`,
          }}
        />
        {/* Needle */}
        <div
          className="absolute bottom-0 left-1/2 h-20 w-1 origin-bottom rounded-full bg-gray-800"
          style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
        />
        {/* Center dot */}
        <div className="absolute bottom-0 left-1/2 h-3 w-3 -translate-x-1/2 translate-y-1/2 rounded-full bg-gray-800" />
      </div>
      <div className="mt-2 text-3xl font-bold" style={{ color }}>
        {score}
        <span className="text-lg text-gray-500">/100</span>
      </div>
    </div>
  );
}
