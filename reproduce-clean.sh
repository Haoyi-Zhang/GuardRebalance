#!/bin/sh
set -eu
cd "$(dirname "$0")"

OUT=${1:-results/reproduced-clean}
PRESENTATION=${2:-results/reproduced-clean-presentation}
REPLAY=${3:-results/reproduced-clean-input-replay.json}
VERIFY=${4:-results/reproduced-clean-verification.json}

# No cleanup command is used. Every output must be a new direct child of this
# project's results/ directory with the reproduced- prefix. Existing paths,
# symlinks, ancestors, retained results, and unrelated project paths are
# rejected before any scientific command runs.
python safe_output.py --artifact-root . "$OUT" "$PRESENTATION" "$REPLAY" "$VERIFY" >/dev/null

python -m unittest discover -s tests -v
python reproduce.py --out "$OUT"
python verify_results.py --reference results/confirmed --candidate "$OUT" > "$VERIFY"
python replay_inputs.py --reference results/confirmed --out "$REPLAY"
python paper_data.py --results "$OUT" --out "$PRESENTATION"
