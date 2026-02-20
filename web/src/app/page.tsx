"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { scanText, type ScanResult } from "@/lib/api";
import RiskBadge from "@/components/risk-badge";
import RiskMeter from "@/components/risk-meter";

export default function Home() {
  const router = useRouter();
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    if (!content.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    // Use demo API key for anonymous scans (will be replaced with auth)
    const apiKey = localStorage.getItem("api_key") || "demo";

    const resp = await scanText(content, apiKey);

    if (resp.ok && resp.data) {
      setResult(resp.data);
    } else {
      setError(resp.error?.message || "Something went wrong. Please try again.");
    }
    setLoading(false);
  };

  return (
    <main className="mx-auto max-w-3xl px-4 py-12">
      {/* Hero */}
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
          Is this a <span className="text-red-600">scam</span>?
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          Paste any suspicious message below. We&apos;ll analyze it using AI and
          threat intelligence to tell you what we found.
        </p>
      </div>

      {/* Scan input */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste the suspicious message here...&#10;&#10;Example: Dear customer, your SBI account will be blocked. Update KYC immediately at http://sbi-kyc-update.xyz/verify"
          className="w-full resize-none rounded-lg border border-gray-300 p-4 text-base text-gray-900 placeholder-gray-400 focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20"
          rows={5}
          maxLength={10000}
        />
        <div className="mt-3 flex items-center justify-between">
          <span className="text-sm text-gray-400">
            {content.length}/10,000 characters
          </span>
          <button
            onClick={handleScan}
            disabled={loading || !content.trim()}
            className="rounded-lg bg-red-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg
                  className="h-4 w-4 animate-spin"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Analyzing...
              </span>
            ) : (
              "Scan Message"
            )}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="mt-8 space-y-6">
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
                    Type: <span className="font-medium">{result.scam_type.replace(/_/g, " ")}</span>
                  </p>
                )}
              </div>
              <RiskMeter score={result.risk_score} />
            </div>
          </div>

          {/* Explanation */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h3 className="mb-3 text-lg font-semibold text-gray-900">
              What we found
            </h3>
            <p className="text-gray-700 leading-relaxed">{result.explanation}</p>
          </div>

          {/* Evidence */}
          {result.evidence.length > 0 && (
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
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
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
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
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            {result.confidence_note}
          </div>

          {/* Share card */}
          {result.scam_card && (
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => router.push(`/card/${result.scam_card!.card_id}`)}
                className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
              >
                View Scam Card
              </button>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(result.scam_card!.card_url);
                }}
                className="rounded-lg bg-red-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700"
              >
                Copy Share Link
              </button>
            </div>
          )}

          {/* Processing time */}
          <p className="text-center text-xs text-gray-400">
            Analyzed in {result.processing_time_ms}ms
          </p>
        </div>
      )}

      {/* How it works */}
      {!result && (
        <div className="mt-16">
          <h2 className="mb-8 text-center text-2xl font-bold text-gray-900">
            How it works
          </h2>
          <div className="grid gap-6 sm:grid-cols-3">
            {[
              {
                step: "1",
                title: "Paste",
                desc: "Copy the suspicious message and paste it above",
              },
              {
                step: "2",
                title: "Analyze",
                desc: "AI + threat intelligence analyze the message for scam patterns",
              },
              {
                step: "3",
                title: "Share",
                desc: "Get a shareable scam card to warn others",
              },
            ].map((item) => (
              <div
                key={item.step}
                className="rounded-xl border border-gray-200 bg-white p-6 text-center shadow-sm"
              >
                <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-red-100 text-lg font-bold text-red-600">
                  {item.step}
                </div>
                <h3 className="mb-1 font-semibold text-gray-900">
                  {item.title}
                </h3>
                <p className="text-sm text-gray-500">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
