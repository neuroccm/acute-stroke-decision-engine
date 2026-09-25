# Hyperacute Stroke Decision Engine

(hot on the release of TypeSafe) A TypeSafe-based, citation-traced decision engine for acute ischemic stroke,
built from the 2026 AHA/ASA guideline, CSBPR 2022 (+ 2025 EVT update), and
the Thrombosis Canada guide. For educational purposes only currently. This
repo is the public site for the TypeSafeStroke decision tree (a local
project, not yet on GitHub) that also runs inside CodeStrokeApp.

**Status: draft, pending clinical review. Decision support, not orders.**
**Last updated:** 2026-09-24.

Picking this project back up in a new session? Read
[`docs/superpowers/STATUS.md`](docs/superpowers/STATUS.md) first.

## Structure

- `index.html` — one-page overview.
- `engine/index.html` — the live decision engine. **Generated only** by
  `scripts/sync-decision-tree.sh` — never hand-edit this file.
- `cases/index.html` — 50 clinical test scenarios grouped by theme, each
  linking into the live engine with real inputs preloaded.
- `disclaimer/index.html` — terms of use and disclaimer (no duty of care,
  educational purpose only, no real patient data, source attribution).
- `engine-jev/index.html` — experimental: Jev (TypeSafe System One)
  decomposed-judgment eval vs. this engine, static snapshot, methodology
  and headline numbers.
- `cases-jev/index.html` — the 42 eval cases behind that page, tree vs.
  Jev verdict per case with a confidence drill-down.
- `assets/` — shared CSS, hand-built icons, brand assets, and the JSON data
  (`scenarios.json`, `stats.json`, `jev-eval.json` generated; `case-notes.json`
  hand-authored here).
- `scripts/sync-decision-tree.sh` — rebuilds `engine/index.html` and the
  generated JSON from a local TypeSafeStroke checkout.
- `scripts/build_jev_eval.py` — one-time snapshot builder for
  `jev-eval.json` from a local TypeSafeWorkJev/ClinicalEval checkout.

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

Connected to Cloudflare Pages, live at [stroke.app](https://stroke.app).
Build command: none. Build output directory: `/` (repo root). Every push to
`main` deploys automatically.

To connect a fresh clone of this repo instead: Cloudflare dashboard →
Workers & Pages → Create → Pages → Connect to Git → select this repository,
same build settings as above. Alternatively, from the CLI: `wrangler login`,
then `wrangler pages deploy . --project-name=acute-stroke-decision-engine`.

## License and attribution

Code is MIT-licensed (see `LICENSE`). Cited guideline text throughout
`engine/index.html` is reproduced as short, individually attributed
quotations — each with source, section, page, and grade — from the 2026
AHA/ASA Acute Ischemic Stroke Guideline, CSBPR Acute Stroke Management 2022,
the CSBPR EVT Interim Update 2025, and the Thrombosis Canada IVT/EVT Guide,
for clinical and educational use. The source PDFs themselves are not
included in this repo.
