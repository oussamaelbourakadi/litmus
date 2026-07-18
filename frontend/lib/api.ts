/**
 * Typed client for the Litmus backend. Plain fetch, no external data library.
 */

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface HealthStatus {
  status: string;
  version: string;
  environment: string;
}

export interface Project {
  id: string;
  name: string;
  slug: string;
  description: string | null;
}

export interface TestCase {
  id: string;
  input: string;
  expected: string | null;
  metadata: Record<string, unknown>;
}

export interface Dataset {
  id: string;
  project_id: string;
  name: string;
  description: string | null;
  cases: TestCase[];
}

export interface DatasetSummary {
  id: string;
  project_id: string;
  name: string;
  description: string | null;
}

export interface ConfidenceInterval {
  point: number;
  low: number;
  high: number;
  confidence: number;
}

export interface Aggregates {
  total: number;
  passed: number;
  errors: number;
  success_rate: number;
  success_rate_ci: ConfidenceInterval;
  latency_p50: number;
  latency_p95: number;
  latency_mean: number;
  total_cost: number;
  evaluator_pass_rates: Record<string, number>;
  repeat_success_mean: number | null;
  repeat_success_std: number | null;
}

export interface CaseResult {
  test_case_id: string;
  repeat_index: number;
  output: string;
  latency_ms: number;
  passed: boolean;
  scores: Record<string, { value: number; passed: boolean; reason: string | null }>;
  error: string | null;
}

export interface Run {
  id: string;
  project_id: string;
  dataset_id: string;
  status: string;
  repeats: number;
  aggregates: Partial<Aggregates>;
  error: string | null;
  results: CaseResult[];
}

export interface RunSummary {
  id: string;
  dataset_id: string;
  status: string;
  success_rate: number | null;
  created_at: string;
}

export interface EvaluatorSpec {
  name: string;
  params?: Record<string, unknown>;
}

export interface RunRequest {
  provider?: string;
  model?: string;
  repeats?: number;
  evaluators: EvaluatorSpec[];
}

export interface CaseChange {
  test_case_id: string;
  base_pass_rate: number;
  candidate_pass_rate: number;
  status: "regressed" | "improved" | "unchanged" | "added" | "removed";
}

export interface Comparison {
  base_run_id: string;
  candidate_run_id: string;
  success_rate_base: number;
  success_rate_candidate: number;
  success_rate_delta: number;
  latency_p50_delta: number;
  latency_p95_delta: number;
  cost_delta: number;
  regressions: number;
  improvements: number;
  case_changes: CaseChange[];
  verdict: { passed: boolean; reason: string };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // response had no JSON body; keep the status text.
    }
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

export const getHealth = () => request<HealthStatus>("/health");

export const listProjects = () => request<Project[]>("/projects");
export const getProject = (id: string) => request<Project>(`/projects/${id}`);
export const createProject = (body: { name: string; slug: string; description?: string }) =>
  request<Project>("/projects", { method: "POST", body: JSON.stringify(body) });

export const listDatasets = (projectId: string) =>
  request<DatasetSummary[]>(`/projects/${projectId}/datasets`);
export const getDataset = (id: string) => request<Dataset>(`/datasets/${id}`);
export const createDataset = (
  projectId: string,
  body: { name: string; description?: string },
) => request<Dataset>(`/projects/${projectId}/datasets`, { method: "POST", body: JSON.stringify(body) });

export const addCasesCsv = (datasetId: string, csv: string) =>
  request<Dataset>(`/datasets/${datasetId}/cases/csv`, {
    method: "POST",
    body: JSON.stringify({ csv }),
  });

export const addCases = (
  datasetId: string,
  cases: Array<{ input: string; expected?: string }>,
) => request<Dataset>(`/datasets/${datasetId}/cases`, { method: "POST", body: JSON.stringify({ cases }) });

export const listRuns = (datasetId: string) =>
  request<RunSummary[]>(`/datasets/${datasetId}/runs`);
export const getRun = (id: string) => request<Run>(`/runs/${id}`);
export const createRun = (datasetId: string, body: RunRequest) =>
  request<Run>(`/datasets/${datasetId}/runs`, { method: "POST", body: JSON.stringify(body) });

export const compareRuns = (baseRunId: string, candidateRunId: string) =>
  request<Comparison>("/compare", {
    method: "POST",
    body: JSON.stringify({ base_run_id: baseRunId, candidate_run_id: candidateRunId }),
  });
