# Screenshots

The `.png` files here are **labeled placeholders**. Replace each with a real
screenshot of your running instance for a portfolio-ready README.

## Seed the demo data first (2 minutes)

1. `docker compose up --build`, then open `http://localhost:3000`.
2. **Projects** → create `Portfolio Demo`.
3. Open it → create a dataset `General knowledge QA`.
4. Open the dataset → **Add cases (CSV)** → paste the contents of
   [`examples/datasets/demo_qa.csv`](../../examples/datasets/demo_qa.csv) → Upload.
5. **Launch a run** → provider `scripted`, model **`mock-small`**, Exact match → Run.
   (~**83%** success.)
6. Go back to the dataset → **Launch a run** again → model **`mock-large`** → Run.
   (**100%** success.)

## What each screenshot should show

| File | Page | Expected values |
| --- | --- | --- |
| `dashboard.png` | The dataset page (or Projects) | The 12-case table + the "Launch a run" form + the runs list with two runs (100% and 83%). |
| `runs.png` | Run detail of **Run #2 (mock-large)** | Success **100%**, latency P50/P95 (~197/257 ms), cost (~$0.004), 12 cases, all-PASS table. |
| `metrics.png` | Run detail metric cards (Run #2), close-up | Success **100%** with **95% CI [100%, 100%]**, latency, cost, cases. |
| `compare.png` | `/compare` (base = Run #1, candidate = Run #2) | Verdict **PASS**, success **+16.7%**, **2 improvements** highlighted green, latency/cost deltas. |

## Tips

- Use a dark browser theme (the dashboard is dark by default).
- Keep a consistent window width (~1600px) so images align in the README grid.
- Screenshot shortcuts: Windows `Win+Shift+S`, macOS `Cmd+Shift+4`, Linux your tool.
- Save with the **exact filenames above** (overwrite the placeholders).
