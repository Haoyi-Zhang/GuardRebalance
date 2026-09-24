#!/usr/bin/env python3
"""Compare a reproduced campaign with the retained confirmation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VOLATILE_KEYS = {
    "resource", "cumulative_cpu_seconds", "maximum_process_peak_rss_kib",
    "driver_and_child_cpu_seconds", "driver_wall_seconds", "note",
}


def normalized(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in sorted(value.items()) if k not in VOLATILE_KEYS}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    errors = []
    reference_files = sorted(p.relative_to(args.reference) for p in args.reference.rglob("*") if p.is_file())
    candidate_files = sorted(p.relative_to(args.candidate) for p in args.candidate.rglob("*") if p.is_file())
    # Compare exact scientific inputs and deterministic JSON; presentation and
    # clean-reproduction metadata may be generated after the core campaign.
    relevant = [p for p in reference_files if p.parts[0] == "inputs" or p.suffix == ".json"]
    for rel in relevant:
        rp = args.reference / rel
        cp = args.candidate / rel
        if not cp.exists():
            errors.append(f"missing {rel}")
            continue
        if rel.parts[0] == "inputs" or rel.suffix != ".json":
            if rp.read_bytes() != cp.read_bytes():
                errors.append(f"byte mismatch {rel}")
        else:
            if normalized(json.loads(rp.read_text())) != normalized(json.loads(cp.read_text())):
                errors.append(f"JSON mismatch {rel}")
    extra_inputs = {
        p.relative_to(args.candidate) for p in args.candidate.rglob("inputs/*.json")
    } - {p for p in relevant if p.parts[0] == "inputs"}
    if extra_inputs:
        errors.append("unexpected retained inputs: " + ", ".join(map(str, sorted(extra_inputs))))
    report = {"accepted": not errors, "compared_files": len(relevant), "errors": errors}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
