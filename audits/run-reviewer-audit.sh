#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PY=${PYTHON:-python3}
$PY "$ROOT/artifact/audits/tools/reference_audit.py" "$ROOT" \
  --cache "$ROOT/artifact/audits/reference/registry-cache.json" \
  --out "$ROOT/artifact/audits/reference"
$PY "$ROOT/artifact/audits/tools/project_audit.py" "$ROOT" --skip-reproduce
$PY "$ROOT/artifact/audits/tools/independence_audit.py" "$ROOT"
$PY "$ROOT/artifact/audits/tools/theorem_audit.py" "$ROOT"
$PY "$ROOT/artifact/audits/tools/experiment_audit.py" "$ROOT"
$PY "$ROOT/artifact/robustness.py"
$PY "$ROOT/artifact/audits/tools/claim_provenance_audit.py" "$ROOT"
$PY "$ROOT/artifact/audits/tools/reference_quality_audit.py" "$ROOT"
$PY "$ROOT/artifact/audits/tools/style_audit.py" "$ROOT"
$PY "$ROOT/artifact/audits/tools/venue_audit.py" "$ROOT"
$PY "$ROOT/artifact/audits/tools/supply_chain_audit.py" "$ROOT"
if [ "${PCCFR_FULL_REVIEW:-0}" = "1" ]; then
  $PY "$ROOT/artifact/audits/tools/mutation_guard.py" "$ROOT"
fi
if command -v pdfinfo >/dev/null 2>&1 && [ -f "$ROOT/paper/main.pdf" ]; then
  $PY "$ROOT/artifact/audits/tools/pdf_audit.py" "$ROOT"
fi
$PY - <<'PY' "$ROOT"
from pathlib import Path
import json,sys
root=Path(sys.argv[1])
paths={
 'references':root/'artifact/audits/reference/reference-audit.json',
 'project':root/'artifact/audits/blind-review/project-audit.json',
 'independence':root/'artifact/audits/blind-review/independence-audit.json',
 'pdf':root/'artifact/audits/paper/pdf-audit.json',
 'theorems':root/'artifact/audits/paper/theorem-audit.json',
 'experiments':root/'artifact/audits/experiments/experiment-audit.json',
 'robustness':root/'artifact/audits/experiments/robustness.json',
 'claim_provenance':root/'artifact/audits/paper/claim-provenance-audit.json',
 'reference_quality':root/'artifact/audits/reference/reference-quality-audit.json',
 'style':root/'artifact/audits/paper/style-audit.json',
 'venue':root/'artifact/audits/paper/venue-audit.json',
 'supply_chain':root/'artifact/audits/supply-chain/supply-chain-audit.json',
}
mut=root/'artifact/audits/tests/mutation-guard.json'
if mut.exists(): paths['mutation_guard']=mut
parts={k:json.loads(p.read_text()) for k,p in paths.items() if p.exists()}
accepted=all(v.get('accepted') is True for v in parts.values()) and set(parts)==set(paths)
out={'accepted':accepted,'components':{k:{'accepted':v.get('accepted')} for k,v in parts.items()},'missing':[k for k,p in paths.items() if not p.exists()]}
(root/'artifact/audits/reviewer-gate.json').write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,sort_keys=True))
if not accepted: raise SystemExit(1)
PY
