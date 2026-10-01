#!/usr/bin/env python3
"""Compare a reproduced campaign with the retained confirmation.

The report separates three evidence layers: file loading/inventory, normalized
JSON reproduction, and exact PFC byte reproduction.  A missing file fails the
layer to which it belongs as well as the overall comparison.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VOLATILE_KEYS = {
    "resource",
    "cumulative_cpu_seconds",
    "maximum_process_peak_rss_kib",
    "driver_and_child_cpu_seconds",
    "driver_wall_seconds",
    "note",
}


def normalized(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalized(item) for key, item in sorted(value.items()) if key not in VOLATILE_KEYS}
    if isinstance(value, list):
        return [normalized(item) for item in value]
    return value


def _empty_report(errors: list[str]) -> dict[str, Any]:
    return {
        "accepted": False,
        "loading": {
            "status": "failed",
            "reference_files": 0,
            "candidate_files": 0,
            "retained_inputs": 0,
            "missing_json": [],
            "missing_pfc": [],
            "unexpected_files": [],
        },
        "numeric_json_reproduction": {"compared_files": 0, "status": "failed"},
        "pfc_byte_reproduction": {"compared_files": 0, "status": "failed"},
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()

    errors: list[str] = []
    if not args.reference.is_dir():
        errors.append("reference result directory is missing")
    if not args.candidate.is_dir():
        errors.append("candidate result directory is missing")
    if errors:
        print(json.dumps(_empty_report(errors), indent=2, sort_keys=True))
        return 1

    reference_files = sorted(path.relative_to(args.reference) for path in args.reference.rglob("*") if path.is_file())
    candidate_files = sorted(path.relative_to(args.candidate) for path in args.candidate.rglob("*") if path.is_file())
    relevant_json = [path for path in reference_files if path.suffix == ".json"]
    relevant_bytes = [path for path in reference_files if path.suffix == ".pfc"]
    retained_inputs = [
        path for path in reference_files
        if path.parts and path.parts[0] == "inputs" and path.suffix == ".json"
    ]

    loading_failed = False
    numeric_failed = False
    byte_failed = False
    missing_json: list[str] = []
    missing_pfc: list[str] = []

    if not retained_inputs:
        errors.append("reference retained-input directory is empty")
        loading_failed = True
    if not relevant_bytes:
        errors.append("reference contains no PFC object bytes")
        loading_failed = True
        byte_failed = True

    json_compared = 0
    byte_compared = 0
    for rel in relevant_json:
        reference_path = args.reference / rel
        candidate_path = args.candidate / rel
        if not candidate_path.is_file():
            errors.append(f"missing JSON {rel}")
            missing_json.append(str(rel))
            loading_failed = True
            numeric_failed = True
            continue
        try:
            reference_value = json.loads(reference_path.read_text(encoding="utf-8"))
            candidate_value = json.loads(candidate_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"JSON parse failure {rel}: {exc}")
            numeric_failed = True
            continue
        json_compared += 1
        if normalized(reference_value) != normalized(candidate_value):
            errors.append(f"JSON mismatch {rel}")
            numeric_failed = True

    for rel in relevant_bytes:
        reference_path = args.reference / rel
        candidate_path = args.candidate / rel
        if not candidate_path.is_file():
            errors.append(f"missing PFC {rel}")
            missing_pfc.append(str(rel))
            loading_failed = True
            byte_failed = True
            continue
        byte_compared += 1
        if reference_path.read_bytes() != candidate_path.read_bytes():
            errors.append(f"byte mismatch {rel}")
            byte_failed = True

    relevant_set = set(relevant_json) | set(relevant_bytes)
    candidate_relevant = {path for path in candidate_files if path.suffix in {".json", ".pfc"}}
    extra = sorted(candidate_relevant - relevant_set)
    if extra:
        errors.append("unexpected deterministic result files: " + ", ".join(map(str, extra)))
        loading_failed = True

    report = {
        "accepted": not errors,
        "loading": {
            "status": "failed" if loading_failed else "ok",
            "reference_files": len(reference_files),
            "candidate_files": len(candidate_files),
            "retained_inputs": len(retained_inputs),
            "missing_json": missing_json,
            "missing_pfc": missing_pfc,
            "unexpected_files": [str(path) for path in extra],
        },
        "numeric_json_reproduction": {
            "compared_files": json_compared,
            "status": "failed" if numeric_failed else "ok",
        },
        "pfc_byte_reproduction": {
            "compared_files": byte_compared,
            "status": "failed" if byte_failed else "ok",
        },
        "errors": errors,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
