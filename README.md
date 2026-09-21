# Hyperacute Stroke Decision Engine

(hot on the release of TypeSafe) A TypeSafe-based, citation-traced decision engine for acute ischemic stroke,
built from the 2026 AHA/ASA guideline, CSBPR 2022 (+ 2025 EVT update), and
the Thrombosis Canada guide. For educational purposes only currently. This
repo is the public site for the [TypeSafeStroke](https://github.com/neuroccm)
decision tree that also runs inside CodeStrokeApp.

**Status: draft, pending clinical review. Decision support, not orders.**

## Structure

- `index.html` — one-page overview.
- `engine/index.html` — the live decision engine. **Generated only** by
  `scripts/sync-decision-tree.sh` — never hand-edit this file.
- `cases/index.html` — 40 clinical test scenarios grouped by theme, each
  linking into the live engine with real inputs preloaded.
- `disclaimer/index.html` — terms of use and disclaimer (no duty of care,
  educational purpose only, no real patient data, source attribution).
- `assets/` — shared CSS, hand-built icons, brand assets, and the JSON data
  (`scenarios.json`, `stats.json` generated; `case-notes.json` hand-authored
  here).
- `scripts/sync-decision-tree.sh` — rebuilds `engine/index.html` and the
  generated JSON from a local TypeSafeStroke checkout.

No build step, no JS framework — Cloudflare Pages serves the repo root
directly.

## Local preview

```sh
python3 -m http.server 4173
```

Then open `http://localhost:4173/`.

## Keeping the engine in sync

The decision tree itself lives in a separate, private checkout at
`~/Downloads/TypeSafeWork/StrokeDecisionTree` (not this repo — it contains
large source PDFs that must never be committed here). After editing the
tree there:

```sh
./scripts/sync-decision-tree.sh [path-to-StrokeDecisionTree]
```

This lints the tree, rebuilds `engine/index.html`, and refreshes
`assets/data/scenarios.json` and `assets/data/stats.json`. Review the diff,
then commit and push — Cloudflare Pages deploys automatically on push to
`main`.

## Deploying

This repo has no Cloudflare Pages project connected yet. One-time setup:

1. In the Cloudflare dashboard, go to Workers & Pages → Create → Pages →
   Connect to Git, and select this repository.
2. Build command: none. Build output directory: `/` (repo root).
3. Every push to `main` deploys automatically after that.

Alternatively, from the CLI: `wrangler login`, then
`wrangler pages deploy . --project-name=acute-stroke-decision-engine`.

## License and attribution

Code is MIT-licensed (see `LICENSE`). Cited guideline text throughout
`engine/index.html` is reproduced as short, individually attributed
quotations — each with source, section, page, and grade — from the 2026
AHA/ASA Acute Ischemic Stroke Guideline, CSBPR Acute Stroke Management 2022,
the CSBPR EVT Interim Update 2025, and the Thrombosis Canada IVT/EVT Guide,
for clinical and educational use. The source PDFs themselves are not
included in this repo.
