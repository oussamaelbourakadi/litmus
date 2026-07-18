import { cn } from "@/lib/utils";

interface Pillar {
  name: string;
  phase: string;
  when: string;
  description: string;
  accent: string;
}

const PILLARS: Pillar[] = [
  {
    name: "Evaluate",
    phase: "Phase 1",
    when: "before deployment",
    description:
      "Metrics, run comparison, regression detection, and a CI gate — with confidence intervals, fixed seeds, and reproducible results.",
    accent: "text-emerald-300",
  },
  {
    name: "Red-Team",
    phase: "Phase 2 · 3",
    when: "before deployment",
    description:
      "Systematic attack suites mapped to OWASP LLM Top 10, plus adversarial vision attacks (FGSM, PGD, patches) — the differentiator.",
    accent: "text-rose-300",
  },
  {
    name: "Monitor",
    phase: "Phase 4",
    when: "after deployment",
    description:
      "Live production traces, online evaluation, drift detection, alerting, and a trace-to-test loop back into your datasets.",
    accent: "text-sky-300",
  },
];

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center gap-12 px-6 py-16">
      <header className="space-y-4">
        <p className="text-sm font-medium uppercase tracking-widest text-brand">Litmus</p>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Ship AI you can trust.
        </h1>
        <p className="max-w-2xl text-lg text-slate-400">
          An open-source, self-hostable platform to evaluate, red-team, and monitor AI systems —
          LLMs, RAG, agents, and vision — before and after production. Runs with{" "}
          <span className="font-medium text-slate-200">no API key</span> thanks to mock and local
          providers.
        </p>
      </header>

      <section className="grid gap-4 sm:grid-cols-3" aria-label="Product pillars">
        {PILLARS.map((pillar) => (
          <article
            key={pillar.name}
            className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 transition hover:border-slate-700"
          >
            <div className="flex items-baseline justify-between">
              <h2 className={cn("text-lg font-semibold", pillar.accent)}>{pillar.name}</h2>
              <span className="text-xs text-slate-500">{pillar.phase}</span>
            </div>
            <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{pillar.when}</p>
            <p className="mt-3 text-sm leading-relaxed text-slate-400">{pillar.description}</p>
          </article>
        ))}
      </section>

      <footer className="text-sm text-slate-500">
        Phase 1.0 — foundation scaffold. Engine, dashboard, SDK, and CI gate land in the next
        sub-phases.
      </footer>
    </main>
  );
}
