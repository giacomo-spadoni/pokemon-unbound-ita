#!/usr/bin/env bash
# Full v7 build: dialogues + pronoun/megacheck fixes + v7 texts + graphics + Pokedex code, then BPS.
#   usage: bash out/build_v7.sh <name> <previous-rom>      e.g. bash out/build_v7.sh fase3q out/fase3o-it.gba
set -e
cd "$(dirname "$0")/.."
NAME="$1"; PREV="$2"
export PYTHONIOENCODING=utf-8
python out/dlg_tools.py apply out/it-eng.json out/it-dlg.json | tail -1
python out/pronoun_fix.py out/it-dlg.json out/it-pron.json
python out/v7_apply.py out/it-pron.json out/it-v7.json
bash out/build.sh out/it-v7.json "$NAME" "$PREV"
python out/v7_gfx.py "out/$NAME-it.gba" "out/$NAME-gfx.gba"
python out/v7_code.py "out/$NAME-gfx.gba" "out/$NAME-final.gba"
python scripts/create_bps.py rom/unbound.gba "out/$NAME-final.gba" -o "out/unbound-it-$NAME-final.bps" | tail -1
echo "ROM: out/$NAME-final.gba"
