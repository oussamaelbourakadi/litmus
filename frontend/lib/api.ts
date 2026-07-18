/**
 * Minimal typed client for the Litmus backend. Expanded in Phase 1.4/1.5 as the
 * API surface grows; for now it exposes the health probe.
 */

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface HealthStatus {
  status: string;
  version: string;
  environment: string;
}

export async function getHealth(signal?: AbortSignal): Promise<HealthStatus> {
  const response = await fetch(`${API_URL}/health`, {
    signal,
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Backend health check failed: ${response.status}`);
  }
  return (await response.json()) as HealthStatus;
}
