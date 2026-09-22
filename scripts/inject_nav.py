#!/usr/bin/env python3
"""Wrap the vendored TypeSafeStroke artifact with this site's navigation.
The artifact's own CSS custom properties (--rule, --muted, --cond, --accent,
--ink) are reused so no extra stylesheet is loaded on this page. The page
already ships full light/dark CSS (:root[data-theme="light"|"dark"], see
template.html); the toggle button, its localStorage-backed logic, and the
site-wide dark default are all added here rather than upstream, since this
is site-level chrome/preference, not a TypeSafeStroke engine feature.

Usage: inject_nav.py <built.html> <out.html>
"""
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
html = src.read_text()

EXTRA_CSS = """
.site-nav { display:flex; align-items:center; gap:12px; padding-bottom:14px; margin-bottom:14px; border-bottom:1px solid var(--rule); }
.site-nav img { border-radius:6px; display:block; }
.site-nav__title { font:600 13px/1 var(--cond); letter-spacing:.01em; color: var(--ink); text-decoration:none; }
.site-nav__links { margin-left:auto; display:flex; align-items:center; gap:16px; font:600 12px/1 var(--cond); letter-spacing:.02em; flex-wrap:wrap; }
.site-nav__links a { color: var(--muted); text-decoration:none; }
.site-nav__links a:hover, .site-nav__links a[aria-current="page"] { color: var(--accent); }
.site-foot-links { display:flex; gap:16px; padding-top:14px; margin-top:18px; border-top:1px solid var(--rule); font:600 12px/1 var(--cond); }
.site-foot-links a { color: var(--muted); text-decoration:none; }
.site-foot-links a:hover { color: var(--accent); }
.site-footer-callout { font:700 12px/1.4 var(--sans); color: var(--cor3nb); margin: 0 0 10px; }
.theme-toggle { width:28px; height:28px; flex:none; display:inline-flex; align-items:center; justify-content:center;
  background: var(--sunk); border: 1px solid var(--rule); border-radius: 6px; font-size: 14px; line-height: 1; cursor: pointer; color: var(--ink); }
.theme-toggle:hover { border-color: var(--muted); }
"""

THEME_SCRIPT = """<script>
(function () {
  var KEY = "stroke-theme";
  var saved = localStorage.getItem(KEY);
  document.documentElement.setAttribute("data-theme", saved === "light" ? "light" : "dark");
  function paint(btn) {
    btn.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "\\u2600\\ufe0f" : "\\ud83c\\udf19";
  }
  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    paint(btn);
    btn.addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem(KEY, next);
      paint(btn);
    });
  });
})();
</script>
"""

NAV_HTML = """<nav class="site-nav">
  <img src="/assets/img/app-icon.png" alt="" width="26" height="26">
  <a href="/" class="site-nav__title">Hyperacute Stroke Decision Engine</a>
  <div class="site-nav__links">
    <a href="/">Home</a>
    <a href="/engine/" aria-current="page">Decision engine</a>
    <a href="/cases/">Case scenarios</a>
    <a href="/engine-jev/">Decision Engine Jev</a>
    <a href="/cases-jev/">Eval Cases Jev</a>
    <button id="theme-toggle" class="theme-toggle" type="button" aria-label="Toggle dark mode" title="Toggle dark mode">&#127761;</button>
  </div>
</nav>
"""

SUBFOOTER_HTML = """<p class="site-footer-callout">There is no duty of care. This is an educational website.</p>
<div class="site-foot-links">
  <a href="/">&larr; Back to overview</a>
  <a href="/cases/">Case scenarios</a>
  <a href="/disclaimer/">Disclaimer</a>
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
html = replace_once(html, "</style>", THEME_SCRIPT)
html = replace_once(html, '<div class="wrap">', NAV_HTML)
html = replace_once(html, '<footer id="disclaimer"></footer>', SUBFOOTER_HTML)

out.write_text(html)
print(f"{out} written, {len(html) // 1024} KB")
