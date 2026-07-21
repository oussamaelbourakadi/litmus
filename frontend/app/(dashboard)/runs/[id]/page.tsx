"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { MetricCard } from "@/components/MetricCard";
import { Badge, Button, ErrorState, Spinner } from "@/components/ui";
import { cancelRun, getRun, isTerminal, type Run } from "@/lib/api";
import { formatCost, formatMs, formatPercent } from "@/lib/utils";

function statusTone(status: string): "success" | "danger" | "warning" {
  if (status === "completed") return "success";
  if (status === "failed" || status === "cancelled") return "danger";
  return "warning";
}

export default function RunDetailPage() {
  const params = useParams<{ id: string }>();
  const runId = params.id;
  const [run, setRun] = useState<Run | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    async function tick() {
      try {
        const data = await getRun(runId);
        if (!active) return;
        setRun(data);
        if (!isTerminal(data.status)) {
          timer = setTimeout(tick, 1000);
        }
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : String(err));
      }
    }
    void tick();
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [runId]);

  const onCancel = useCallback(async () => {
    setCancelling(true);
    try {
      await cancelRun(runId);
    } catch {
      // ignore — polling will reflect the final state
    } finally {
      setCancelling(false);
    }
  }, [runId]);

  if (error) return <ErrorState message={error} />;
  if (!run) return <Spinner label="Loading run…" />;

  const agg = run.aggregates;
  const ci = agg.success_rate_ci;
  const running = !isTerminal(run.status);

  return (
    <div className="space-y-8">
      <div>
        <Link
          href={`/datasets/${run.dataset_id}`}
          className="text-xs text-slate-500 hover:text-slate-300"
        >
          ← Dataset
        </Link>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold">Run {run.id.slice(0, 8)}</h1>
          <Badge tone={statusTone(run.status)}>{run.status}</Badge>
          {running ? (
            <>
              <span className="text-sm text-slate-400">
                {run.completed_cases}/{run.total_cases} cases
              </span>
              <Button variant="ghost" onClick={onCancel} disabled={cancelling}>
                {cancelling ? "Cancelling…" : "Cancel"}
              </Button>
            </>
          ) : null}
        </div>
        {run.error ? <p className="mt-2 text-sm text-rose-300">{run.error}</p> : null}
      </div>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Success rate"
          value={agg.success_rate !== undefined ? formatPercent(agg.success_rate) : "—"}
          sub={ci ? `95% CI [${formatPercent(ci.low)}, ${formatPercent(ci.high)}]` : undefined}
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
          sub={run.repeats > 1 ? `${run.repeats} repeats` : undefined}
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
              {run.results.map((result, index) => (
                <tr
                  key={`${result.test_case_id}-${result.repeat_index}-${index}`}
                  className="border-t border-slate-800"
                >
                  <td className="max-w-md truncate px-3 py-2 text-slate-200">
                    {result.output || "—"}
                  </td>
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
