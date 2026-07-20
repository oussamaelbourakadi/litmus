# Screenshots

Real screenshots of the local Docker demo, referenced from the top-level
[`README.md`](../../README.md). All values are computed by the app (the `scripted`
fixture provider) — nothing is faked.

| File | Page | Shows |
| --- | --- | --- |
| `landing.png` | Landing (`/`) | Hero + the three pillars (Evaluate shipped). |
| `dashboard.png` | Projects (`/projects`) | The projects list and the create-project form. |
| `dataset.png` | Dataset detail | The 12 test cases (input → expected). |
| `runs.png` | Dataset detail | The "Launch a run" form, the runs list (100% vs 83.3%), and the compare launcher. |
| `compare.png` | Comparison (`/compare`) | A −16.7% drop flagged as a **regression**, with success/latency deltas. |
| `compare-cases.png` | Comparison (`/compare`) | The per-case diff with the two regressed cases highlighted. |

## Refreshing the screenshots

1. `docker compose up --build` and open `http://localhost:3000`.
2. Follow the **Portfolio Demo** steps in the top-level README to seed a project,
   the demo dataset (`examples/datasets/demo_qa.csv`), and two runs
   (`mock-large` → 100%, `mock-small` → 83.3%).
3. Retake the screenshots and overwrite the files above (keep the same names).
   Use a dark browser theme and a consistent window width (~1600px) so the grid
   in the README stays aligned.
