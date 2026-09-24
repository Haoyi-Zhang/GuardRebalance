#!/bin/sh
set -eu
cd "$(dirname "$0")"

OUT=${1:-results/reproduced}
PRESENTATION=${2:-results/reproduced-presentation}
REPLAY=${OUT%/}-input-replay.json

rm -rf "$OUT" "$PRESENTATION" "$REPLAY"
python -m unittest discover -s tests -v
python reproduce.py --out "$OUT"
python verify_results.py --reference results/confirmed --candidate "$OUT"
python replay_inputs.py --results "$OUT" --out "$REPLAY"
python paper_data.py --results "$OUT" --out "$PRESENTATION"
