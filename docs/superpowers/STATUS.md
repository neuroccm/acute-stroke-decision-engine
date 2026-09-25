# Project status / handoff

**Last updated:** 2026-09-24, by Claude (Sonnet 5), end of the session that built the whole site.
**Purpose of this file:** read this first when a new coding session picks this project back up. It's a living document — update it (don't just append) when you finish a body of work, so the next session doesn't have to reconstruct context from git log.

## Current state, in one paragraph

The site is built, deployed, and live at **https://stroke.app**, backed by the public repo **github.com/neuroccm/acute-stroke-decision-engine**, branch `main`. Local, GitHub, and the live site are all in sync as of commit `b0dfb8e` (confirmed: `curl https://stroke.app/assets/data/stats.json` matches the local file exactly). Six pages, no framework, no build step. Cloudflare Pages auto-deploys on every push to `main` — usually fast, but has taken up to ~140s once; don't assume instant, but don't over-verify either (see "Workflow notes" below).

## What this project is

A public showcase site for **TypeSafeStroke**, a citation-traced deterministic decision tree for acute ischemic stroke (IV thrombolysis / EVT eligibility), built from the 2026 AHA/ASA guideline, CSBPR 2022 (+ 2025 EVT update), and the Thrombosis Canada guide. The tree's design was inspired by TypeSafe's System One primitives (confirmed directly by Houman). The site also showcases a second, experimental track: whether **Jev** (TypeSafe's System One model) can replicate the tree's decisions when its judgment is decomposed into small sub-questions and synthesized by the real tree engine (95% accurate) vs. asked for the grade directly (42%, not usable).

Styled with CodeStrokeApp's visual identity (dark theme, iOS-blue accent, the actual app icon as favicon/logo). Educational purposes only, explicitly and repeatedly — "no duty of care" banner on every page, disclaimer page, draft-status framing throughout.

## The six pages

| Route | What it is | Source |
| --- | --- | --- |
| `/` | One-page homepage: hero, problem statement, "What this is" (now covers both the tree and the Jev track), how-it-works, live stat strip, CodeStrokeApp tie-in, explore cards, open questions | Hand-authored, `index.html` |
| `/engine/` | The actual interactive decision-tree tool | **Vendored, generated only** — never hand-edit. See below. |
| `/cases/` | 50 clinical test scenarios grouped into 9 clinical themes, cards link into `/engine/?scenario=ID` | Hand-authored page (`cases/index.html`) + generated data (`assets/data/scenarios.json`, `assets/data/case-notes.json` hand-authored) |
| `/disclaimer/` | Terms of use, adapted from Houman's codestroke.net text | Hand-authored, `disclaimer/index.html` |
| `/engine-jev/` | Jev eval methodology + headline numbers + the one confirmed gap | Hand-authored, `engine-jev/index.html` |
| `/cases-jev/` | All 42 Jev-eval cases, tree-vs-Jev verdict per question, drill-down into sub-answers/confidence and guideline sources | Hand-authored page (`cases-jev/index.html`) + generated data (`assets/data/jev-eval.json`) |

All six pages carry the same nav (Home / Decision engine / Case scenarios / Decision Engine Jev / Eval Cases Jev) and the same footer (duty-of-care callout, disclaimer, sources, attribution, SVIN/Mission Thrombectomy thanks, links).

## The two external source projects (not in this repo, not git-tracked)

1. **`~/Downloads/TypeSafeWork/StrokeDecisionTree`** — TypeSafeStroke itself: the Swift decision engine + JS port + `decision_tree.json`/`variables.json`/`recommendations.json` + 50 test scenarios. **This is the canonical copy** — `scripts/sync-decision-tree.sh` reads from here. Current state: 13 modules, 222 nodes, 147 outcomes, 1268-statement citation corpus, 50 scenarios (S01-S50), `tree_version: 2026.09-draft1`.
   - `review/template.html` in that project has been patched **six times** by this project, all small and surgical: `<!doctype html>`+`<meta charset>` (fixed a real mojibake bug), `<meta name="viewport">` (fixed mobile layout), a `?scenario=ID` deep-link hook, the status badge text ("Draft for review" → "Beta"), and two favicon `<link>` tags. **If you're touching this file for something else, check `grep -n 'URLSearchParams\|charset\|viewport\|Beta\|favicon' review/template.html` first** to make sure none of these six patches got lost by whoever/whatever is also editing that project.
2. **`~/Downloads/TypeSafeWorkJev/ClinicalEval`** — the Jev evaluation harness (separate project, separate session originally: "TypeSafeWorkJev"). `scripts/build_jev_eval.py` reads its `results/ischemic_decomposed/_summary.json`, per-case `_raw.json` files, and calls its own `ischemic.decompose_questions.build_eval_set_with_targets()` as a subprocess to get each case's ground-truth outcome ID.
   - **Known gotcha, already handled correctly, but re-check if this ever seems wrong:** `TypeSafeWorkJev/StrokeDecisionTree` is a **separate, independent copy** of StrokeDecisionTree that ClinicalEval's own code uses internally — and it had drifted out of sync (217 nodes vs the canonical 222) at the time this was discovered. `build_jev_eval.py` deliberately gets outcome IDs from ClinicalEval's code (valid regardless of which tree computed them — they're derived from each case's own `expect` list, not by walking a tree) but looks up citation sources/divergence notes in the **canonical** tree, not ClinicalEval's copy. If you rerun this and something's off, check whether the two tree copies have drifted further.

## Timeline / what's been built (chronological, grouped)

1. **Brainstorming → spec → plan → Subagent-Driven Development build** (see `docs/superpowers/specs/2026-09-21-stroke-decision-engine-site-design.md` and `docs/superpowers/plans/2026-09-21-stroke-decision-engine-site.md` for the full original process, ledger, and rulings). Built all 4 original pages, the sync pipeline, CSS/icons/brand assets, the disclaimer page (added mid-build), final whole-branch review, then published to GitHub (`neuroccm/acute-stroke-decision-engine`, public).
2. **Wording revisions:** "type-safe" → "TypeSafe-based", educational-purposes-only language added to descriptions, "hand-authored decision tree" reworded to be less declarative and more grounded ("within the bounded space of the guidelines... not a clinician's judgment").
3. **Favicon replaced** with the real CodeStrokeApp app icon (was a hand-drawn approximation).
4. **Two TypeSafeStroke re-syncs** as the upstream project's code review landed fixes: first 40→50 scenarios (S41-S50 added, mostly regression tests for real bugs the review fixed — blank-field handling, non-integer ASPECTS/mRS, coag-lab/microbleed caution flags), then a second sync when S41-S49's internal "Code review F#:" debug titles got cleaned up to patient-facing names. **Caught and fixed a real bug of our own along the way:** the cases page had five places still hardcoding "40" scenarios after the count changed to 50 — check for stale counts like this after any future re-sync.
5. **Jev integration** (biggest addition after the initial build): two new pages, `scripts/build_jev_eval.py`, nav updated on all pages. Cross-session collaboration with a sibling "TypeSafeWorkJev" session for source content (confirmed via direct message exchange, not guessed).
6. **Deploy troubleshooting:** `stroke.app` was already connected to Cloudflare Pages (discovered mid-session, wasn't obvious from this environment since `wrangler` has never been authenticated here). Two new pages 404'd after their first push despite the homepage and a data file from the same commit deploying fine — turned out to just be a slow build (~140s), not a routing/caching issue as first suspected. If new pages ever 404 right after a push, wait longer before assuming something structural is wrong.
7. **Homepage "What this is" rewritten** to introduce the Jev track with links to all four engine/cases pages, crediting TypeSafe's System One SKILL.md as the tree's actual design inspiration (confirmed directly by Houman, not inferred).
8. **Guideline-source attribution added to `/cases-jev/`:** every verdict now shows which guideline(s) it traces to, with divergence notes surfaced when AHA and CSBPR actually disagree. Required extending `build_jev_eval.py` to cross-reference both external projects (see gotcha above).
9. **Dark mode toggle + full nav added to `/engine/`:** the vendored artifact already had light/dark CSS with no UI control; added the toggle entirely in `scripts/inject_nav.py` (not upstream) since it's site chrome, not a TypeSafeStroke feature. Also replaced the old minimal breadcrumb nav with the same 5-link nav every other page has. Site now defaults to dark for first-time visitors (matches the rest of the site, which has no light mode at all) — an explicit light choice is remembered via `localStorage`.

## Workflow notes for the next session

- **`engine/index.html` is generated only** — never hand-edit it. To change anything about it: either patch `~/Downloads/TypeSafeWork/StrokeDecisionTree/review/template.html` (for TypeSafeStroke's own content/behavior) or `scripts/inject_nav.py` (for site-level chrome — nav, footer, theme toggle), then run `./scripts/sync-decision-tree.sh` and commit the regenerated output.
- **Always verify locally before pushing:** `python3 -m http.server 4173`, then use claude-in-chrome to check the actual page, not just curl status codes — several real bugs (mojibake, missing viewport, stale hardcoded counts) were only caught by looking at the rendered page or the actual response body, not HTTP status alone.
- **After pushing, don't reflexively poll `stroke.app`** to verify the deploy landed — it works reliably now, just sometimes takes a couple of minutes. Houman said as much explicitly mid-session. Only chase it if something seems genuinely broken.
- **Commit any direct edit to a shared file immediately** — don't leave edits (e.g. to a plan doc, or to any file another dispatched agent might also touch) sitting uncommitted in the working tree. This bit us once: an uncommitted footer-text edit got silently clobbered by a subagent's own "confirm nothing unexpected changed" cleanup step before it could be committed.
- **`git commit --allow-empty` is a legitimate way to retrigger a Cloudflare Pages build** if you ever suspect a deploy didn't pick up a change — but confirmed in practice this session that a slow build, not a stuck one, was the actual cause; try waiting first.
- This repo is **not itself the source of truth for the decision tree or the Jev eval** — both external projects (`TypeSafeWork/StrokeDecisionTree`, `TypeSafeWorkJev/ClinicalEval`) are, and this repo only vendors snapshots of them. Houman confirmed this explicitly. Don't treat anything under `assets/data/*.json` or `engine/index.html` as hand-editable; regenerate via the sync scripts instead.

## Known minor issues, not yet fixed (low priority, deferred from the final whole-branch review and since)

- `cases/index.html` has a dead `fetch("/assets/data/stats.json")` whose result is never used.
- Homepage's icon/stats `fetch()` calls have no `.catch()` — a network failure leaves the stat strip stuck on placeholder ellipses rather than degrading gracefully.
- `engine/index.html` still lacks `<html lang="en">` (the other five pages have it) — would need another small `template.html` patch.
- `scripts/inject_nav.py` / `scripts/write_stats.py` don't pass `encoding="utf-8"` explicitly to `Path.read_text()`/`write_text()` — works fine on this machine (UTF-8 locale) but is cheap insurance against a repeat of the earlier charset bug class on a different host.
- `scripts/sync-decision-tree.sh`'s `mktemp` file for the engine build isn't cleaned up if a step fails partway (`trap 'rm -f "$TMP_ENGINE"' EXIT` would fix it).
- Three icons in `assets/icons/` (`icon-arrow-right.svg`, `icon-alert-triangle.svg`, `icon-doc-search.svg`) are unreferenced — kept intentionally for future reuse, not a bug.

## Not yet done / possible next steps

- Hemorrhagic (ICH) stroke module — explicitly out of scope so far, both for the tree and the Jev eval (ClinicalEval's README notes extraction is in progress but `hemorrhagic/questions.py` isn't written yet).
- A live-query mode for Jev (current eval is a static, one-time snapshot; live querying would need a backend proxy since an API key can't live in client-side JS — explicitly flagged as a separate, bigger ask if ever wanted).
- The literature-case candidates ClinicalEval's README mentions are not built into scored vignettes yet.
- No custom favicon/OG-image testing has been done for social share previews.
