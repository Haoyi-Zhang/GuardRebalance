#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
"$ROOT/artifact/reproduce-clean.sh"
"$ROOT/artifact/audits/run-reviewer-audit.sh"
