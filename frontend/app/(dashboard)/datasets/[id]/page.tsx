"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useState } from "react";

import { Button, Card, EmptyState, ErrorState, Input, Select, Spinner } from "@/components/ui";
import {
  addCasesCsv,
  createRun,
  getDataset,
  listRuns,
  type EvaluatorSpec,
} from "@/lib/api";
import { useAsync } from "@/lib/hooks";
import { formatPercent } from "@/lib/utils";

export default function DatasetDetailPage() {
  const params = useParams<{ id: string }>();
  const datasetId = params.id;
  const router = useRouter();

  const dataset = useAsync(useCallback(() => getDataset(datasetId), [datasetId]), [datasetId]);
  const runs = useAsync(useCallback(() => listRuns(datasetId), [datasetId]), [datasetId]);

  const [csv, setCsv] = useState("input,expected\n");
  const [csvBusy, setCsvBusy] = useState(false);
  const [csvError, setCsvError] = useState<string | null>(null);

  const [provider, setProvider] = useState("mock");
  const [repeats, setRepeats] = useState(1);
  const [useExact, setUseExact] = useState(true);
  const [useRegex, setUseRegex] = useState(false);
  const [pattern, setPattern] = useState("");
  const [runBusy, setRunBusy] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  const [base, setBase] = useState("");
  const [candidate, setCandidate] = useState("");

  async function onUploadCsv(event: React.FormEvent) {
    event.preventDefault();
    setCsvBusy(true);
    setCsvError(null);
    try {
      await addCasesCsv(datasetId, csv);
      setCsv("input,expected\n");
      dataset.reload();
    } catch (err) {
      setCsvError(err instanceof Error ? err.message : "upload failed");
    } finally {
      setCsvBusy(false);
    }
  }

  async function onLaunchRun(event: React.FormEvent) {
    event.preventDefault();
    const evaluators: EvaluatorSpec[] = [];
    if (useExact) evaluators.push({ name: "exact_match" });
    if (useRegex) evaluators.push({ name: "regex_match", params: { pattern } });
    if (evaluators.length === 0) {
      setRunError("select at least one evaluator");
      return;
    }
    setRunBusy(true);
    setRunError(null);
    try {
      const run = await createRun(datasetId, { provider, repeats, evaluators });
      router.push(`/runs/${run.id}`);
    } catch (err) {
      setRunError(err instanceof Error ? err.message : "run failed");
      setRunBusy(false);
    }
  }

  function onCompare() {
    if (base && candidate) router.push(`/compare?base=${base}&candidate=${candidate}`);
  }

  return (
    <div className="space-y-8">
      <div>
        <Link
          href={dataset.data ? `/projects/${dataset.data.project_id}` : "/projects"}
          className="text-xs text-slate-500 hover:text-slate-300"
        >
          ← Project
        </Link>
        <h1 className="mt-2 text-2xl font-bold">{dataset.data?.name ?? "Dataset"}</h1>
        {dataset.error ? <ErrorState message={dataset.error} /> : null}
      </div>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Test cases</h2>
        {dataset.loading ? <Spinner /> : null}
        {dataset.data && dataset.data.cases.length === 0 ? (
          <EmptyState message="No test cases yet. Add some via CSV below." />
        ) : null}
        {dataset.data && dataset.data.cases.length > 0 ? (
          <div className="overflow-x-auto rounded-lg border border-slate-800">
            <table className="w-full text-sm">
              <thead className="bg-slate-900 text-left text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">Input</th>
                  <th className="px-3 py-2">Expected</th>
                </tr>
              </thead>
              <tbody>
                {dataset.data.cases.map((testCase) => (
                  <tr key={testCase.id} className="border-t border-slate-800">
                    <td className="px-3 py-2 text-slate-200">{testCase.input}</td>
                    <td className="px-3 py-2 text-slate-400">{testCase.expected ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>

      <Card>
        <h2 className="mb-3 text-lg font-semibold">Add cases (CSV)</h2>
        <form onSubmit={onUploadCsv} className="space-y-3">
          <textarea
            value={csv}
            onChange={(e) => setCsv(e.target.value)}
            rows={4}
            className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-slate-100 outline-none focus:border-brand"
          />
          <Button type="submit" disabled={csvBusy}>
            {csvBusy ? "Uploading…" : "Upload CSV"}
          </Button>
          {csvError ? <p className="text-sm text-rose-300">{csvError}</p> : null}
        </form>
      </Card>

      <Card>
        <h2 className="mb-3 text-lg font-semibold">Launch a run</h2>
        <form onSubmit={onLaunchRun} className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-3">
            <div>
              <label className="mb-1 block text-xs uppercase tracking-wide text-slate-500">
                Provider
              </label>
              <Select value={provider} onChange={(e) => setProvider(e.target.value)}>
                <option value="mock">mock</option>
                <option value="ollama">ollama</option>
              </Select>
            </div>
            <div>
              <label className="mb-1 block text-xs uppercase tracking-wide text-slate-500">
                Repeats
              </label>
              <Input
                type="number"
                min={1}
                max={50}
                value={repeats}
                onChange={(e) => setRepeats(Number(e.target.value))}
              />
            </div>
          </div>
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={useExact}
                onChange={(e) => setUseExact(e.target.checked)}
              />
              Exact match
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={useRegex}
                onChange={(e) => setUseRegex(e.target.checked)}
              />
              Regex match
            </label>
            {useRegex ? (
              <Input
                value={pattern}
                onChange={(e) => setPattern(e.target.value)}
                placeholder="regex pattern, e.g. \\d+"
              />
            ) : null}
          </div>
          <Button type="submit" disabled={runBusy}>
            {runBusy ? "Running…" : "Run evaluation"}
          </Button>
          {runError ? <p className="text-sm text-rose-300">{runError}</p> : null}
        </form>
      </Card>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Runs</h2>
        {runs.loading ? <Spinner /> : null}
        {runs.error ? <ErrorState message={runs.error} /> : null}
        {runs.data && runs.data.length === 0 ? (
          <EmptyState message="No runs yet. Launch one above." />
        ) : null}
        {runs.data && runs.data.length > 0 ? (
          <div className="space-y-4">
            <div className="overflow-x-auto rounded-lg border border-slate-800">
              <table className="w-full text-sm">
                <thead className="bg-slate-900 text-left text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-3 py-2">Run</th>
                    <th className="px-3 py-2">Status</th>
                    <th className="px-3 py-2">Success</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.data.map((run) => (
                    <tr key={run.id} className="border-t border-slate-800">
                      <td className="px-3 py-2">
                        <Link href={`/runs/${run.id}`} className="text-brand hover:underline">
                          {run.id.slice(0, 8)}
                        </Link>
                      </td>
                      <td className="px-3 py-2 text-slate-400">{run.status}</td>
                      <td className="px-3 py-2 text-slate-200">
                        {run.success_rate === null ? "—" : formatPercent(run.success_rate)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <Card>
              <h3 className="mb-3 text-sm font-semibold text-slate-200">Compare two runs</h3>
              <div className="grid gap-3 sm:grid-cols-3">
                <Select value={base} onChange={(e) => setBase(e.target.value)}>
                  <option value="">base run…</option>
                  {runs.data.map((run) => (
                    <option key={run.id} value={run.id}>
                      {run.id.slice(0, 8)}
                    </option>
                  ))}
                </Select>
                <Select value={candidate} onChange={(e) => setCandidate(e.target.value)}>
                  <option value="">candidate run…</option>
                  {runs.data.map((run) => (
                    <option key={run.id} value={run.id}>
                      {run.id.slice(0, 8)}
                    </option>
                  ))}
                </Select>
                <Button variant="ghost" onClick={onCompare} disabled={!base || !candidate}>
                  Compare
                </Button>
              </div>
            </Card>
          </div>
        ) : null}
      </section>
    </div>
  );
}
