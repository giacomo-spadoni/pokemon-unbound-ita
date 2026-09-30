#!/usr/bin/env bash
# Build the Italian ROM from a translation JSON, verify it against the previous ROM,
# and create the BPS patch.   usage: bash out/build.sh <json> <out-name> <previous-rom>
# example: bash out/build.sh out/it-dlg.json fase3a out/eng-it.gba
set -e
cd "$(dirname "$0")/.."
JSON="$1"; NAME="$2"; PREV="$3"
python 005_hybrid_injector.py rom/unbound.gba "$JSON" -o "out/$NAME-it.gba" --target-lang it \
  --map-output "out/$NAME-map.json" --reclaim-script-slots --fail-on-no-space 2>&1 \
  | grep -E "Skipped no space|Remaining free|Encode errors|Pointer mismatches|Fixed truncated|No-reloc truncated|Ability desc|RuntimeError"
PYTHONIOENCODING=utf-8 python out/verify2.py "$PREV" "out/$NAME-it.gba" "$JSON"
python scripts/create_bps.py rom/unbound.gba "out/$NAME-it.gba" -o "out/unbound-it-$NAME.bps" | tail -1
echo "ROM: out/$NAME-it.gba   PATCH: out/unbound-it-$NAME.bps"
