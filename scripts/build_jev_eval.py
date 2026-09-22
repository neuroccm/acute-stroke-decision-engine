#!/usr/bin/env python3
"""Bake a static snapshot of the Jev clinical-judgment eval into this repo.

Unlike scripts/sync-decision-tree.sh, this is a one-time snapshot of a
point-in-time evaluation writeup, not an ongoing sync target -- rerun it by
hand if TypeSafeWorkJev's results change, same as any other data file here.

Source: ~/Downloads/TypeSafeWorkJev/ClinicalEval (a separate, non-git-tracked
project directory). Reads only the two results/_summary.json files and the
per-case results/ischemic_decomposed/<id>_raw.json files -- never sends
anything anywhere, no network calls.

Usage: build_jev_eval.py <clinical_eval_dir> <out.json>
"""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
out = Path(sys.argv[2])

decomposed = json.loads((root / "results/ischemic_decomposed/_summary.json").read_text())
single_shot = json.loads((root / "results/ischemic/_summary.json").read_text())


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
    case["questions"][r["question"]] = {
        "target_kind": r["target_kind"],
        "synthesized_kind": r["synthesized_kind"],
        "correct": r["correct"],
        "sub_answers": sub_answers,
    }

snapshot = {
    "singleShot": {"correct": single_shot["correct"], "total": 66, "byQuestion": by_question(single_shot["rows"])},
    "decomposed": {"correct": decomposed["correct"], "total": decomposed["total"], "byQuestion": by_question(decomposed["rows"])},
    "caseCount": len(cases),
    "cases": dict(sorted(cases.items())),
}
out.write_text(json.dumps(snapshot, indent=2) + "\n")
print(f"{out}: {snapshot['caseCount']} cases, decomposed {snapshot['decomposed']['correct']}/{snapshot['decomposed']['total']}, single-shot {snapshot['singleShot']['correct']}/{snapshot['singleShot']['total']}")
