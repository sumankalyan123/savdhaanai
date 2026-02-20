"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getScan, type ScanResult } from "@/lib/api";
import RiskBadge from "@/components/risk-badge";
import RiskMeter from "@/components/risk-meter";

export default function ScanPage() {
  const params = useParams();
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchScan = async () => {
      const apiKey = localStorage.getItem("api_key") || "";
      const resp = await getScan(params.id as string, apiKey);
      if (resp.ok && resp.data) {
        setResult(resp.data);
      } else {
        setError(resp.error?.message || "Scan not found");
      }
      setLoading(false);
    };
    fetchScan();
  }, [params.id]);

  if (loading) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-20 text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-red-600" />
        <p className="mt-4 text-gray-500">Loading scan result...</p>
      </main>
    );
  }

  if (error || !result) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-20 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Scan not found</h1>
        <p className="mt-2 text-gray-500">{error}</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-12">
      {/* Risk overview */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-gray-900">
                Risk Assessment
              </h2>
              <RiskBadge level={result.risk_level} />
            </div>
            {result.scam_type && (
              <p className="mt-1 text-sm text-gray-500">
                Type:{" "}
                <span className="font-medium">
                  {result.scam_type.replace(/_/g, " ")}
                </span>
              </p>
            )}
          </div>
          <RiskMeter score={result.risk_score} />
        </div>
      </div>

      {/* Explanation */}
      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="mb-3 text-lg font-semibold text-gray-900">
          What we found
        </h3>
        <p className="text-gray-700 leading-relaxed">{result.explanation}</p>
      </div>

      {/* Evidence */}
      {result.evidence.length > 0 && (
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h3 className="mb-3 text-lg font-semibold text-gray-900">
            Evidence
          </h3>
          <ul className="space-y-2">
            {result.evidence.map((e, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span
                  className={`mt-0.5 h-2 w-2 flex-shrink-0 rounded-full ${
                    e.is_threat ? "bg-red-500" : "bg-gray-400"
                  }`}
                />
                <span className="text-gray-700">
                  <span className="font-medium text-gray-900">
                    {e.source}:
                  </span>{" "}
                  {e.detail}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      {result.actions.length > 0 && (
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h3 className="mb-3 text-lg font-semibold text-gray-900">
            Recommended Actions
          </h3>
          <ul className="space-y-2">
            {result.actions.map((action, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-sm text-gray-700"
              >
                <span className="mt-0.5 text-red-500">&#10140;</span>
                {action}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Confidence note */}
      <div className="mt-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        {result.confidence_note}
      </div>

      {/* Meta */}
      <p className="mt-4 text-center text-xs text-gray-400">
        Scan ID: {result.scan_id} | Analyzed in {result.processing_time_ms}ms
      </p>
    </main>
  );
}
