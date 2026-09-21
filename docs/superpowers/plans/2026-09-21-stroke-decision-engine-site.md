# Hyperacute Stroke Decision Engine Site — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and (with explicit go-ahead) publish a public static site — one-page homepage, `/engine/` (the live TypeSafeStroke decision engine artifact), `/cases/` (40 clinical scenarios as a themed index into the live engine) — styled with CodeStrokeApp's dark/iOS theme and icon language, deployable to Cloudflare Pages with no build step.

**Architecture:** Pure static HTML/CSS/vanilla JS, no framework, no build tool. A shell+Python sync script vendors the TypeSafeStroke engine artifact and its scenario/stat data into this repo on demand; the homepage and cases page render from that vendored JSON client-side. A tiny upstream patch to TypeSafeStroke's own page generator adds `?scenario=ID` deep-linking.

**Tech Stack:** HTML5, CSS (custom properties, no preprocessor), vanilla JS (`fetch`, no bundler), Python 3 (sync/build scripts, matches TypeSafeStroke's own tooling), Bash (sync entrypoint), Google Fonts CDN (IBM Plex family — already used by the vendored engine page, reused here for one consistent type system).

**Spec:** `docs/superpowers/specs/2026-09-21-stroke-decision-engine-site-design.md`

## Global Constraints

- No JS framework, no build step, no npm dependency — Cloudflare Pages serves the repo root as-is.
- Never commit anything from `~/Downloads/TypeSafeWork/StrokeDecisionTree` except what the sync script explicitly copies (`engine/index.html`, `assets/data/scenarios.json`, `assets/data/stats.json`). Never commit the source PDFs.
- `engine/index.html` is **generated only** by `scripts/sync-decision-tree.sh` — never hand-edit it. If it needs to look different, change `scripts/inject_nav.py` or the upstream `template.html`, then re-run the sync script.
- Guideline citation text is reproduced in full verbatim (per spec decision 2) — this is unchanged, inherited as-is from the vendored artifact; no task in this plan touches citation text.
- Every page (`/`, `/engine/`, `/cases/`) must surface the disclaimer: *"Clinical decision support derived from the cited guidelines. It does not replace clinical judgement, local protocols, or specialist consultation. Draft pending clinical review."* (verbatim, from `decision_tree.json`'s `disclaimer` field).
- Repo name: `acute-stroke-decision-engine`. GitHub account: `neuroccm` (already `gh`-authenticated in this environment).
- Color tokens come from `CodeStrokeApp/Theme/AppColors.swift`; typography reuses IBM Plex Sans / Sans Condensed / Mono (already loaded by the vendored engine page) across all three pages.
- Task 12 (publish to GitHub) is a hard stop: do not run it without an explicit, separate go-ahead from Houman, even if earlier tasks were approved.

---

## Task 1: Repo scaffolding

**Files:**
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `_headers`

**Interfaces:**
- Produces: baseline repo files every later task assumes exist (git already initialized at repo root with the spec committed as the first commit).

- [ ] **Step 1: Write `.gitignore`**

```
.DS_Store
*.log
.wrangler/
```

- [ ] **Step 2: Write `LICENSE` (MIT, code only — guideline text attribution lives in README, Task 10)**

```
MIT License

Copyright (c) 2026 Houman Khosravani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Write `_headers` (Cloudflare Pages response headers)**

```
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
```

- [ ] **Step 4: Verify and commit**

Run: `git status --short` — expect `.gitignore`, `LICENSE`, `_headers` as untracked.

```bash
git add .gitignore LICENSE _headers
git commit -m "Add repo scaffolding: license, gitignore, security headers"
```

---

## Task 2: Design tokens & shared CSS

**Files:**
- Create: `assets/css/site.css`

**Interfaces:**
- Produces (consumed by Tasks 8, 9): CSS custom properties (`--bg`, `--surface-1`, `--surface-2`, `--surface-3`, `--accent`, `--green`, `--yellow`, `--red`, `--code-red`, `--text-1`, `--text-2`, `--text-3`, `--rule`, `--hero-grad-1`, `--hero-grad-2`, `--sans`, `--cond`, `--mono`, `--radius`, `--shadow`) and component classes: `.topnav`, `.topnav__mark`, `.topnav__title`, `.topnav__links`, `.wrap`, `.section`, `.section--tight`, `.eyebrow`, `.lede`, `.badge--disclaimer`, `.btn`, `.btn--primary`, `.btn--ghost`, `.stat-strip`, `.stat`, `.step-grid`, `.step`, `.step__icon`, `.card-grid`, `.card`, `.card__meta`, `.site-footer`, `.hero`.

- [ ] **Step 1: Write `assets/css/site.css`**

```css
/* Hyperacute Stroke Decision Engine — shared site theme
   Palette from CodeStrokeApp/Theme/AppColors.swift. Typography matches
   the vendored TypeSafeStroke engine page (IBM Plex family) for one
   consistent system across / , /engine/ , /cases/ . */

:root {
  --bg: #0d0d0d;
  --surface-1: #1a1a1a;
  --surface-2: #2a2a2a;
  --surface-3: #3a3a3a;
  --accent: #007aff;
  --green: #34c759;
  --yellow: #ffd60a;
  --red: #ff3b30;
  --code-red: #cc0000;
  --text-1: #ffffff;
  --text-2: #aaaaaa;
  --text-3: #666666;
  --rule: #2a2a2a;
  --hero-grad-1: #0b1330;
  --hero-grad-2: #1c1440;
  --sans: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --cond: "IBM Plex Sans Condensed", "Arial Narrow", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
  --radius: 12px;
  --shadow: 0 1px 2px rgba(0, 0, 0, .4), 0 8px 24px rgba(0, 0, 0, .35);
  --maxw: 1100px;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text-1);
  font: 15px/1.6 var(--sans);
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); }
img { max-width: 100%; display: block; }
h1, h2, h3 { font-family: var(--cond); font-weight: 700; letter-spacing: -.01em; text-wrap: balance; margin: 0; }
p { margin: 0; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }

.wrap { max-width: var(--maxw); margin: 0 auto; padding-inline: 20px; }

/* Top navigation */
.topnav {
  position: sticky; top: 0; z-index: 30;
  display: flex; align-items: center; gap: 12px;
  padding: 14px max(20px, calc((100vw - var(--maxw)) / 2));
  background: rgba(13, 13, 13, .86);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--rule);
}
.topnav__mark { width: 28px; height: 28px; border-radius: 7px; }
.topnav__title { font: 600 14px/1 var(--cond); letter-spacing: .01em; color: var(--text-1); text-decoration: none; }
.topnav__links { margin-left: auto; display: flex; gap: 22px; font: 600 13px/1 var(--cond); letter-spacing: .02em; }
.topnav__links a { color: var(--text-2); text-decoration: none; }
.topnav__links a:hover, .topnav__links a[aria-current="page"] { color: var(--text-1); }

/* Sections */
.section { padding: 72px 0; border-top: 1px solid var(--rule); }
.section:first-of-type { border-top: 0; }
.section--tight { padding: 40px 0; }
.eyebrow {
  display: inline-block; font: 600 11px/1 var(--cond); letter-spacing: .14em;
  text-transform: uppercase; color: var(--accent); margin-bottom: 10px;
}
.lede { color: var(--text-2); max-width: 68ch; font-size: 16px; margin-top: 14px; }

/* Hero */
.hero {
  padding: 96px 0 72px;
  background:
    radial-gradient(1100px 520px at 15% -10%, var(--hero-grad-2), transparent 60%),
    radial-gradient(900px 520px at 100% 0%, var(--hero-grad-1), transparent 55%),
    var(--bg);
}
.hero h1 { font-size: clamp(34px, 5vw, 56px); max-width: 16ch; }
.hero__row { display: flex; align-items: center; gap: 14px; margin-bottom: 18px; }
.hero__mark { width: 44px; height: 44px; border-radius: 10px; }
.hero__actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 30px; }

.badge--disclaimer {
  display: inline-flex; align-items: center; gap: 8px;
  font: 600 11px/1 var(--cond); letter-spacing: .06em; text-transform: uppercase;
  color: var(--yellow); border: 1px solid currentColor; border-radius: 999px;
  padding: 7px 12px; margin-top: 28px;
}

/* Buttons */
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  font: 600 14px/1 var(--cond); letter-spacing: .02em;
  padding: 13px 20px; border-radius: 999px; text-decoration: none;
  border: 1px solid transparent; cursor: pointer;
}
.btn--primary { background: var(--accent); color: #fff; }
.btn--primary:hover { background: #1a86ff; }
.btn--ghost { background: var(--surface-1); color: var(--text-1); border-color: var(--surface-3); }
.btn--ghost:hover { border-color: var(--text-2); }
.btn svg { width: 16px; height: 16px; }

/* Stat strip */
.stat-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 18px; margin-top: 8px; }
.stat { background: var(--surface-1); border: 1px solid var(--rule); border-radius: var(--radius); padding: 18px; }
.stat b { display: block; font: 700 30px/1 var(--cond); color: var(--text-1); }
.stat span { display: block; margin-top: 6px; font: 500 12px/1.3 var(--sans); color: var(--text-2); }

/* Step grid ("how it works") */
.step-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-top: 32px; }
.step { background: var(--surface-1); border: 1px solid var(--rule); border-radius: var(--radius); padding: 22px; }
.step__icon {
  width: 40px; height: 40px; border-radius: 10px; background: var(--surface-2);
  display: flex; align-items: center; justify-content: center; color: var(--accent); margin-bottom: 16px;
}
.step__icon svg { width: 20px; height: 20px; }
.step h3 { font-size: 16px; margin-bottom: 8px; }
.step p { color: var(--text-2); font-size: 13.5px; }

/* Card grid (explore cards, case scenario cards) */
.card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-top: 18px; }
.card {
  display: block; background: var(--surface-1); border: 1px solid var(--rule); border-radius: var(--radius);
  padding: 20px; text-decoration: none; color: inherit; box-shadow: var(--shadow); transition: border-color .15s ease;
}
.card:hover { border-color: var(--accent); }
.card h3 { font-size: 16px; margin-bottom: 6px; }
.card p { color: var(--text-2); font-size: 13.5px; }
.card__meta { display: block; font: 600 11px/1 var(--mono); letter-spacing: .04em; color: var(--accent); margin-bottom: 10px; text-transform: uppercase; }

/* Footer */
.site-footer { padding: 48px 0 64px; border-top: 1px solid var(--rule); color: var(--text-2); font-size: 13px; }
.site-footer .disclaimer { color: var(--yellow); font-weight: 600; max-width: 70ch; margin-bottom: 16px; }
.site-footer .links { display: flex; flex-wrap: wrap; gap: 18px; margin-top: 18px; font: 600 12px/1 var(--cond); }
.site-footer .links a { color: var(--text-2); text-decoration: none; }
.site-footer .links a:hover { color: var(--text-1); }

@media (max-width: 640px) {
  .topnav__links { gap: 14px; }
  .hero { padding: 64px 0 48px; }
  .section { padding: 48px 0; }
}
```

- [ ] **Step 2: Verify visually**

Copy the file to the session scratchpad as a throwaway preview (`<scratchpad>/css-preview.html`) with a `<link rel="stylesheet" href="site.css">` and one instance of each component class (`.topnav`, `.hero` with `.badge--disclaimer` and two `.btn`, a `.stat-strip` with 3 `.stat`, a `.step-grid` with 2 `.step`, a `.card-grid` with 2 `.card`). Serve with `python3 -m http.server 4173` from the scratchpad dir, open in Chrome via `claude-in-chrome`, screenshot, confirm dark theme renders, sticky nav blurs on scroll, buttons/cards have visible hover affordance. Delete the scratch preview when done — it is not part of the repo.

- [ ] **Step 3: Commit**

```bash
git add assets/css/site.css
git commit -m "Add shared design tokens and component CSS"
```

---

## Task 3: Icon set

**Files:**
- Create: `assets/icons/icon-mic.svg`
- Create: `assets/icons/icon-brain.svg`
- Create: `assets/icons/icon-cpu.svg`
- Create: `assets/icons/icon-check-seal.svg`
- Create: `assets/icons/icon-waveform.svg`
- Create: `assets/icons/icon-shield.svg`
- Create: `assets/icons/icon-clock.svg`
- Create: `assets/icons/icon-arrow-right.svg`
- Create: `assets/icons/icon-alert-triangle.svg`
- Create: `assets/icons/icon-doc-search.svg`

**Interfaces:**
- Produces (consumed by Task 9): 10 inline-able SVG files, each `viewBox="0 0 24 24"`, `stroke="currentColor"`, `fill="none"`, so they inherit CSS `color` wherever embedded.

Each file follows the same shape: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">...</svg>`. Mirrors the SF Symbols CodeStrokeApp uses (`mic.circle.fill`, `brain.head.profile`, typed-state, `checkmark.seal.fill`, `waveform`, `shield.checkered`, `clock.arrow.circlepath`, arrow, `exclamationmark.triangle.fill`, `doc.text.magnifyingglass`) as simple line icons.

- [ ] **Step 1: Write `assets/icons/icon-mic.svg`** (free-text / dictation input)

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <rect x="9" y="3" width="6" height="11" rx="3"/>
  <path d="M5 11a7 7 0 0 0 14 0"/>
  <path d="M12 18v3"/>
  <path d="M8.5 21h7"/>
</svg>
```

- [ ] **Step 2: Write `assets/icons/icon-brain.svg`** (clinical reasoning / the tree)

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3.2 3.2 0 0 0 2 5.8V19a2 2 0 0 0 2 2h2V4z"/>
  <path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3.2 3.2 0 0 1-2 5.8V19a2 2 0 0 1-2 2h-2V4z"/>
  <path d="M9 8h2m-2 4h2m-2 4h2m2-8h2m-2 4h2m-2 4h2"/>
</svg>
```

- [ ] **Step 3: Write `assets/icons/icon-cpu.svg`** (typed `PatientState`)

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <rect x="6" y="6" width="12" height="12" rx="2"/>
  <rect x="9.5" y="9.5" width="5" height="5" rx="1"/>
  <path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>
</svg>
```

- [ ] **Step 4: Write `assets/icons/icon-check-seal.svg`** (verified citation / evidence-linked outcome)

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3l2.2 1.3 2.5-.3 1.1 2.3 2.3 1.1-.3 2.5L21 12l-1.3 2.2.3 2.5-2.3 1.1-1.1 2.3-2.5-.3L12 21l-2.2-1.3-2.5.3-1.1-2.3-2.3-1.1.3-2.5L3 12l1.3-2.2-.3-2.5 2.3-1.1 1.1-2.3 2.5.3L12 3z"/>
  <path d="M9 12l2 2 4-4"/>
</svg>
```

- [ ] **Step 5: Write `assets/icons/icon-waveform.svg`** (dual-engine parity: Swift + JS)

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 12h2l2-7 3 14 3-11 2 4h5"/>
</svg>
```

- [ ] **Step 6: Write `assets/icons/icon-shield.svg`** ("unknown is never no" / safety)

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z"/>
  <path d="M9.5 12l2 2 3.5-4"/>
</svg>
```

- [ ] **Step 7: Write `assets/icons/icon-clock.svg`** (draft status / time-critical)

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="8.5"/>
  <path d="M12 7.5V12l3 2"/>
</svg>
```

- [ ] **Step 8: Write `assets/icons/icon-arrow-right.svg`** (CTAs)

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 12h15"/>
  <path d="M13 6l6 6-6 6"/>
</svg>
```

- [ ] **Step 9: Write `assets/icons/icon-alert-triangle.svg`** (open questions / limitations)

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 4l9.5 16H2.5L12 4z"/>
  <path d="M12 10v4"/>
  <path d="M12 17.5h.01"/>
</svg>
```

- [ ] **Step 10: Write `assets/icons/icon-doc-search.svg`** (sources & citations)

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
  <path d="M7 3h7l4 4v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/>
  <path d="M14 3v4h4"/>
  <circle cx="10.5" cy="14.5" r="2.5"/>
  <path d="M12.3 16.3L14 18"/>
</svg>
```

- [ ] **Step 11: Verify all 10 parse as valid SVG**

Run: `for f in assets/icons/*.svg; do xmllint --noout "$f" || echo "BAD: $f"; done`
Expected: no "BAD" lines printed. (`xmllint` ships with macOS; it only checks well-formedness of files authored in this task, not untrusted input.)

- [ ] **Step 12: Commit**

```bash
git add assets/icons
git commit -m "Add hand-built line icon set matching CodeStrokeApp's SF Symbol vocabulary"
```

---

## Task 4: Brand assets (favicon / nav mark)

**Files:**
- Create: `assets/img/app-icon.png` (copy of CodeStrokeApp's app icon)
- Create: `assets/img/favicon.svg`

**Interfaces:**
- Produces (consumed by Tasks 6, 8, 9): `/assets/img/app-icon.png` used as the nav mark on all pages and the injected engine breadcrumb; `/assets/img/favicon.svg` referenced from every page's `<head>`.

- [ ] **Step 1: Copy the app icon**

```bash
cp "/Users/houman/Downloads/Claude_CoWork_Local/app-development/StrokeApp/CodeStrokeApp/CodeStrokeApp/Resources/Assets.xcassets/AppIcon.appiconset/StrokeApp_Full_Stack_Care.png" assets/img/app-icon.png
```

- [ ] **Step 2: Write a simple monogram `assets/img/favicon.svg`** (matches the dark/blue palette; browsers render SVG favicons at any size, no build step needed)

```svg
<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
  <rect width="32" height="32" rx="7" fill="#0d1b4c"/>
  <path d="M16 6c-5 0-9 4-9 9 0 4 2.6 7.4 6.3 8.7L16 26l2.7-2.3C22.4 22.4 25 19 25 15c0-5-4-9-9-9z" fill="none" stroke="#4fc3ff" stroke-width="1.4"/>
  <path d="M16 9l-3 7h2.4l-1 6 4.6-8h-2.6l1-5z" fill="#ffffff"/>
</svg>
```

- [ ] **Step 3: Verify**

Run: `file assets/img/app-icon.png` — expect `PNG image data, 1024 x 1024`.
Run: `xmllint --noout assets/img/favicon.svg` — expect no error.

- [ ] **Step 4: Commit**

```bash
git add assets/img/app-icon.png assets/img/favicon.svg
git commit -m "Add brand assets: CodeStrokeApp icon and site favicon"
```

---

## Task 5: Upstream deep-link patch to TypeSafeStroke

**Files:**
- Modify: `/Users/houman/Downloads/TypeSafeWork/StrokeDecisionTree/review/template.html` (outside this repo — TypeSafeStroke has no git of its own; this is a plain file edit)

**Interfaces:**
- Produces: the vendored engine artifact (built in Task 6) responds to `?scenario=ID` in its URL by preloading that scenario, using the page's own existing `loadScenario(id)` function. No new interface surface — purely additive behavior on an existing function.

- [ ] **Step 1: Confirm the anchor is unique before editing**

Run: `grep -c 'loadScenario("S01");' /Users/houman/Downloads/TypeSafeWork/StrokeDecisionTree/review/template.html`
Expected: `1`

- [ ] **Step 2: Apply the patch**

In `/Users/houman/Downloads/TypeSafeWork/StrokeDecisionTree/review/template.html`, find the end of the page's inline `<script>` block:

```js
  loadScenario("S01");
})();
```

Replace with:

```js
  const params = new URLSearchParams(location.search);
  loadScenario(params.get("scenario") || "S01");
})();
```

- [ ] **Step 3: Verify the tree still builds clean**

```bash
cd /Users/houman/Downloads/TypeSafeWork/StrokeDecisionTree
python3 review/build_page.py Sources/StrokeDecisionEngine/Resources Tests/StrokeDecisionEngineTests/scenarios.json /tmp/patch_check.html
grep -c 'URLSearchParams' /tmp/patch_check.html
rm /tmp/patch_check.html
```
Expected: build succeeds with no error, `grep` prints `1`.

- [ ] **Step 4: No commit here** — TypeSafeStroke is not a git repo; this file edit is picked up automatically the next time Task 6's sync script runs. Note it in the site repo's own commit for Task 6 so the dependency is documented.

---

## Task 6: Sync script (build the engine artifact into this repo)

**Files:**
- Create: `scripts/sync-decision-tree.sh`
- Create: `scripts/inject_nav.py`
- Create: `scripts/write_stats.py`
- Create (generated, first real run of this task): `engine/index.html`
- Create (generated): `assets/data/scenarios.json`
- Create (generated): `assets/data/stats.json`

**Interfaces:**
- Consumes: Task 5's patched `template.html`; `assets/img/app-icon.png` (Task 4) for the injected breadcrumb image path `/assets/img/app-icon.png`.
- Produces (consumed by Tasks 8, 9): `assets/data/scenarios.json` — same shape as TypeSafeStroke's own file: `{"presets": {...}, "scenarios": [{"id": "S01", "title": "...", "presets": [...], "inputs": {...}, "expect": [...], "expect_not": [...]}, ...]}`. `assets/data/stats.json` — `{"modules": int, "nodes": int, "outcomes": int, "citedStatements": int, "corpusStatements": int, "scenarios": int, "treeVersion": string, "generatedAt": ISO8601 string}`. `engine/index.html` — the full interactive tool at route `/engine/`, reachable with `?scenario=SXX`.

- [ ] **Step 1: Write `scripts/inject_nav.py`**

```python
#!/usr/bin/env python3
"""Wrap the vendored TypeSafeStroke artifact with this site's navigation.
The artifact's own CSS custom properties (--rule, --muted, --cond, --accent,
--ink) are reused so no extra stylesheet is loaded on this page.

Usage: inject_nav.py <built.html> <out.html>
"""
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
html = src.read_text()

EXTRA_CSS = """
.site-crumbs { display:flex; align-items:center; gap:10px; padding-bottom:14px; margin-bottom:14px; border-bottom:1px solid var(--rule); font:600 12px/1 var(--cond); }
.site-crumbs img { border-radius:6px; display:block; }
.site-crumbs a { color: var(--muted); text-decoration:none; }
.site-crumbs a:hover { color: var(--accent); }
.site-crumbs .sep { color: var(--rule); }
.site-crumbs .current { color: var(--ink); }
.site-foot-links { display:flex; gap:16px; padding-top:14px; margin-top:18px; border-top:1px solid var(--rule); font:600 12px/1 var(--cond); }
.site-foot-links a { color: var(--muted); text-decoration:none; }
.site-foot-links a:hover { color: var(--accent); }
"""

NAV_HTML = """<div class="site-crumbs">
  <img src="/assets/img/app-icon.png" alt="" width="22" height="22">
  <a href="/">Hyperacute Stroke Decision Engine</a>
  <span class="sep">/</span>
  <span class="current">Decision engine</span>
  <a href="/cases/" style="margin-left:auto">Case scenarios &rarr;</a>
</div>
"""

SUBFOOTER_HTML = """<div class="site-foot-links">
  <a href="/">&larr; Back to overview</a>
  <a href="/cases/">Case scenarios</a>
  <a href="https://github.com/neuroccm/acute-stroke-decision-engine">Source on GitHub</a>
</div>
"""


def replace_once(html, needle, insert, insert_before=False):
    assert html.count(needle) == 1, f"anchor not unique, template.html shape changed: {needle!r}"
    idx = html.index(needle)
    if insert_before:
        return html[:idx] + insert + html[idx:]
    end = idx + len(needle)
    return html[:end] + insert + html[end:]


html = replace_once(html, "</style>", EXTRA_CSS, insert_before=True)
html = replace_once(html, '<div class="wrap">', NAV_HTML)
html = replace_once(html, '<footer id="disclaimer"></footer>', SUBFOOTER_HTML)

out.write_text(html)
print(f"{out} written, {len(html) // 1024} KB")
```

- [ ] **Step 2: Write `scripts/write_stats.py`**

```python
#!/usr/bin/env python3
"""Compute assets/data/stats.json for the homepage stat strip, so the
numbers on the marketing site can never drift from the engine they
describe. Mirrors the citation-walk in TypeSafeStroke's review/build_page.py.

Usage: write_stats.py <resources_dir> <scenarios.json> <out.json>
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

res, scen_path, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
tree = json.loads((res / "decision_tree.json").read_text())
corpus = json.loads((res / "recommendations.json").read_text())
scenarios = json.loads(scen_path.read_text())["scenarios"]

cited = set()


def walk(o):
    if isinstance(o, dict):
        cited.update(o.get("rec_ids", []))
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(tree)

nodes = sum(len(m["nodes"]) for m in tree["modules"])
outcomes = sum(
    1 for m in tree["modules"] for n in m["nodes"].values()
    if n.get("type") not in ("decision", "screen")
)

stats = {
    "modules": len(tree["modules"]),
    "nodes": nodes,
    "outcomes": outcomes,
    "citedStatements": len(cited),
    "corpusStatements": len(corpus),
    "scenarios": len(scenarios),
    "treeVersion": tree["tree_version"],
    "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
out.write_text(json.dumps(stats, indent=2) + "\n")
print(json.dumps(stats, indent=2))
```

- [ ] **Step 3: Write `scripts/sync-decision-tree.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

SRC="${1:-$HOME/Downloads/TypeSafeWork/StrokeDecisionTree}"
SITE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RES="$SRC/Sources/StrokeDecisionEngine/Resources"
SCEN="$SRC/Tests/StrokeDecisionEngineTests/scenarios.json"

if [ ! -d "$SRC" ]; then
  echo "error: TypeSafeStroke checkout not found at $SRC" >&2
  exit 1
fi

echo "==> Linting decision tree"
python3 "$SRC/tools/lint_tree.py" "$RES/decision_tree.json" "$RES/variables.json" "$RES/recommendations.json"

echo "==> Building engine artifact"
TMP_ENGINE="$(mktemp)"
python3 "$SRC/review/build_page.py" "$RES" "$SCEN" "$TMP_ENGINE"

echo "==> Injecting site navigation"
mkdir -p "$SITE_DIR/engine"
python3 "$SITE_DIR/scripts/inject_nav.py" "$TMP_ENGINE" "$SITE_DIR/engine/index.html"
rm -f "$TMP_ENGINE"

echo "==> Copying scenario data"
mkdir -p "$SITE_DIR/assets/data"
cp "$SCEN" "$SITE_DIR/assets/data/scenarios.json"

echo "==> Writing stats.json"
python3 "$SITE_DIR/scripts/write_stats.py" "$RES" "$SCEN" "$SITE_DIR/assets/data/stats.json"

echo "==> Done. Review changes before committing:"
git -C "$SITE_DIR" diff --stat -- engine/index.html assets/data/scenarios.json assets/data/stats.json || true
```

- [ ] **Step 4: Make it executable and run it for real**

```bash
chmod +x scripts/sync-decision-tree.sh
./scripts/sync-decision-tree.sh
```
Expected: prints lint success, "engine/index.html written, ~4XX KB", `assets/data/stats.json` printed with `modules: 13, nodes: 217, outcomes: 142, scenarios: 40`.

- [ ] **Step 5: Verify the deep-link hook actually works in a browser**

```bash
python3 -m http.server 4173 &
SERVER_PID=$!
```
Use `claude-in-chrome` to navigate to `http://localhost:4173/engine/?scenario=S16`. Confirm: the "Load a test case" dropdown shows `S16 · 10-year-old with M1 at 3 h` selected, and the plan panel reflects that scenario's inputs (age 10). Also confirm the injected breadcrumb ("Hyperacute Stroke Decision Engine / Decision engine ... Case scenarios →") renders above the header, and the "← Back to overview" / "Case scenarios" / "Source on GitHub" links render below the footer disclaimer. Check console via `read_console_messages` for errors — expect none.
Then: `kill $SERVER_PID`.

- [ ] **Step 6: Validate `assets/data/stats.json` and `scenarios.json` structurally**

Run:
```bash
python3 -c "
import json
s = json.load(open('assets/data/stats.json'))
assert s['modules'] == 13 and s['nodes'] == 217 and s['outcomes'] == 142 and s['scenarios'] == 40, s
sc = json.load(open('assets/data/scenarios.json'))
assert len(sc['scenarios']) == 40
ids = {x['id'] for x in sc['scenarios']}
assert ids == {f'S{i:02d}' for i in range(1, 41)}, sorted(ids)
print('OK')
"
```
Expected: `OK`.

- [ ] **Step 7: Commit**

```bash
git add scripts/sync-decision-tree.sh scripts/inject_nav.py scripts/write_stats.py engine/index.html assets/data/scenarios.json assets/data/stats.json
git commit -m "Add sync script; vendor first build of the TypeSafeStroke engine artifact

Depends on the ?scenario deep-link patch applied to
~/Downloads/TypeSafeWork/StrokeDecisionTree/review/template.html (not
tracked in this repo, which has no git of its own)."
```

---

## Task 7: Case-notes content

**Files:**
- Create: `assets/data/case-notes.json`

**Interfaces:**
- Consumes: scenario ids from `assets/data/scenarios.json` (Task 6) — every id must be covered, no extras.
- Produces (consumed by Task 8): `{"S01": {"theme": "...", "note": "..."}, ...}` for all 40 ids. `theme` must be one of exactly these 9 strings (order matters, matches Task 8's `THEME_ORDER`):
  `"Core pathway & absolute exclusions"`, `"Imaging & core-size edge cases"`, `"Vessel & anatomy nuance"`, `"Baseline function & special populations"`, `"Anticoagulation, labs & recent-procedure risk"`, `"Blood pressure"`, `"Incomplete information"`, `"Post-treatment complications"`, `"Downstream care & systems"`.

- [ ] **Step 1: Write `assets/data/case-notes.json`**

```json
{
  "S01": { "theme": "Core pathway & absolute exclusions", "note": "The core pathway at its cleanest: disabling deficit, clean imaging, early window — thrombolysis plus an EVT bridge with no branch left ambiguous." },
  "S02": { "theme": "Core pathway & absolute exclusions", "note": "Tests the non-disabling branch — a real stroke that still routes away from standard thrombolysis and into antiplatelet therapy." },
  "S04": { "theme": "Core pathway & absolute exclusions", "note": "The absolute exclusion the whole pathway checks before anything else runs." },
  "S33": { "theme": "Core pathway & absolute exclusions", "note": "Past every reperfusion window — the tree still has to land somewhere useful." },
  "S34": { "theme": "Core pathway & absolute exclusions", "note": "Routing and transfer logic when EVT isn't available on site." },

  "S05": { "theme": "Imaging & core-size edge cases", "note": "Unwitnessed onset — the tree lets imaging mismatch substitute for a clock nobody can read." },
  "S06": { "theme": "Imaging & core-size edge cases", "note": "Vessel location and hemisphere dominance change the answer even when perfusion looks favorable." },
  "S07": { "theme": "Imaging & core-size edge cases", "note": "Late window, but a small enough core that time alone doesn't disqualify the patient." },
  "S08": { "theme": "Imaging & core-size edge cases", "note": "A large core early in the window — tests where the ASPECTS threshold actually bites." },
  "S09": { "theme": "Imaging & core-size edge cases", "note": "About as large a core as the tree will ever see — the floor of the ASPECTS threshold." },
  "S10": { "theme": "Imaging & core-size edge cases", "note": "Large core, late window, and advanced age stacked together — three relative factors at once." },

  "S11": { "theme": "Vessel & anatomy nuance", "note": "Posterior circulation with a severe deficit gets a wider window than anterior circulation would." },
  "S12": { "theme": "Vessel & anatomy nuance", "note": "Same vessel, mild deficit — tests whether severity alone gates EVT for basilar occlusion." },
  "S13": { "theme": "Vessel & anatomy nuance", "note": "The M2-dominance branch that CodeStrokeApp's current model doesn't capture yet." },
  "S32": { "theme": "Vessel & anatomy nuance", "note": "An ischemic event the tree has to recognize as outside the standard cerebral pathway." },

  "S14": { "theme": "Baseline function & special populations", "note": "Mild baseline disability — still a clear candidate, not an automatic individualize." },
  "S15": { "theme": "Baseline function & special populations", "note": "Moderate baseline disability tips the same occlusion into individualized decision-making." },
  "S16": { "theme": "Baseline function & special populations", "note": "The pediatric age gate in the early window, where adult defaults don't apply." },
  "S17": { "theme": "Baseline function & special populations", "note": "Pediatric, late window, and imaging-selected — the narrowest version of the EVT criteria." },
  "S39": { "theme": "Baseline function & special populations", "note": "Pregnancy as a relative factor the tree weighs, not an automatic exclusion." },

  "S03": { "theme": "Anticoagulation, labs & recent-procedure risk", "note": "A DOAC with no drug level and no clear last-dose confirmation — thrombolysis eligibility narrows, EVT stays open." },
  "S18": { "theme": "Anticoagulation, labs & recent-procedure risk", "note": "Hypoglycemia that can mimic or worsen a deficit — corrected before the stroke pathway proceeds." },
  "S21": { "theme": "Anticoagulation, labs & recent-procedure risk", "note": "A recent-surgery relative contraindication with its own lookback window." },

  "S19": { "theme": "Blood pressure", "note": "Above the pre-treatment blood pressure threshold — treat first, then re-check eligibility." },
  "S20": { "theme": "Blood pressure", "note": "Blood pressure that won't come into range in time closes the thrombolysis window entirely." },
  "S37": { "theme": "Blood pressure", "note": "Post-stroke blood pressure management when reperfusion therapy isn't in the picture." },

  "S22": { "theme": "Incomplete information", "note": "The 'unknown is not no' rule under real time pressure — the tree stops and asks rather than assuming." },
  "S35": { "theme": "Incomplete information", "note": "Two unknowns stacked — onset time and imaging strategy both still open." },
  "S36": { "theme": "Incomplete information", "note": "The empty-state worst case for how the tree handles missing information." },

  "S23": { "theme": "Post-treatment complications", "note": "The symptomatic hemorrhage pathway that follows a treatment complication, not a treatment decision." },
  "S24": { "theme": "Post-treatment complications", "note": "A different post-thrombolysis emergency, with its own immediate management branch." },
  "S28": { "theme": "Post-treatment complications", "note": "A day-2 complication that moves the patient into decompressive-surgery territory." },
  "S29": { "theme": "Post-treatment complications", "note": "A posterior fossa emergency that exits the standard pathway entirely." },

  "S25": { "theme": "Downstream care & systems", "note": "Reperfusion grading after mechanical-only treatment, feeding directly into secondary prevention." },
  "S26": { "theme": "Downstream care & systems", "note": "High-risk TIA triage — no reperfusion decision, but urgency the tree still has to route correctly." },
  "S27": { "theme": "Downstream care & systems", "note": "Anticoagulation timing after a non-reperfused cardioembolic stroke — AHA and CSBPR diverge here." },
  "S30": { "theme": "Downstream care & systems", "note": "Mothership-versus-drip-and-ship, in a system built to support direct transfer." },
  "S31": { "theme": "Downstream care & systems", "note": "The same routing decision under worse real-world constraints." },
  "S38": { "theme": "Downstream care & systems", "note": "Mild deficit, late presentation, no reperfusion candidate — secondary prevention carries the visit." },
  "S40": { "theme": "Downstream care & systems", "note": "A stroke mimic that turns out not to be one — the tree has to tell the difference." }
}
```

- [ ] **Step 2: Verify coverage against `scenarios.json`**

```bash
python3 -c "
import json
notes = json.load(open('assets/data/case-notes.json'))
scen = {s['id'] for s in json.load(open('assets/data/scenarios.json'))['scenarios']}
assert set(notes) == scen, (set(notes) ^ scen)
themes = {
  'Core pathway & absolute exclusions', 'Imaging & core-size edge cases', 'Vessel & anatomy nuance',
  'Baseline function & special populations', 'Anticoagulation, labs & recent-procedure risk', 'Blood pressure',
  'Incomplete information', 'Post-treatment complications', 'Downstream care & systems',
}
assert {v['theme'] for v in notes.values()} == themes
print('OK', len(notes))
"
```
Expected: `OK 40`.

- [ ] **Step 3: Commit**

```bash
git add assets/data/case-notes.json
git commit -m "Add themed case notes for all 40 TypeSafeStroke scenarios"
```

---

## Task 8: `/cases/` page

**Files:**
- Create: `cases/index.html`

**Interfaces:**
- Consumes: `assets/css/site.css` classes (Task 2), `assets/data/scenarios.json` (Task 6), `assets/data/case-notes.json` (Task 7), `assets/img/favicon.svg` + `assets/img/app-icon.png` (Task 4). `THEME_ORDER` array must match Task 7's 9 theme strings exactly, in the spec's table order.
- Produces: route `/cases/`, linking each card to `/engine/?scenario=<id>`.

- [ ] **Step 1: Write `cases/index.html`**

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Case scenarios — Hyperacute Stroke Decision Engine</title>
<meta name="description" content="40 clinical test scenarios for the Hyperacute Stroke Decision Engine, grouped by theme, each running live against the real decision tree.">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>

<nav class="topnav">
  <img class="topnav__mark" src="/assets/img/app-icon.png" alt="">
  <a class="topnav__title" href="/">Hyperacute Stroke Decision Engine</a>
  <div class="topnav__links">
    <a href="/">Home</a>
    <a href="/engine/">Decision engine</a>
    <a href="/cases/" aria-current="page">Case scenarios</a>
  </div>
</nav>

<header class="section section--tight wrap">
  <span class="eyebrow">40 clinical test scenarios</span>
  <h1 style="font-size:clamp(28px,4vw,42px)">Case scenarios &amp; edge cases</h1>
  <p class="lede">Every card below is a real test case from TypeSafeStroke's scenario suite &mdash; the same 40 cases that gate every change to the tree. Open one and it runs live against the actual decision engine, not a canned summary.</p>
</header>

<main class="wrap">
  <div id="theme-sections"></div>
</main>

<footer class="site-footer wrap">
  <p class="disclaimer" id="disclaimer-text"></p>
  <p>Sources: 2026 AHA/ASA Acute Ischemic Stroke Guideline &middot; CSBPR Acute Stroke Management 2022 &middot; CSBPR EVT Interim Update 2025 &middot; Thrombosis Canada IVT/EVT Guide.</p>
  <p>An educational initiative &mdash; Division of Neurology, University of Toronto &mdash; Dr. Houman Khosravani, MD PhD FRCPC.</p>
  <div class="links">
    <a href="/">Home</a>
    <a href="/engine/">Decision engine</a>
    <a href="https://github.com/neuroccm/acute-stroke-decision-engine">GitHub</a>
  </div>
</footer>

<script>
const THEME_ORDER = [
  "Core pathway & absolute exclusions",
  "Imaging & core-size edge cases",
  "Vessel & anatomy nuance",
  "Baseline function & special populations",
  "Anticoagulation, labs & recent-procedure risk",
  "Blood pressure",
  "Incomplete information",
  "Post-treatment complications",
  "Downstream care & systems",
];

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

Promise.all([
  fetch("/assets/data/scenarios.json").then((r) => r.json()),
  fetch("/assets/data/case-notes.json").then((r) => r.json()),
]).then(([scenData, notes]) => {
  const titleById = Object.fromEntries(scenData.scenarios.map((s) => [s.id, s.title]));
  const root = document.getElementById("theme-sections");
  for (const theme of THEME_ORDER) {
    const ids = Object.keys(notes).filter((id) => notes[id].theme === theme).sort();
    if (!ids.length) continue;
    const section = document.createElement("section");
    section.className = "section";
    section.innerHTML = `<h2>${esc(theme)}</h2><div class="card-grid"></div>`;
    const grid = section.querySelector(".card-grid");
    for (const id of ids) {
      const a = document.createElement("a");
      a.className = "card";
      a.href = `/engine/?scenario=${encodeURIComponent(id)}`;
      a.innerHTML = `<span class="card__meta">${esc(id)}</span><h3>${esc(titleById[id] || id)}</h3><p>${esc(notes[id].note)}</p>`;
      grid.appendChild(a);
    }
    root.appendChild(section);
  }
});

fetch("/assets/data/stats.json").then((r) => r.json()).catch(() => null);
document.getElementById("disclaimer-text").textContent =
  "Clinical decision support derived from the cited guidelines. It does not replace clinical judgement, local protocols, or specialist consultation. Draft pending clinical review.";
</script>

</body>
</html>
```

- [ ] **Step 2: Verify in a browser**

```bash
python3 -m http.server 4173 &
SERVER_PID=$!
```
Navigate to `http://localhost:4173/cases/` with `claude-in-chrome`. Confirm: 9 theme headings render in the spec's order, card count per theme matches the spec table (5/6/4/5/3/3/3/4/7 = 40 total), each card shows an id badge + title + one-line note, and clicking a card (e.g. the S16 card) navigates to `/engine/?scenario=S16` and preloads it (per Task 6 Step 5). Check console for errors — expect none. `kill $SERVER_PID`.

- [ ] **Step 3: Commit**

```bash
git add cases/index.html
git commit -m "Add case-scenario index page grouped by clinical theme"
```

---

## Task 9: Homepage

**Files:**
- Create: `index.html`

**Interfaces:**
- Consumes: `assets/css/site.css` (Task 2), all 10 icons (Task 3), brand assets (Task 4), `assets/data/stats.json` (Task 6).
- Produces: route `/`, linking to `/engine/` and `/cases/`.

- [ ] **Step 1: Write `index.html`**

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hyperacute Stroke Decision Engine</title>
<meta name="description" content="A type-safe, citation-traced decision engine for acute ischemic stroke, built from U.S. and Canadian guidelines. Open source, built from CodeStrokeApp.">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>

<nav class="topnav">
  <img class="topnav__mark" src="/assets/img/app-icon.png" alt="">
  <a class="topnav__title" href="/">Hyperacute Stroke Decision Engine</a>
  <div class="topnav__links">
    <a href="/" aria-current="page">Home</a>
    <a href="/engine/">Decision engine</a>
    <a href="/cases/">Case scenarios</a>
  </div>
</nav>

<header class="hero">
  <div class="wrap">
    <div class="hero__row">
      <img class="hero__mark" src="/assets/img/app-icon.png" alt="">
      <span class="eyebrow" style="margin:0">From CodeStrokeApp</span>
    </div>
    <h1>A type-safe decision engine for the first hours of stroke care</h1>
    <p class="lede">Every branch is built from the 2026 AHA/ASA guideline, CSBPR 2022 and its 2025 EVT update, and the Thrombosis Canada guide &mdash; with a verbatim citation, page number, and grade behind every recommendation. Free-text input is turned into a typed patient state with TypeSafe, then evaluated by the same engine that runs inside CodeStrokeApp.</p>
    <div class="hero__actions">
      <a class="btn btn--primary" href="/engine/">Run the decision engine</a>
      <a class="btn btn--ghost" href="/cases/">Browse case scenarios</a>
    </div>
    <div class="badge--disclaimer">Draft &middot; decision support, not orders</div>
  </div>
</header>

<section class="section">
  <div class="wrap">
    <span class="eyebrow">The problem</span>
    <h2 style="font-size:clamp(24px,3.4vw,34px);max-width:26ch">Guidelines are thousands of pages. Bedside decisions happen in minutes.</h2>
    <p class="lede">The AHA/ASA and Canadian (CSBPR) stroke guidelines run to hundreds of pages combined, and they don't always agree with each other. A team standing at the bedside needs a fast, specific, defensible answer &mdash; and needs to know exactly which page of which guideline that answer came from.</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <span class="eyebrow">What this is</span>
    <h2 style="font-size:clamp(24px,3.4vw,34px);max-width:30ch">A hand-authored decision tree, every leaf traced back to its source</h2>
    <p class="lede">TypeSafeStroke pairs a small language model (TypeSafe) that turns free text &mdash; an EMS handover, a history, a medication list &mdash; into typed, confidence-scored inputs, with a decision tree authored directly from the guidelines, node by node. Nothing is inferred silently: unknown is never read as no. When the tree is missing something it needs, it stops and says exactly what.</p>
    <div class="stat-strip" id="stat-strip">
      <div class="stat"><b>&hellip;</b><span>Modules</span></div>
      <div class="stat"><b>&hellip;</b><span>Decision nodes</span></div>
      <div class="stat"><b>&hellip;</b><span>Outcome paths</span></div>
      <div class="stat"><b>&hellip;</b><span>Cited statements</span></div>
      <div class="stat"><b>&hellip;</b><span>Full citation corpus</span></div>
      <div class="stat"><b>&hellip;</b><span>Test scenarios</span></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <span class="eyebrow">How it works</span>
    <h2 style="font-size:clamp(24px,3.4vw,34px);max-width:26ch">From free text to an evidence-linked outcome</h2>
    <div class="step-grid">
      <div class="step">
        <div class="step__icon" id="icon-slot-mic"></div>
        <h3>1. Free text in</h3>
        <p>EMS handover, chart history, med list &mdash; whatever's on hand, unstructured.</p>
      </div>
      <div class="step">
        <div class="step__icon" id="icon-slot-cpu"></div>
        <h3>2. Typed patient state</h3>
        <p>TypeSafe infers structured fields with asymmetric confidence thresholds; anything uncertain stays unconfirmed rather than guessed.</p>
      </div>
      <div class="step">
        <div class="step__icon" id="icon-slot-brain"></div>
        <h3>3. Decision engine</h3>
        <p>A three-valued tree &mdash; true, false, unknown &mdash; walks phase-ordered modules and stops rather than assumes.</p>
      </div>
      <div class="step">
        <div class="step__icon" id="icon-slot-check"></div>
        <h3>4. Evidence-linked outcome</h3>
        <p>Every recommendation carries its source, section, page, and grade &mdash; ready to check against the guideline itself.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <span class="eyebrow">From CodeStrokeApp to the web</span>
    <h2 style="font-size:clamp(24px,3.4vw,34px);max-width:28ch">The same engine, running twice, agreeing every time</h2>
    <p class="lede">This tree runs in Swift inside CodeStrokeApp and in JavaScript on this page &mdash; two independent implementations of the same semantics, checked against each other on every one of the 40 test scenarios below. It's slated to replace CodeStrokeApp's current hard-coded <code>EligibilityEngine</code>, whose rules already differ from the sources in places this project corrects.</p>
    <div class="step-grid" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr))">
      <div class="step">
        <div class="step__icon" id="icon-slot-waveform"></div>
        <h3>Dual-engine parity</h3>
        <p>Swift and JavaScript engines are parity-tested against the same scenario suite on every rebuild.</p>
      </div>
      <div class="step">
        <div class="step__icon" id="icon-slot-shield"></div>
        <h3>Unknown is never no</h3>
        <p>A missing input halts a decision and records what's needed &mdash; it never falls through to a false branch.</p>
      </div>
      <div class="step">
        <div class="step__icon" id="icon-slot-clock"></div>
        <h3>Draft, under clinical review</h3>
        <p>Every open question is tracked in the open below &mdash; nothing here is presented as finished.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <span class="eyebrow">Explore</span>
    <div class="card-grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
      <a class="card" href="/engine/">
        <span class="card__meta">Interactive</span>
        <h3>Run the decision engine</h3>
        <p>Load a case, or build one field at a time, and see the outcomes and citations the tree produces &mdash; the exact same artifact this project ships.</p>
      </a>
      <a class="card" href="/cases/">
        <span class="card__meta">40 scenarios</span>
        <h3>Case scenarios &amp; edge cases</h3>
        <p>Pediatric occlusions, basilar strokes, DOACs without a level, malignant edema, incomplete histories &mdash; grouped by theme, each running live.</p>
      </a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <span class="eyebrow">Open questions</span>
    <h2 style="font-size:clamp(24px,3.4vw,34px);max-width:26ch">Where the guidelines disagree, or the tree isn't settled yet</h2>
    <ul class="lede" style="padding-left:20px">
      <li>AHA's "absolute" Table 8 items are worded as "higher relative harm" in its own legend; the tree currently treats them as do-not-give.</li>
      <li>Lab thresholds (platelets, INR, aPTT, PT) are AHA-absolute but CSBPR/Thrombosis Canada-relative &mdash; the tree follows AHA.</li>
      <li>ASPECTS &lt;6 for thrombolysis is CSBPR-relative; AHA only excludes extensive, clear hypodensity.</li>
      <li>Pediatric EVT at 6&ndash;17y in the 0&ndash;6h window: AHA's figure requires salvageable tissue that the recommendation text doesn't state explicitly.</li>
      <li>AHA favors early DOAC resumption after AF-related stroke (2a); CSBPR uses a 1-3-6-12 day consensus schedule. Both are shown.</li>
      <li>Not covered: intracerebral hemorrhage management, and CSBPR's inpatient-complications and MAiD sections.</li>
    </ul>
  </div>
</section>

<footer class="site-footer wrap">
  <p class="disclaimer">Clinical decision support derived from the cited guidelines. It does not replace clinical judgement, local protocols, or specialist consultation. Draft pending clinical review.</p>
  <p>Sources: 2026 AHA/ASA Acute Ischemic Stroke Guideline &middot; CSBPR Acute Stroke Management 2022 &middot; CSBPR EVT Interim Update 2025 &middot; Thrombosis Canada IVT/EVT Guide. Code is MIT-licensed; cited guideline text is reproduced as short, individually attributed quotations for clinical and educational use.</p>
  <p>An educational initiative &mdash; Division of Neurology, University of Toronto &mdash; Dr. Houman Khosravani, MD PhD FRCPC.</p>
  <div class="links">
    <a href="/engine/">Decision engine</a>
    <a href="/cases/">Case scenarios</a>
    <a href="https://github.com/neuroccm/acute-stroke-decision-engine">GitHub</a>
  </div>
</footer>

<script>
const ICONS = {
  mic: "/assets/icons/icon-mic.svg",
  cpu: "/assets/icons/icon-cpu.svg",
  brain: "/assets/icons/icon-brain.svg",
  check: "/assets/icons/icon-check-seal.svg",
  waveform: "/assets/icons/icon-waveform.svg",
  shield: "/assets/icons/icon-shield.svg",
  clock: "/assets/icons/icon-clock.svg",
};
Object.entries(ICONS).forEach(([key, src]) => {
  const slot = document.getElementById(`icon-slot-${key}`);
  if (slot) fetch(src).then((r) => r.text()).then((svg) => (slot.innerHTML = svg));
});

fetch("/assets/data/stats.json").then((r) => r.json()).then((s) => {
  const strip = document.getElementById("stat-strip");
  const items = [
    [s.modules, "Modules"],
    [s.nodes, "Decision nodes"],
    [s.outcomes, "Outcome paths"],
    [s.citedStatements, "Cited statements"],
    [s.corpusStatements, "Full citation corpus"],
    [s.scenarios, "Test scenarios"],
  ];
  strip.innerHTML = items.map(([n, label]) => `<div class="stat"><b>${n}</b><span>${label}</span></div>`).join("");
});
</script>

</body>
</html>
```

- [ ] **Step 2: Verify in a browser**

```bash
python3 -m http.server 4173 &
SERVER_PID=$!
```
Navigate to `http://localhost:4173/` with `claude-in-chrome`. Confirm: sticky top nav, hero renders with gradient + disclaimer badge + both CTAs, stat strip fills in with real numbers (13/217/142/362/1268/40) after the fetch resolves, all 6 icons render (not broken images) in the "How it works" and "CodeStrokeApp" sections, both explore cards link correctly, open-questions list renders, footer disclaimer matches the canonical text verbatim. Resize to a narrow (390px) viewport and confirm no horizontal scroll and the stat strip / step grid reflow to fewer columns. Check console for errors — expect none. Click through to `/engine/` and `/cases/` and back to confirm nav links all resolve. `kill $SERVER_PID`.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "Add homepage: one-page single-scroll overview of the decision engine"
```

---

## Task 10: README and final cross-page polish

**Files:**
- Create: `README.md`
- Modify (only if Task 9's browser check found a real defect): any of the above

**Interfaces:**
- Produces: top-level project documentation covering what this is, local preview, the sync workflow, and Cloudflare Pages deployment.

- [ ] **Step 1: Write `README.md`**

```markdown
# Hyperacute Stroke Decision Engine

A type-safe, citation-traced decision engine for acute ischemic stroke,
built from the 2026 AHA/ASA guideline, CSBPR 2022 (+ 2025 EVT update), and
the Thrombosis Canada guide. This repo is the public site for the
[TypeSafeStroke](https://github.com/neuroccm) decision tree that also runs
inside CodeStrokeApp.

**Status: draft, pending clinical review. Decision support, not orders.**

## Structure

- `index.html` — one-page overview.
- `engine/index.html` — the live decision engine. **Generated only** by
  `scripts/sync-decision-tree.sh` — never hand-edit this file.
- `cases/index.html` — 40 clinical test scenarios grouped by theme, each
  linking into the live engine with real inputs preloaded.
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
```

- [ ] **Step 2: Full cross-page verification pass**

```bash
python3 -m http.server 4173 &
SERVER_PID=$!
```
With `claude-in-chrome`: visit `/`, click "Run the decision engine" → confirm lands on `/engine/` with breadcrumb nav; click "Case scenarios →" in that breadcrumb → confirm lands on `/cases/`; click any case card → confirm lands on `/engine/?scenario=SXX` with that scenario preloaded; click "← Back to overview" in the engine subfooter → confirm lands on `/`. Confirm the disclaimer text is byte-identical across `/`, `/cases/`, and `/engine/`'s own footer. `kill $SERVER_PID`. Fix anything broken directly in the relevant file from Tasks 6/8/9 (do not add new files for this).

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "Add README with local preview, sync, and deploy instructions"
```

---

## Task 11: Disclaimer page and footer duty-of-care callout

Added mid-run at the user's request: a dedicated `/disclaimer/` page adapted
from the author's existing codestroke.net terms-of-use text, plus a bold
"no duty of care" callout added to the footer of all three existing pages
(`index.html`, `cases/index.html`, and the vendored `engine/index.html`'s
injected subfooter). Four adaptation decisions already made with the user:
reuse `stroke@codestroke.net` as the HIPAA/PHIPA contact, omit the
advertising-policy clause (no ads on this project), state plainly that no
tracking/analytics is in place (accurate for the current static site), and
omit the Dr. Luis Domitrovic illustration credit (this site uses none of
his artwork).

**Files:**
- Create: `disclaimer/index.html`
- Modify: `assets/css/site.css` (add `.footer-callout` and `.prose` rules)
- Modify: `index.html:153-161` (footer)
- Modify: `cases/index.html:36-44` (footer)
- Modify: `scripts/inject_nav.py` (`SUBFOOTER_HTML`)
- Regenerate: `engine/index.html` (via `scripts/sync-decision-tree.sh`)

**Interfaces:**
- Consumes: `assets/css/site.css` classes from Task 2 (`.topnav`, `.section`,
  `.wrap`, `.eyebrow`, `.lede`, `.site-footer`), the disclaimer text and
  attribution line already used on every page.
- Produces: route `/disclaimer/`; a `.footer-callout` class and `.prose`
  class added to `assets/css/site.css` for this and future pages; a
  `<a href="/disclaimer/">Disclaimer</a>` link added to the footer `.links`
  row on all three pages.

- [ ] **Step 1: Add two rules to `assets/css/site.css`** (append after the
  existing `.site-footer .links a:hover { color: var(--text-1); }` rule,
  before the closing responsive `@media` block)

```css
.footer-callout { font: 700 13px/1.5 var(--sans); color: var(--red); margin: 0 0 14px; }

.prose { max-width: 74ch; color: var(--text-1); font-size: 14.5px; line-height: 1.7; }
.prose h2 { font-size: 18px; margin: 32px 0 4px; color: var(--text-1); }
.prose p { margin: 0 0 14px; }
.prose a { color: var(--accent); }
```

- [ ] **Step 2: Write `disclaimer/index.html`**

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Disclaimer — Hyperacute Stroke Decision Engine</title>
<meta name="description" content="Terms of use and disclaimer for the Hyperacute Stroke Decision Engine: educational purpose, no duty of care, no real patient data, and source attribution.">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>

<nav class="topnav">
  <img class="topnav__mark" src="/assets/img/app-icon.png" alt="">
  <a class="topnav__title" href="/">Hyperacute Stroke Decision Engine</a>
  <div class="topnav__links">
    <a href="/">Home</a>
    <a href="/engine/">Decision engine</a>
    <a href="/cases/">Case scenarios</a>
  </div>
</nav>

<header class="section section--tight wrap">
  <span class="eyebrow">Terms of use</span>
  <h1 style="font-size:clamp(28px,4vw,42px)">Disclaimer</h1>
  <p class="lede">There is no duty of care. This is an educational website.</p>
</header>

<main class="wrap" style="padding-bottom:48px">
  <div class="prose">
    <p>This Terms of Use Agreement (this &ldquo;Agreement&rdquo;) is entered into by and between the Hyperacute Stroke Decision Engine project (Dr. Houman Khosravani, the &ldquo;author&rdquo;) and &ldquo;you,&rdquo; the user of this website (the &ldquo;Site&rdquo;). Access to, use of, and/or browsing of the Site is provided subject to the terms and conditions set out here. By accessing, using, and/or browsing the Site, you agree to these terms and conditions.</p>
    <p>All opinions expressed here are those of the author and not of their employer.</p>

    <h2>Overview</h2>
    <p>Information provided on this Site is for EDUCATIONAL PURPOSES ONLY. THERE IS NO DUTY OF CARE. THIS WEBSITE IS FOR EDUCATIONAL AND RESEARCH PURPOSES AND USE BY SPECIFIC HEALTH PROFESSIONALS. It is not intended as, and does not substitute for, medical advice. If you are a patient, please see your doctor for evaluation of your individual case. Under no circumstances will the author be liable to you for any direct or indirect damages arising in connection with use of this Site. This Site&rsquo;s intended audience is medical providers (medical students, residents, staff, nurses) for EDUCATIONAL PURPOSES ONLY. Any operational decision or use is at the discretion of the provider and based on their own expertise and judgment. This Site and its content have no medical care responsibility, do not claim to be the ground source of truth, and do not replace expert clinical opinion and practice. The decision engine on this Site is explicitly marked draft and pending clinical review &mdash; see the disclaimer repeated on every page.</p>

    <h2>External hyperlinks</h2>
    <p>The appearance of external hyperlinks to other websites does not constitute endorsement. We do not verify, endorse, or take responsibility for the accuracy, currency, completeness, or quality of the content contained on those sites.</p>

    <h2>Case data</h2>
    <p>There is no real patient data on this Site. We do not write or &ldquo;blog&rdquo; about patients. The 40 case scenarios shown on this Site are synthetic test cases used to validate the decision engine&rsquo;s logic &mdash; similar in spirit to the vignettes in a board-exam question bank &mdash; not descriptions of real patients or real clinical encounters.</p>
    <p>Report a suspected HIPAA/PHIPA violation to <a href="mailto:stroke@codestroke.net">stroke@codestroke.net</a>.</p>

    <h2>Purpose of this Site</h2>
    <p>This Site is intended for medical professionals but can also be accessed by the general public. The information provided here is made available by the author for educational purposes only and is not intended to provide medical advice. By accessing the Site, visitors acknowledge that there is no physician-patient relationship between them and the author. The Site should not be used as a substitute for competent medical advice from a licensed physician. It is designed to support, not replace, the relationship that exists between a patient and their physician. Every recommendation the decision engine produces is linked to its source guideline, section, page, and grade &mdash; nothing here asserts authority beyond the cited source.</p>

    <h2>Privacy</h2>
    <p>This Site does not currently collect any personal information about its visitors and readers, and does not use cookies or analytics.</p>

    <h2>Disclosure of funding sources</h2>
    <p>This is a private, non-commercial educational project receiving no funding from any third party.</p>

    <h2>Links to other websites</h2>
    <p>This Site may contain links to third-party websites. These links do not represent a guarantee, warranty, or recommendation by the author, nor any affiliation, sponsorship, or endorsement of those third-party websites.</p>

    <h2>Copyright</h2>
    <p>Copyright &copy; 2026 Dr. Houman Khosravani, and Division of Neurology, University of Toronto. Code is MIT-licensed (see the project&rsquo;s GitHub repository); cited guideline text is reproduced as short, individually attributed quotations for clinical and educational use.</p>
  </div>
</main>

<footer class="site-footer wrap">
  <p class="footer-callout">There is no duty of care. This is an educational website.</p>
  <p class="disclaimer">Clinical decision support derived from the cited guidelines. It does not replace clinical judgement, local protocols, or specialist consultation. Draft pending clinical review.</p>
  <p>An educational initiative &mdash; Division of Neurology, University of Toronto &mdash; Dr. Houman Khosravani, MD PhD FRCPC.</p>
  <div class="links">
    <a href="/">Home</a>
    <a href="/engine/">Decision engine</a>
    <a href="/cases/">Case scenarios</a>
    <a href="/disclaimer/">Disclaimer</a>
    <a href="https://github.com/neuroccm/acute-stroke-decision-engine">GitHub</a>
  </div>
</footer>

</body>
</html>
```

- [ ] **Step 3: Edit `index.html`'s footer** — insert the callout as the
  first line inside the footer, and add the Disclaimer link:

Old:
```html
<footer class="site-footer wrap">
  <p class="disclaimer">Clinical decision support derived from the cited guidelines. It does not replace clinical judgement, local protocols, or specialist consultation. Draft pending clinical review.</p>
  <p>Sources: 2026 AHA/ASA Acute Ischemic Stroke Guideline &middot; CSBPR Acute Stroke Management 2022 &middot; CSBPR EVT Interim Update 2025 &middot; Thrombosis Canada IVT/EVT Guide. Code is MIT-licensed; cited guideline text is reproduced as short, individually attributed quotations for clinical and educational use.</p>
  <p>An educational initiative &mdash; Division of Neurology, University of Toronto &mdash; Dr. Houman Khosravani, MD PhD FRCPC.</p>
  <div class="links">
    <a href="/engine/">Decision engine</a>
    <a href="/cases/">Case scenarios</a>
    <a href="https://github.com/neuroccm/acute-stroke-decision-engine">GitHub</a>
  </div>
</footer>
```

New:
```html
<footer class="site-footer wrap">
  <p class="footer-callout">There is no duty of care. This is an educational website.</p>
  <p class="disclaimer">Clinical decision support derived from the cited guidelines. It does not replace clinical judgement, local protocols, or specialist consultation. Draft pending clinical review.</p>
  <p>Sources: 2026 AHA/ASA Acute Ischemic Stroke Guideline &middot; CSBPR Acute Stroke Management 2022 &middot; CSBPR EVT Interim Update 2025 &middot; Thrombosis Canada IVT/EVT Guide. Code is MIT-licensed; cited guideline text is reproduced as short, individually attributed quotations for clinical and educational use.</p>
  <p>An educational initiative &mdash; Division of Neurology, University of Toronto &mdash; Dr. Houman Khosravani, MD PhD FRCPC.</p>
  <div class="links">
    <a href="/engine/">Decision engine</a>
    <a href="/cases/">Case scenarios</a>
    <a href="/disclaimer/">Disclaimer</a>
    <a href="https://github.com/neuroccm/acute-stroke-decision-engine">GitHub</a>
  </div>
</footer>
```

- [ ] **Step 4: Edit `cases/index.html`'s footer** the same way:

Old:
```html
<footer class="site-footer wrap">
  <p class="disclaimer" id="disclaimer-text"></p>
  <p>Sources: 2026 AHA/ASA Acute Ischemic Stroke Guideline &middot; CSBPR Acute Stroke Management 2022 &middot; CSBPR EVT Interim Update 2025 &middot; Thrombosis Canada IVT/EVT Guide.</p>
  <p>An educational initiative &mdash; Division of Neurology, University of Toronto &mdash; Dr. Houman Khosravani, MD PhD FRCPC.</p>
  <div class="links">
    <a href="/">Home</a>
    <a href="/engine/">Decision engine</a>
    <a href="https://github.com/neuroccm/acute-stroke-decision-engine">GitHub</a>
  </div>
```

New:
```html
<footer class="site-footer wrap">
  <p class="footer-callout">There is no duty of care. This is an educational website.</p>
  <p class="disclaimer" id="disclaimer-text"></p>
  <p>Sources: 2026 AHA/ASA Acute Ischemic Stroke Guideline &middot; CSBPR Acute Stroke Management 2022 &middot; CSBPR EVT Interim Update 2025 &middot; Thrombosis Canada IVT/EVT Guide.</p>
  <p>An educational initiative &mdash; Division of Neurology, University of Toronto &mdash; Dr. Houman Khosravani, MD PhD FRCPC.</p>
  <div class="links">
    <a href="/">Home</a>
    <a href="/engine/">Decision engine</a>
    <a href="/disclaimer/">Disclaimer</a>
    <a href="https://github.com/neuroccm/acute-stroke-decision-engine">GitHub</a>
  </div>
```

- [ ] **Step 5: Edit `scripts/inject_nav.py`'s `SUBFOOTER_HTML`** to add the
  same callout (using the engine page's own CSS vars, since that page
  doesn't load `site.css`) and a Disclaimer link. Also add one rule to
  `EXTRA_CSS`:

Old `EXTRA_CSS` (add one rule to the end of the existing string, before the
closing `"""`):
```python
EXTRA_CSS = """
.site-crumbs { display:flex; align-items:center; gap:10px; padding-bottom:14px; margin-bottom:14px; border-bottom:1px solid var(--rule); font:600 12px/1 var(--cond); }
.site-crumbs img { border-radius:6px; display:block; }
.site-crumbs a { color: var(--muted); text-decoration:none; }
.site-crumbs a:hover { color: var(--accent); }
.site-crumbs .sep { color: var(--rule); }
.site-crumbs .current { color: var(--ink); }
.site-foot-links { display:flex; gap:16px; padding-top:14px; margin-top:18px; border-top:1px solid var(--rule); font:600 12px/1 var(--cond); }
.site-foot-links a { color: var(--muted); text-decoration:none; }
.site-foot-links a:hover { color: var(--accent); }
"""
```

New `EXTRA_CSS`:
```python
EXTRA_CSS = """
.site-crumbs { display:flex; align-items:center; gap:10px; padding-bottom:14px; margin-bottom:14px; border-bottom:1px solid var(--rule); font:600 12px/1 var(--cond); }
.site-crumbs img { border-radius:6px; display:block; }
.site-crumbs a { color: var(--muted); text-decoration:none; }
.site-crumbs a:hover { color: var(--accent); }
.site-crumbs .sep { color: var(--rule); }
.site-crumbs .current { color: var(--ink); }
.site-foot-links { display:flex; gap:16px; padding-top:14px; margin-top:18px; border-top:1px solid var(--rule); font:600 12px/1 var(--cond); }
.site-foot-links a { color: var(--muted); text-decoration:none; }
.site-foot-links a:hover { color: var(--accent); }
.site-footer-callout { font:700 12px/1.4 var(--sans); color: var(--cor3nb); margin: 0 0 10px; }
"""
```

Old `SUBFOOTER_HTML`:
```python
SUBFOOTER_HTML = """<div class="site-foot-links">
  <a href="/">&larr; Back to overview</a>
  <a href="/cases/">Case scenarios</a>
  <a href="https://github.com/neuroccm/acute-stroke-decision-engine">Source on GitHub</a>
</div>
"""
```

New `SUBFOOTER_HTML`:
```python
SUBFOOTER_HTML = """<p class="site-footer-callout">There is no duty of care. This is an educational website.</p>
<div class="site-foot-links">
  <a href="/">&larr; Back to overview</a>
  <a href="/cases/">Case scenarios</a>
  <a href="/disclaimer/">Disclaimer</a>
  <a href="https://github.com/neuroccm/acute-stroke-decision-engine">Source on GitHub</a>
</div>
"""
```

- [ ] **Step 6: Re-run the sync script to regenerate `engine/index.html`
  with the updated subfooter**

```bash
./scripts/sync-decision-tree.sh
```

- [ ] **Step 7: Verify in a browser**

```bash
python3 -m http.server 4173 &
SERVER_PID=$!
```
With `claude-in-chrome`, visit `/disclaimer/` and confirm: the page renders
with readable prose (headings and paragraphs properly spaced via `.prose`),
the "There is no duty of care" line appears both as the page's lede and as
the bold red `.footer-callout` in its own footer, the HIPAA/PHIPA mailto
link is present, and the topnav/footer links work. Then visit `/`,
`/cases/`, and `/engine/` and confirm each now shows the bold callout line
and a working `/disclaimer/` link in its footer (the engine page's version
uses its own red tone from `--cor3nb`, not `site.css`). Check console on
all four pages — expect no errors. `kill $SERVER_PID`.

- [ ] **Step 8: Update `README.md`'s Structure section** to add one line
  for the new page:

Old:
```markdown
- `cases/index.html` — 40 clinical test scenarios grouped by theme, each
  linking into the live engine with real inputs preloaded.
```

New:
```markdown
- `cases/index.html` — 40 clinical test scenarios grouped by theme, each
  linking into the live engine with real inputs preloaded.
- `disclaimer/index.html` — terms of use and disclaimer (no duty of care,
  educational purpose only, no real patient data, source attribution).
```

- [ ] **Step 9: Commit**

```bash
git add assets/css/site.css disclaimer/index.html index.html cases/index.html scripts/inject_nav.py engine/index.html README.md
git commit -m "Add disclaimer page and duty-of-care callout to every footer"
```

---

## Task 12: Publish to GitHub (explicit go-ahead required)

**STOP. Do not run this task's steps without Houman explicitly confirming he wants the repo created and pushed now** — this is public, visible to others, and not easily reversible. Confirm the repo name (`acute-stroke-decision-engine`) and that `neuroccm` is the right account before proceeding, since both were assumed in this plan, not reconfirmed at execution time.

**Files:** none (repo operations only).

- [ ] **Step 1: Confirm working tree is clean**

Run: `git status --short` — expect empty output (everything from Tasks 1–10 committed).

- [ ] **Step 2: Create the GitHub repo and push**

```bash
gh repo create neuroccm/acute-stroke-decision-engine --public \
  --description "A type-safe, citation-traced decision engine for acute ischemic stroke, built from U.S. and Canadian guidelines." \
  --source=. --remote=origin --push
```

- [ ] **Step 3: Verify**

Run: `gh repo view neuroccm/acute-stroke-decision-engine --web=false` — confirm it prints the expected description and is public.
Run: `git log --oneline -1` and `git -C . rev-parse origin/main` — confirm they match (push succeeded).

- [ ] **Step 4: Report the repo URL and the Cloudflare Pages connection step back to Houman** (from README Task 10) — this is a manual dashboard step outside the scope of this plan.

---

## Self-review notes

- **Spec coverage:** homepage (Task 9), `/engine/` live artifact + sync (Task 6, upstream patch Task 5), `/cases/` themed index (Tasks 7–8), CodeStrokeApp theme/icons (Tasks 2–4), public repo + disclaimer (Task 12 + disclaimer text baked into Tasks 8–10, plus a dedicated `/disclaimer/` page in Task 11), MIT code license + verbatim-citation attribution (Task 1 LICENSE, Task 10 README) all have a task. Cloudflare deploy is documented (README) but not executed — no Cloudflare credentials available in this environment (checked: `wrangler whoami` fails, not logged in); left as a documented manual step, matching the spec's "Deployment" section.
- **Placeholder scan:** no TBD/TODO; every step has literal file content or an exact command.
- **Type/interface consistency:** `THEME_ORDER` (Task 8) matches the 9 theme strings used in `case-notes.json` (Task 7) exactly; `stats.json` keys used in Task 9's fetch (`modules`, `nodes`, `outcomes`, `citedStatements`, `corpusStatements`, `scenarios`) match exactly what Task 6's `write_stats.py` writes; icon filenames referenced in Task 9's `ICONS` map match Task 3's filenames exactly; nav links (`/`, `/engine/`, `/cases/`) are consistent across Tasks 8, 9, and the injected nav in Task 6.
