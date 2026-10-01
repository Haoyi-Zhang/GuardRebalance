#!/usr/bin/env python3
"""Replay retained exact inputs by stable ID without regenerating them."""
from __future__ import annotations

import argparse
import resource
import time
from pathlib import Path
from typing import Any, Dict, Mapping

from pccfr.bytecode import encode_object
from pccfr.oracle import direct_tree_shape_optimum
from pccfr.optimize import (
    branchless_cost,
    direct_leaf_optimum,
    fully_split_cost,
    leaf_search_outcome,
    optimize_leaf,
    optimize_tree,
    origin_refined_model,
)
from pccfr.provenance import binding_id, input_summary, scientific_source_summary
from pccfr.util import read_json, write_json


FAMILY_COUNTS = {"exact": 130, "baseline": 64, "joint": 128, "padding": 64, "many": 5}


def _expected_ids() -> set[str]:
    return {
        f"{prefix}-{index:03d}"
        for prefix, count in FAMILY_COUNTS.items()
        for index in range(count)
    }


def _record_index(reference: Path, phase: str) -> Dict[str, Mapping[str, Any]]:
    data = read_json(reference / f"{phase}.json")
    records = data.get("records")
    if type(records) is not list:
        raise ValueError(f"{phase}.json has no record list")
    result: Dict[str, Mapping[str, Any]] = {}
    for record in records:
        if not isinstance(record, Mapping) or type(record.get("id")) is not str:
            raise ValueError(f"{phase}.json contains a record without a stable id")
        identifier = record["id"]
        if identifier in result:
            raise ValueError(f"duplicate stable id {identifier} in {phase}.json")
        result[identifier] = record
    return result


def _cost(value: Mapping[str, Any] | None) -> int | None:
    return None if value is None else int(value["cost"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() or args.out.is_symlink():
        raise SystemExit(f"refusing to overwrite existing replay report: {args.out}")

    start_cpu = time.process_time()
    start_wall = time.monotonic()
    errors: list[dict[str, Any]] = []
    inputs_dir = args.reference / "inputs"
    files = sorted(inputs_dir.glob("*.json")) if inputs_dir.is_dir() else []
    expected_ids = _expected_ids()
    actual_ids = {path.stem for path in files}
    missing = sorted(expected_ids - actual_ids)
    unexpected = sorted(actual_ids - expected_ids)
    if not files:
        errors.append({"stage": "loading", "error": "retained input directory is missing or empty"})
    if missing:
        errors.append({"stage": "loading", "error": "missing stable ids", "ids": missing})
    if unexpected:
        errors.append({"stage": "loading", "error": "unexpected stable ids", "ids": unexpected})

    try:
        trees = _record_index(args.reference, "trees")
        baselines = _record_index(args.reference, "baselines")
        search = _record_index(args.reference, "search")
        padding = _record_index(args.reference, "padding")
        many = _record_index(args.reference, "many-relevant")
    except Exception as exc:
        errors.append({"stage": "loading", "error": str(exc)})
        trees = baselines = search = padding = many = {}

    expected_record_ids = set(trees) | set(baselines) | set(search) | set(padding) | set(many)
    if expected_record_ids != expected_ids:
        errors.append({
            "stage": "loading",
            "error": "record stable-id set does not match retained inputs",
            "missing_record_ids": sorted(expected_ids - expected_record_ids),
            "extra_record_ids": sorted(expected_record_ids - expected_ids),
        })

    numeric_comparisons = 0
    byte_comparisons = 0
    family_loaded = {key: 0 for key in FAMILY_COUNTS}
    for path in files:
        identifier = path.stem
        prefix = identifier.split("-", 1)[0]
        if prefix not in family_loaded:
            continue
        family_loaded[prefix] += 1
        try:
            model = read_json(path)
            if prefix == "exact":
                expected = trees[identifier]
                fast = optimize_tree(model)
                oracle = direct_tree_shape_optimum(model)
                for field, actual in (
                    ("optimizer_status", fast["status"]),
                    ("optimizer_cost", fast["object_cost"]),
                    ("oracle_status", oracle["status"]),
                    ("oracle_cost", oracle["object_cost"]),
                ):
                    numeric_comparisons += 1
                    if expected.get(field) != actual:
                        errors.append({"stage": "numeric", "id": identifier, "field": field, "expected": expected.get(field), "actual": actual})
                object_path = args.reference / str(expected["object_file"])
                if not object_path.is_file():
                    errors.append({"stage": "loading", "id": identifier, "error": f"missing object {object_path}"})
                else:
                    actual_bytes = encode_object(model, fast["tree"])
                    byte_comparisons += 1
                    if actual_bytes != object_path.read_bytes():
                        errors.append({"stage": "bytes", "id": identifier, "error": "PFC object byte mismatch"})
            elif prefix == "baseline":
                expected = baselines[identifier]
                exact = optimize_tree(model)
                split = fully_split_cost(model)
                branchless = branchless_cost(model)
                refined = optimize_tree(origin_refined_model(model))
                actuals = {
                    "exact_private_tree": exact["object_cost"],
                    "fully_split": split,
                    "branchless_status": branchless["status"],
                    "branchless": branchless["object_cost"],
                    "branchless_search_mode": branchless.get("search_mode"),
                    "origin_refined": refined["object_cost"],
                }
                for field, actual in actuals.items():
                    numeric_comparisons += 1
                    if expected.get(field) != actual:
                        errors.append({"stage": "numeric", "id": identifier, "field": field, "expected": expected.get(field), "actual": actual})
            elif prefix == "joint":
                expected = search[identifier]
                direct = direct_leaf_optimum(model, (0, 0))
                methods = {
                    mode: optimize_leaf(model, (0, 0), mode, 4096)
                    for mode in ("auto", "optional_subset", "representative_tuple")
                }
                actuals = {"direct": _cost(direct), **{mode: _cost(value) for mode, value in methods.items()}}
                for field, actual in actuals.items():
                    numeric_comparisons += 1
                    if expected.get(field) != actual:
                        errors.append({"stage": "numeric", "id": identifier, "field": field, "expected": expected.get(field), "actual": actual})
                expected_modes = expected.get("actual_search_modes", {})
                for mode, value in methods.items():
                    actual_mode = None if value is None else value.get("search_mode")
                    numeric_comparisons += 1
                    if expected_modes.get(mode) != actual_mode:
                        errors.append({"stage": "numeric", "id": identifier, "field": f"actual_search_modes.{mode}", "expected": expected_modes.get(mode), "actual": actual_mode})
            elif prefix == "padding":
                expected = padding[identifier]
                value = optimize_leaf(model, (0, 0), "auto", 4096)
                numeric_comparisons += 1
                if expected.get("cost") != _cost(value):
                    errors.append({"stage": "numeric", "id": identifier, "field": "cost", "expected": expected.get("cost"), "actual": _cost(value)})
            elif prefix == "many":
                expected = many[identifier]
                for mode in ("auto", "representative_tuple", "optional_subset"):
                    outcome = leaf_search_outcome(model, (0, 0), mode, 4096)
                    expected_method = expected["methods"][mode]
                    for field, actual in (
                        ("status", outcome["status"]),
                        ("cost", outcome["cost"]),
                        ("actual_search_mode", outcome.get("search_mode")),
                    ):
                        numeric_comparisons += 1
                        if expected_method.get(field) != actual:
                            errors.append({"stage": "numeric", "id": identifier, "field": f"methods.{mode}.{field}", "expected": expected_method.get(field), "actual": actual})
        except Exception as exc:
            errors.append({"stage": "execution", "id": identifier, "error": f"{type(exc).__name__}: {exc}"})

    artifact_root = Path(__file__).resolve().parent
    source = scientific_source_summary(artifact_root)
    inputs = input_summary(inputs_dir) if inputs_dir.is_dir() else {"aggregate": None, "files": 0, "bytes": 0, "families": {}}
    current_binding = binding_id(source, inputs) if inputs.get("aggregate") else None
    retained_provenance = read_json(args.reference / "provenance.json") if (args.reference / "provenance.json").is_file() else None
    if retained_provenance is None:
        errors.append({"stage": "binding", "error": "missing provenance.json"})
    elif retained_provenance.get("binding_id") != current_binding:
        errors.append({
            "stage": "binding",
            "error": "retained source/input binding does not match current source and retained inputs",
            "expected": retained_provenance.get("binding_id"),
            "actual": current_binding,
        })

    report = {
        "accepted": not errors,
        "loading": {
            "status": "ok" if not any(error["stage"] == "loading" for error in errors) else "failed",
            "input_tables_loaded": len(files),
            "stable_ids_expected": len(expected_ids),
            "stable_ids_present": len(actual_ids),
            "families_loaded": family_loaded,
            "missing_ids": missing,
            "unexpected_ids": unexpected,
        },
        "numeric_reproduction": {
            "status": "ok" if not any(error["stage"] in {"numeric", "execution"} for error in errors) else "failed",
            "comparisons": numeric_comparisons,
        },
        "byte_reproduction": {
            "status": "ok" if not any(error["stage"] == "bytes" for error in errors) else "failed",
            "pfc_objects_compared": byte_comparisons,
        },
        "binding": {
            "status": "ok" if retained_provenance and retained_provenance.get("binding_id") == current_binding else "failed",
            "binding_id": current_binding,
            "source_summary": source,
            "input_summary": inputs,
        },
        "errors": errors,
        "resource": {
            "cpu_seconds": time.process_time() - start_cpu,
            "wall_seconds": time.monotonic() - start_wall,
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "workers": 1,
        },
    }
    write_json(args.out, report)
    print(args.out)
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
