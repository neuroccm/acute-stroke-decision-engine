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
