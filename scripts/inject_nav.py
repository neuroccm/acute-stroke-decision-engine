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
.site-footer-callout { font:700 12px/1.4 var(--sans); color: var(--cor3nb); margin: 0 0 10px; }
"""

NAV_HTML = """<div class="site-crumbs">
  <img src="/assets/img/app-icon.png" alt="" width="22" height="22">
  <a href="/">Hyperacute Stroke Decision Engine</a>
  <span class="sep">/</span>
  <span class="current">Decision engine</span>
  <a href="/cases/" style="margin-left:auto">Case scenarios &rarr;</a>
</div>
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
html = replace_once(html, '<div class="wrap">', NAV_HTML)
html = replace_once(html, '<footer id="disclaimer"></footer>', SUBFOOTER_HTML)

out.write_text(html)
print(f"{out} written, {len(html) // 1024} KB")
