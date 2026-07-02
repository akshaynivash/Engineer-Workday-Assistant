const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

export interface PartSummary {
  ID: string;
  DESCRIPTION: string;
  Application: string;
  Attribut1: string;
}

export interface PartDetail extends PartSummary {
  "Rated Current (A)": string;
  "Rated Voltage (V)": string;
  "Rated Voltage (VDC)": string;
  "Rated Breaking Capacity (A)": string;
  Mounting: string;
}

export interface PartFacets {
  applications: string[];
  fuse_types: string[];
}

export type Tier = "Tier 1" | "Tier 2" | "Tier 3" | "Tier 4" | "Tier 5";

export class ApiError extends Error {
  status: number;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body?.detail ?? `Request failed with status ${response.status}`);
  }
  return response.json();
}

export function checkHealth(): Promise<{ status: string }> {
  return request("/api/health");
}

export function browseParts(params: { application?: string; fuseType?: string; limit?: number } = {}): Promise<PartSummary[]> {
  const query = new URLSearchParams();
  if (params.application) query.set("application", params.application);
  if (params.fuseType) query.set("fuse_type", params.fuseType);
  if (params.limit) query.set("limit", String(params.limit));
  const qs = query.toString();
  return request(`/api/parts${qs ? `?${qs}` : ""}`);
}

export function getPartFacets(): Promise<PartFacets> {
  return request("/api/parts/facets");
}

export function getPart(partId: string): Promise<PartDetail> {
  return request(`/api/parts/${encodeURIComponent(partId)}`);
}

export function getAlternatives(partId: string, tier: Tier): Promise<PartSummary[]> {
  return request(`/api/parts/${encodeURIComponent(partId)}/alternatives?tier=${encodeURIComponent(tier)}`);
}

export function explainPart(
  partId: string,
  payload: { useAi: boolean; alternativeId?: string | null },
): Promise<{ explanation: string }> {
  return request(`/api/parts/${encodeURIComponent(partId)}/explain`, {
    method: "POST",
    body: JSON.stringify({ use_ai: payload.useAi, alternative_id: payload.alternativeId ?? null }),
  });
}

export function sendChat(message: string): Promise<{ response: string }> {
  return request("/api/chat", { method: "POST", body: JSON.stringify({ message }) });
}

export function sendAssistantChat(message: string): Promise<{ response: string }> {
  return request("/api/assistant/chat", { method: "POST", body: JSON.stringify({ message }) });
}

export function createTask(payload: { task: string; answer: string; day?: string | null }): Promise<{ message: string }> {
  return request("/api/assistant/tasks", {
    method: "POST",
    body: JSON.stringify({ task: payload.task, answer: payload.answer, day: payload.day ?? null }),
  });
}

export function getRecentTasks(limit = 5): Promise<string[]> {
  return request(`/api/assistant/tasks/recent?limit=${limit}`);
}
