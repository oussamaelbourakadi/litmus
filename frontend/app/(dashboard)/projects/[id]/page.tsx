"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useState } from "react";

import { Button, Card, EmptyState, ErrorState, Input, Spinner } from "@/components/ui";
import { createDataset, getProject, listDatasets } from "@/lib/api";
import { useAsync } from "@/lib/hooks";

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id;

  const project = useAsync(useCallback(() => getProject(projectId), [projectId]), [projectId]);
  const datasets = useAsync(useCallback(() => listDatasets(projectId), [projectId]), [projectId]);

  const [name, setName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function onCreate(event: React.FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    setSubmitting(true);
    setFormError(null);
    try {
      await createDataset(projectId, { name: name.trim() });
      setName("");
      datasets.reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "failed to create dataset");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <Link href="/projects" className="text-xs text-slate-500 hover:text-slate-300">
          ← Projects
        </Link>
        <h1 className="mt-2 text-2xl font-bold">{project.data?.name ?? "Project"}</h1>
        {project.error ? <ErrorState message={project.error} /> : null}
      </div>

      <Card>
        <form onSubmit={onCreate} className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1">
            <label className="mb-1 block text-xs uppercase tracking-wide text-slate-500">
              New dataset name
            </label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. QA set" />
          </div>
          <Button type="submit" disabled={submitting || !name.trim()}>
            {submitting ? "Creating…" : "Create dataset"}
          </Button>
        </form>
        {formError ? <p className="mt-3 text-sm text-rose-300">{formError}</p> : null}
      </Card>

      <div>
        <h2 className="mb-3 text-lg font-semibold">Datasets</h2>
        {datasets.loading ? <Spinner /> : null}
        {datasets.error ? <ErrorState message={datasets.error} /> : null}
        {datasets.data && datasets.data.length === 0 ? (
          <EmptyState message="No datasets yet. Create one above." />
        ) : null}
        {datasets.data && datasets.data.length > 0 ? (
          <ul className="grid gap-3 sm:grid-cols-2">
            {datasets.data.map((dataset) => (
              <li key={dataset.id}>
                <Link href={`/datasets/${dataset.id}`}>
                  <Card className="transition hover:border-slate-700">
                    <p className="font-semibold text-slate-100">{dataset.name}</p>
                    {dataset.description ? (
                      <p className="mt-1 text-xs text-slate-500">{dataset.description}</p>
                    ) : null}
                  </Card>
                </Link>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
    </div>
  );
}
