"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useCallback } from "react";

import { MetricCard } from "@/components/MetricCard";
import { VerdictBadge } from "@/components/VerdictBadge";
import { Card, EmptyState, ErrorState, Spinner } from "@/components/ui";
import { compareRuns } from "@/lib/api";
import { useAsync } from "@/lib/hooks";
import { cn, formatMs, formatPercent, formatSignedPercent } from "@/lib/utils";

function CompareInner() {
  const params = useSearchParams();
  const base = params.get("base") ?? "";
  const candidate = params.get("candidate") ?? "";

  const { data, loading, error } = useAsync(
    useCallback(() => compareRuns(base, candidate), [base, candidate]),
    [base, candidate],
  );

  if (!base || !candidate) {
    return <EmptyState message="Provide base and candidate run ids to compare." />;
  }
  if (loading) return <Spinner label="Comparing runs…" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold">Comparison</h1>
        <VerdictBadge passed={data.verdict.passed} />
      </div>
      <p className="text-sm text-slate-400">{data.verdict.reason}</p>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Base success" value={formatPercent(data.success_rate_base)} />
        <MetricCard label="Candidate success" value={formatPercent(data.success_rate_candidate)} />
        <MetricCard
          label="Success delta"
          value={formatSignedPercent(data.success_rate_delta)}
        />
        <MetricCard
          label="Regressions / improvements"
          value={`${data.regressions} / ${data.improvements}`}
        />
      </section>

      <Card>
        <p className="text-sm text-slate-400">
          Latency P50 Δ {formatMs(data.latency_p50_delta)} · P95 Δ {formatMs(data.latency_p95_delta)}
        </p>
      </Card>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Per-case changes</h2>
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-slate-900 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-3 py-2">Case</th>
                <th className="px-3 py-2">Base</th>
                <th className="px-3 py-2">Candidate</th>
                <th className="px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.case_changes.map((change) => (
                <tr
                  key={change.test_case_id}
                  className={cn(
                    "border-t border-slate-800",
                    change.status === "regressed" && "bg-rose-950/40",
                    change.status === "improved" && "bg-emerald-950/30",
                  )}
                >
                  <td className="px-3 py-2 text-slate-400">{change.test_case_id.slice(0, 8)}</td>
                  <td className="px-3 py-2 text-slate-200">{formatPercent(change.base_pass_rate)}</td>
                  <td className="px-3 py-2 text-slate-200">
                    {formatPercent(change.candidate_pass_rate)}
                  </td>
                  <td className="px-3 py-2 text-slate-300">{change.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<Spinner />}>
      <CompareInner />
    </Suspense>
  );
}
