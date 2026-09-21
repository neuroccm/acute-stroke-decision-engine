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
