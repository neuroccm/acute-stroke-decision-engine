#!/usr/bin/env python3
"""Bake a static snapshot of the Jev clinical-judgment eval into this repo.

Unlike scripts/sync-decision-tree.sh, this is a one-time snapshot of a
point-in-time evaluation writeup, not an ongoing sync target -- rerun it by
hand if TypeSafeWorkJev's results change, same as any other data file here.

Sources (never sends anything anywhere, no network calls):
- ~/Downloads/TypeSafeWorkJev/ClinicalEval -- a separate, non-git-tracked
  project directory. Reads the two results/_summary.json files, the per-case
  results/ischemic_decomposed/<id>_raw.json files, and calls its own
  ischemic.decompose_questions.build_eval_set_with_targets() (run as a
  subprocess from inside that directory, so its own relative imports
  resolve) purely to get each case's ground-truth outcome_id -- that
  function derives outcome_id from the case's own `expect` list, not from
  walking a tree, so it's valid regardless of which tree copy computed it.
- The canonical StrokeDecisionTree checkout (same one
  scripts/sync-decision-tree.sh reads) -- ClinicalEval keeps its own,
  independent copy for its test suite, which can drift out of sync (seen in
  practice: 217 nodes there vs 222 in the canonical copy at time of writing).
  Citation sources and divergence notes are looked up here, not in
  ClinicalEval's copy, so what this page shows always matches what the rest
  of the site already shows for the same outcome ids.

Usage: build_jev_eval.py <clinical_eval_dir> <stroke_decision_tree_dir> <out.json>
"""
import json
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
tree_dir = Path(sys.argv[2])
out = Path(sys.argv[3])

decomposed = json.loads((root / "results/ischemic_decomposed/_summary.json").read_text())
single_shot = json.loads((root / "results/ischemic/_summary.json").read_text())

eval_set_json = subprocess.run(
    [sys.executable, "-c",
     "import json; from ischemic.decompose_questions import build_eval_set_with_targets; "
     "print(json.dumps(build_eval_set_with_targets()))"],
    cwd=root, capture_output=True, text=True, check=True,
).stdout
outcome_targets = {row["id"]: row["targets"] for row in json.loads(eval_set_json)}

tree = json.loads((tree_dir / "Sources/StrokeDecisionEngine/Resources/decision_tree.json").read_text())
nodes = {}
for m in tree["modules"]:
    nodes.update(m["nodes"])

SOURCE_ORDER = ["AHA2026", "CSBPR2022", "CSBPR_EVT2025", "TC_IVT_EVT", "MEVO_REVIEW2026"]
SOURCE_LABEL = {
    "AHA2026": "AHA 2026", "CSBPR2022": "CSBPR 2022", "CSBPR_EVT2025": "CSBPR EVT 2025",
    "TC_IVT_EVT": "Thrombosis Canada", "MEVO_REVIEW2026": "MeVO review 2026",
}


def outcome_sources(outcome_id):
    n = nodes.get(outcome_id)
    if not n:
        return [], None
    present = set(e["source"] for e in n.get("evidence", []))
    ordered = [s for s in SOURCE_ORDER if s in present]
    return [SOURCE_LABEL.get(s, s) for s in ordered], n.get("divergence")


def by_question(rows):
    agg = {}
    for r in rows:
        q = r["question"]
        a = agg.setdefault(q, [0, 0])
        a[1] += 1
        if r["correct"]:
            a[0] += 1
    return {q: {"correct": c, "total": t} for q, (c, t) in agg.items()}


cases = {}
for r in decomposed["rows"]:
    case = cases.setdefault(r["case_id"], {"title": r["title"], "questions": {}})
    raw_path = root / "results/ischemic_decomposed" / f"{r['case_id']}_raw.json"
    raw = json.loads(raw_path.read_text())["answers"] if raw_path.exists() else {}
    sub_answers = {}
    for key, band in r["sub_answers"].items():
        entry = {"band": band}
        if key in raw:
            entry["confidence"] = raw[key].get("confidence")
            entry["probabilities"] = raw[key].get("probabilities")
        sub_answers[key] = entry
    outcome_id = (outcome_targets.get(r["case_id"], {}).get(r["question"]) or {}).get("outcome_id")
    sources, divergence = outcome_sources(outcome_id) if outcome_id else ([], None)
    case["questions"][r["question"]] = {
        "target_kind": r["target_kind"],
        "synthesized_kind": r["synthesized_kind"],
        "correct": r["correct"],
        "sub_answers": sub_answers,
        "targetOutcomeId": outcome_id,
        "sources": sources,
        "divergence": divergence,
    }

snapshot = {
    "singleShot": {"correct": single_shot["correct"], "total": 66, "byQuestion": by_question(single_shot["rows"])},
    "decomposed": {"correct": decomposed["correct"], "total": decomposed["total"], "byQuestion": by_question(decomposed["rows"])},
    "caseCount": len(cases),
    "cases": dict(sorted(cases.items())),
}
out.write_text(json.dumps(snapshot, indent=2) + "\n")
missing = sum(1 for c in cases.values() for q in c["questions"].values() if not q["sources"])
print(f"{out}: {snapshot['caseCount']} cases, decomposed {snapshot['decomposed']['correct']}/{snapshot['decomposed']['total']}, "
      f"single-shot {snapshot['singleShot']['correct']}/{snapshot['singleShot']['total']}, {missing} question(s) missing sources")
