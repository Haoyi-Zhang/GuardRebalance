#!/bin/sh
set -eu
cd "$(dirname "$0")"

OUT=${1:-results/reproduced-clean}
PRESENTATION=${2:-results/reproduced-clean-presentation}
REPLAY=${3:-results/reproduced-clean-input-replay.json}
VERIFY=${4:-results/reproduced-clean-verification.json}
SECOND=${5:-${OUT}-second}

# No cleanup command is used. Every output must be a new direct child of this
# project's results/ directory with the reproduced- prefix. Existing paths,
# symlinks, ancestors, retained results, and unrelated project paths are
# rejected before any scientific command runs.
python -B safe_output.py --artifact-root . "$OUT" "$PRESENTATION" "$REPLAY" "$VERIFY" "$SECOND" >/dev/null

python -B -m unittest discover -s tests -v
python -B -m unittest discover -s tests -p incidence_regression.py -v
python -B reproduce.py --out "$OUT"
python -B reproduce.py --out "$SECOND"
python -B verify_results.py --reference "$OUT" --candidate "$SECOND" > "$VERIFY"
python -B replay_inputs.py --reference "$OUT" --out "$REPLAY"
python -B paper_data.py --results "$OUT" --out "$PRESENTATION"
