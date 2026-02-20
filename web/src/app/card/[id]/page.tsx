import { getCard } from "@/lib/api";
import RiskBadge from "@/components/risk-badge";
import type { Metadata } from "next";

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;

  // Fetch card data server-side for OG tags
  const API_BASE =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${API_BASE}/card/${id}`, { cache: "no-store" });
    const data = await res.json();

    if (data.ok && data.data) {
      const card = data.data;
      return {
        title: `${card.title} — Savdhaan AI`,
        description: card.summary,
        openGraph: {
          title: card.title,
          description: card.summary,
          siteName: "Savdhaan AI",
          type: "article",
          images: card.image_url ? [card.image_url] : [],
        },
      };
    }
  } catch {
    // Fall through to default
  }

  return {
    title: "Scam Alert — Savdhaan AI",
    description: "This message has been flagged as a potential scam.",
  };
}

export default async function CardPage({ params }: Props) {
  const { id } = await params;
  const resp = await getCard(id);

  if (!resp.ok || !resp.data) {
    return (
      <main className="mx-auto max-w-2xl px-4 py-20 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Card not found</h1>
        <p className="mt-2 text-gray-500">
          This scam card may have been removed or the link is invalid.
        </p>
      </main>
    );
  }

  const card = resp.data;

  return (
    <main className="mx-auto max-w-2xl px-4 py-12">
      <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
        {/* Header */}
        <div className="mb-6 flex items-start justify-between">
          <div>
            <RiskBadge level={card.risk_level} />
            <h1 className="mt-3 text-2xl font-bold text-gray-900">
              {card.title}
            </h1>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-red-600">
              {card.risk_score}
              <span className="text-lg text-gray-400">/100</span>
            </div>
            <p className="text-xs text-gray-400">Risk Score</p>
          </div>
        </div>

        {/* Summary */}
        <p className="mb-6 text-gray-700 leading-relaxed">{card.summary}</p>

        {/* Scam type */}
        {card.scam_type && (
          <div className="mb-6 rounded-lg bg-gray-50 p-4">
            <p className="text-sm text-gray-500">
              Scam type:{" "}
              <span className="font-semibold text-gray-900">
                {card.scam_type.replace(/_/g, " ")}
              </span>
            </p>
          </div>
        )}

        {/* CTA */}
        <div className="border-t border-gray-200 pt-6">
          <p className="mb-4 text-center text-sm text-gray-500">
            Got a suspicious message? Check it for free.
          </p>
          <div className="flex justify-center">
            <a
              href="/"
              className="rounded-lg bg-red-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700"
            >
              Scan a Message
            </a>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 flex items-center justify-between text-xs text-gray-400">
          <span>
            {new Date(card.created_at).toLocaleDateString("en-US", {
              year: "numeric",
              month: "short",
              day: "numeric",
            })}
          </span>
          <span>{card.view_count} views</span>
        </div>
      </div>

      {/* Powered by */}
      <p className="mt-6 text-center text-xs text-gray-400">
        Powered by{" "}
        <a href="/" className="font-medium text-gray-600 hover:text-gray-900">
          Savdhaan AI
        </a>
      </p>
    </main>
  );
}
