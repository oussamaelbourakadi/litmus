"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback } from "react";

import { MetricCard } from "@/components/MetricCard";
import { Badge, ErrorState, Spinner } from "@/components/ui";
import { getRun } from "@/lib/api";
import { useAsync } from "@/lib/hooks";
import { formatCost, formatMs, formatPercent } from "@/lib/utils";

export default function RunDetailPage() {
  const params = useParams<{ id: string }>();
  const runId = params.id;
  const { data, loading, error } = useAsync(useCallback(() => getRun(runId), [runId]), [runId]);

  if (loading) return <Spinner label="Loading run…" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  const agg = data.aggregates;
  const ci = agg.success_rate_ci;

  return (
    <div className="space-y-8">
      <div>
        <Link
          href={`/datasets/${data.dataset_id}`}
          className="text-xs text-slate-500 hover:text-slate-300"
        >
          ← Dataset
        </Link>
        <div className="mt-2 flex items-center gap-3">
          <h1 className="text-2xl font-bold">Run {data.id.slice(0, 8)}</h1>
          <Badge tone={data.status === "completed" ? "success" : "warning"}>{data.status}</Badge>
        </div>
      </div>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Success rate"
          value={agg.success_rate !== undefined ? formatPercent(agg.success_rate) : "—"}
          sub={
            ci
              ? `95% CI [${formatPercent(ci.low)}, ${formatPercent(ci.high)}]`
              : undefined
          }
        />
        <MetricCard
          label="Latency P50 / P95"
          value={
            agg.latency_p50 !== undefined && agg.latency_p95 !== undefined
              ? `${formatMs(agg.latency_p50)} / ${formatMs(agg.latency_p95)}`
              : "—"
          }
        />
        <MetricCard
          label="Estimated cost"
          value={agg.total_cost !== undefined ? formatCost(agg.total_cost) : "—"}
        />
        <MetricCard
          label="Cases / errors"
          value={`${agg.total ?? 0} / ${agg.errors ?? 0}`}
          sub={data.repeats > 1 ? `${data.repeats} repeats` : undefined}
        />
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Case results</h2>
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-slate-900 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-3 py-2">Output</th>
                <th className="px-3 py-2">Latency</th>
                <th className="px-3 py-2">Result</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((result, index) => (
                <tr key={`${result.test_case_id}-${result.repeat_index}-${index}`} className="border-t border-slate-800">
                  <td className="max-w-md truncate px-3 py-2 text-slate-200">{result.output || "—"}</td>
                  <td className="px-3 py-2 text-slate-400">{formatMs(result.latency_ms)}</td>
                  <td className="px-3 py-2">
                    <Badge tone={result.passed ? "success" : "danger"}>
                      {result.passed ? "pass" : "fail"}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
