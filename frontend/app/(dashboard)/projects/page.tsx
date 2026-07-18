"use client";

import Link from "next/link";
import { useState } from "react";

import { Button, Card, EmptyState, ErrorState, Input, Spinner } from "@/components/ui";
import { createProject, listProjects } from "@/lib/api";
import { useAsync } from "@/lib/hooks";

function slugify(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export default function ProjectsPage() {
  const { data, loading, error, reload } = useAsync(listProjects, []);
  const [name, setName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function onCreate(event: React.FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    setSubmitting(true);
    setFormError(null);
    try {
      await createProject({ name: name.trim(), slug: slugify(name) });
      setName("");
      reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "failed to create project");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Projects</h1>
        <p className="mt-1 text-sm text-slate-400">Create a project, then add datasets and runs.</p>
      </div>

      <Card>
        <form onSubmit={onCreate} className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1">
            <label className="mb-1 block text-xs uppercase tracking-wide text-slate-500">
              New project name
            </label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Support chatbot"
            />
          </div>
          <Button type="submit" disabled={submitting || !name.trim()}>
            {submitting ? "Creating…" : "Create project"}
          </Button>
        </form>
        {formError ? <p className="mt-3 text-sm text-rose-300">{formError}</p> : null}
      </Card>

      {loading ? <Spinner /> : null}
      {error ? <ErrorState message={error} /> : null}
      {data && data.length === 0 ? <EmptyState message="No projects yet. Create one above." /> : null}

      {data && data.length > 0 ? (
        <ul className="grid gap-3 sm:grid-cols-2">
          {data.map((project) => (
            <li key={project.id}>
              <Link href={`/projects/${project.id}`}>
                <Card className="transition hover:border-slate-700">
                  <p className="font-semibold text-slate-100">{project.name}</p>
                  <p className="mt-1 text-xs text-slate-500">{project.slug}</p>
                </Card>
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
