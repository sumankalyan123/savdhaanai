const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ApiResponse<T> {
  ok: boolean;
  data: T | null;
  error: { code: string; message: string; details?: Record<string, unknown> } | null;
  meta?: Record<string, unknown>;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  return res.json();
}

// --- Auth ---

export async function register(
  email: string,
  password: string,
  displayName?: string
) {
  return request<{
    access_token: string;
    refresh_token: string;
    expires_in: number;
  }>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, display_name: displayName }),
  });
}

export async function login(email: string, password: string) {
  return request<{
    access_token: string;
    refresh_token: string;
    expires_in: number;
  }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function refreshToken(refreshToken: string) {
  return request<{
    access_token: string;
    refresh_token: string;
    expires_in: number;
  }>("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

// --- Scan ---

export interface ScanResult {
  scan_id: string;
  risk_score: number;
  risk_level: string;
  scam_type: string | null;
  explanation: string;
  evidence: { source: string; detail: string; is_threat: boolean }[];
  actions: string[];
  entities: {
    urls: string[];
    phones: string[];
    emails: string[];
    crypto_addresses: string[];
    upi_ids: string[];
  };
  checks_performed: string[];
  checks_not_available: string[];
  confidence_note: string;
  scam_card: { card_id: string; card_url: string; image_url?: string } | null;
  processing_time_ms: number;
  created_at: string;
}

export async function scanText(content: string, apiKey: string) {
  return request<ScanResult>("/scan", {
    method: "POST",
    headers: { "X-API-Key": apiKey },
    body: JSON.stringify({ content, content_type: "text" }),
  });
}

export async function getScan(scanId: string, apiKey: string) {
  return request<ScanResult>(`/scan/${scanId}`, {
    headers: { "X-API-Key": apiKey },
  });
}

// --- Card ---

export interface CardData {
  card_id: string;
  title: string;
  summary: string;
  risk_level: string;
  risk_score: number;
  scam_type: string | null;
  card_url: string;
  image_url: string | null;
  view_count: number;
  created_at: string;
}

export async function getCard(shortId: string) {
  return request<CardData>(`/card/${shortId}`);
}
