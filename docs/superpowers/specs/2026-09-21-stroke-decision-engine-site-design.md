# Hyperacute Stroke Decision Engine — public site design

Status: approved by Houman 2026-09-21. Ready for implementation planning.

## What this is

A new public GitHub repo, deployed on Cloudflare Pages, that showcases the
`TypeSafeStroke` project (`~/Downloads/TypeSafeWork/StrokeDecisionTree`) — a
type-safe, guideline-traced decision engine for acute ischemic stroke — styled
with the visual identity of `CodeStrokeApp`, the iOS app it will eventually
power. The site is a one-page single-scroll homepage plus two supporting
pages: a live, fully rendered copy of the engine, and a case-scenario index
built from the engine's own 40 test cases.

Working name: repo `acute-stroke-decision-engine`, site title "Hyperacute
Stroke Decision Engine."

## Source projects (read-only inputs to this repo)

- **TypeSafeStroke** — `~/Downloads/TypeSafeWork/StrokeDecisionTree`. Not a
  git repo. Contains large source PDFs (AHA, CSBPR, Thrombosis Canada, MeVO)
  that must never be copied into this repo. What we vendor in:
  - `review/build_page.py` + `review/template.html` + `review/engine.js` →
    already produce a self-contained ~435KB HTML artifact (verified working,
    builds clean, 0 unverified citations) with 4 tabs: Case runner, Tree,
    AHA vs CSBPR, Sources and method.
  - `Sources/StrokeDecisionEngine/Resources/{decision_tree.json,
    variables.json, recommendations.json}` — get inlined into the built
    artifact by `build_page.py`, not copied separately.
  - `Tests/StrokeDecisionEngineTests/scenarios.json` — 40 scenarios (`S01`-
    `S40`), each with `id`, `title`, `presets`, `inputs`, `expect`,
    `expect_not`. Source of truth for the case-scenario page.
  - Live figures (2026-09-21, `tree_version: 2026.09-draft1`): 13 modules,
    217 nodes, 142 outcome nodes, 1,268 statements in the full citation
    corpus, 362 of them currently cited by the tree, 40 scenarios.
  - `disclaimer` field in `decision_tree.json`: *"Clinical decision support
    derived from the cited guidelines. It does not replace clinical
    judgement, local protocols, or specialist consultation. Draft pending
    clinical review."* — reuse this verbatim as the canonical disclaimer.

- **CodeStrokeApp** —
  `~/Downloads/Claude_CoWork_Local/app-development/StrokeApp/CodeStrokeApp`.
  Theme source: `CodeStrokeApp/Theme/AppColors.swift` and the app icon
  (`Resources/Assets.xcassets/AppIcon.appiconset/StrokeApp_Full_Stack_Care.png`,
  1024×1024: split blue/red brain silhouette, white caduceus + lightning
  bolt, cyan circuit ring, "CODE STROKE / FULL STACK CARE" wordmark on a
  navy-to-purple radial ground). SF Symbol vocabulary in use across the app:
  `brain.head.profile`, `bolt.heart.fill`, `waveform`, `waveform.badge.
  checkmark`, `shield.checkered`, `checkmark.seal.fill`, `mic.circle.fill`,
  `sparkle`, `wand.and.stars`, `exclamationmark.triangle.fill`, `clock.
  arrow.circlepath`, `camera.viewfinder`, `doc.text.magnifyingglass`.

## Decisions locked in (from brainstorming Q&A)

1. **Repo visibility: public.** Every page carries the draft/decision-support
   disclaimer prominently (hero badge + footer).
2. **Guideline quotes: full verbatim**, same as the local review tool. Code
   is MIT; cited guideline text is reproduced as short, individually
   attributed quotations (source, section, PDF page, grade) for clinical/
   educational purposes — not the source PDFs themselves, which are never
   committed.
3. **Sync mechanism: local script**, not CI. `scripts/sync-decision-tree.sh`
   regenerates the vendored artifact from a local TypeSafeStroke checkout;
   run manually, diffed, committed, pushed.
4. **Case-scenario page: index → live runner.** Cards grouped by clinical
   theme, each linking to `engine/?scenario=S01`, which preloads that
   scenario's real inputs into the actual engine (not a hardcoded summary).

## Repo layout

```
acute-stroke-decision-engine/
├── index.html                     # homepage — one page, single scroll
├── engine/
│   └── index.html                 # vendored TypeSafeStroke artifact (generated, not hand-edited)
├── cases/
│   └── index.html                 # case-scenario index, themed card groups
├── assets/
│   ├── css/site.css                # shared theme: tokens, layout, components
│   ├── icons/                      # hand-built SVG line icons (no CDN/icon-font dependency)
│   ├── img/
│   │   ├── app-icon.png            # copied from CodeStrokeApp AppIcon (nav mark / favicon source)
│   │   └── favicon.svg / apple-touch-icon.png (derived)
│   └── data/
│       ├── stats.json              # {modules, nodes, outcomes, citedStatements, scenarios, treeVersion, generatedAt} — written by sync script, read by homepage
│       ├── scenarios.json          # copied verbatim from TypeSafeStroke (id/title/inputs/expect)
│       └── case-notes.json         # hand-authored: theme grouping + one-line "why this case matters" per scenario id (this repo owns it; sync script does not touch it)
├── scripts/
│   └── sync-decision-tree.sh       # see below
├── _headers                        # Cloudflare Pages response headers (basic security headers)
├── README.md                       # what this is, how to run locally, how to sync, deploy instructions
└── LICENSE                         # MIT (code); README documents the guideline-text attribution separately
```

No JS framework, no build step. Cloudflare Pages serves the repo root
directly. `wrangler.jsonc` is optional — only needed if we want
`wrangler pages dev` for local preview; can add if useful, not required for
deploy (Cloudflare's native GitHub integration handles that once the repo is
connected in the dashboard — a manual one-time step, `wrangler` here isn't
logged into a Cloudflare account).

## Sync script behavior

`scripts/sync-decision-tree.sh [path-to-StrokeDecisionTree]`
(default `~/Downloads/TypeSafeWork/StrokeDecisionTree`):

1. `python3 tools/lint_tree.py <resources>` in the source tree — abort if it
   fails; never publish a broken tree.
2. `python3 review/build_page.py <resources> <scenarios.json> <site>/engine/index.html`.
3. Copy `scenarios.json` to `<site>/assets/data/scenarios.json`.
4. Compute and write `<site>/assets/data/stats.json` (modules/nodes/outcomes/
   cited-statements/scenario counts + `tree_version` + build timestamp) from
   the same source data, so the homepage stat strip can never drift from the
   engine it's describing.
5. Print `git diff --stat` for the touched paths so the changes can be
   reviewed before commit.
6. Does **not** touch `case-notes.json` (hand-authored) or commit/push —
   those stay manual.

## Upstream change to TypeSafeStroke (small, additive)

Add a ~6-line deep-link hook to `review/template.html`'s existing script: on
load, read `?scenario=ID` from `location.search` and call the page's own
`loadScenario(id)` (already exists, used by the scenario `<select>`). This
benefits the local review tool too and flows through the sync script
automatically. This is the only edit made outside the new repo.

## Homepage (`index.html`) — one page, single scroll

1. **Hero** — nav mark (from CodeStrokeApp app icon), project name, one-line
   tagline, draft/disclaimer badge, two CTAs ("Run the decision engine" →
   `/engine/`, "Browse case scenarios" → `/cases/`).
2. **The problem** — stroke guidelines are large, dense, and sometimes
   disagree (AHA vs CSBPR); bedside teams need fast, traceable answers.
3. **What this is** — TypeSafe-driven free-text prefill + a hand-authored,
   citation-linked decision tree; "unknown is never read as no."
4. **How it works** — 4-step visual: free text (EMS handover / history) →
   TypeSafe prefill → typed `PatientState` → `DecisionEngine` (Swift +
   JS, parity-tested) → evidence-linked outcomes with citations.
5. **By the numbers** — stat strip sourced live from `assets/data/stats.json`
   (modules, nodes, outcomes, cited statements, scenarios, tree version).
6. **From CodeStrokeApp to the web** — this is the same engine slated to
   replace `EligibilityEngine.swift` inside CodeStrokeApp; short section
   tying the two projects together visually (dark theme, SF-Symbol-style
   icons).
7. **Explore** — two large cards into `/engine/` and `/cases/`.
8. **Open questions / limitations** — drawn from TypeSafeStroke's README
   ("Open questions for clinical review": Table 8 wording, lab thresholds,
   ASPECTS <6, pediatric EVT, age boundary, post-thrombolysis BP, AF
   anticoagulation timing; explicitly not covering ICH management or CSBPR
   inpatient-complications sections). Keeps the site honest about draft
   status.
9. **Footer** — disclaimer (verbatim from `decision_tree.json`), source
   guideline list with attribution, MIT license note, GitHub link,
   attribution to Dr. Houman Khosravani.

## `/engine/` page

The vendored artifact, verbatim output of `build_page.py`, embedded as-is
(plus the deep-link hook above). A thin site header/footer wraps it for nav
consistency (back to home, link to `/cases/`) without altering its internal
tabs/behavior.

## `/cases/` page — 40 scenarios in 9 clinical themes

Each card: scenario id + title (from `scenarios.json`), one-line "why this
case matters" (from `case-notes.json`), link to `/engine/?scenario=SXX`.

| Theme | Scenarios |
| --- | --- |
| Core pathway & absolute exclusions | S01, S02, S04, S33, S34 |
| Imaging & core-size edge cases | S05, S06, S07, S08, S09, S10 |
| Vessel & anatomy nuance | S11, S12, S13, S32 |
| Baseline function & special populations | S14, S15, S16, S17, S39 |
| Anticoagulation, labs & recent-procedure risk | S03, S18, S21 |
| Blood pressure | S19, S20, S37 |
| Incomplete information | S22, S35, S36 |
| Post-treatment complications | S23, S24, S28, S29 |
| Downstream care & systems | S25, S26, S27, S30, S31, S38, S40 |

(Full 40-entry title + one-line blurb mapping is authored directly into
`case-notes.json` during implementation; themes above are final.)

## Visual theme

- Palette (from `AppColors.swift`): background `#0D0D0D`, surfaces `#1A1A1A`/
  `#2A2A2A`, accent `#007AFF`, status green `#34C759` / yellow `#FFD60A` /
  red `#FF3B30`, Code Stroke red `#CC0000`. Hero uses a navy→purple radial
  gradient echoing the app icon's background.
- Typography: reuse IBM Plex Sans / Sans Condensed / Mono (already loaded by
  the vendored `/engine/` page) across all three pages for one consistent
  system, rather than introducing a second type family.
- Icons: hand-built SVG line icons (~1.5px stroke, rounded caps) mirroring
  the SF Symbols listed above — no external icon font/CDN, keeping the site
  dependency-free like `engine.js`.
- Logo: the CodeStrokeApp app-icon PNG reused directly for favicon / nav
  mark (small scale); homepage hero does not re-draw it larger than a nav
  mark to avoid a blurry raster hero.

## Deployment

Static site, no build command; Cloudflare Pages root = `/`. `wrangler` here
isn't authenticated to a Cloudflare account, so the one-time "connect this
GitHub repo in the Cloudflare Pages dashboard" step is manual (documented in
README). Repo push to GitHub (`neuroccm` account, `gh` authenticated) happens
only after explicit go-ahead, since creating a public repo and pushing is a
visible, hard-to-reverse action.

## Out of scope for this pass

- CI-based auto-sync from a second TypeSafeStroke repo (deferred; local
  script chosen).
- Custom domain configuration (default `*.pages.dev` for now).
- Editing `EligibilityEngine.swift` / actually integrating the Swift package
  into CodeStrokeApp (mentioned as future context only).
