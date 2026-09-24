#!/usr/bin/env python3
"""Directly replay retained exact JSON tables without regenerating them."""
from __future__ import annotations

import argparse
import resource
import time
from pathlib import Path

from pccfr.optimize import SearchRefusal, direct_leaf_optimum, optimize_leaf, optimize_tree
from pccfr.util import read_json, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    start_cpu = time.process_time(); start_wall = time.monotonic()
    files = sorted((args.results / "inputs").glob("*.json"))
    counts = {"exact": 0, "baseline": 0, "joint": 0, "padding": 0, "many": 0}
    mismatches = 0
    joint_matches = 0
    admitted = 0
    refusals = 0
    for p in files:
        model = read_json(p)
        prefix = p.stem.split("-", 1)[0]
        counts[prefix] += 1
        if prefix == "exact":
            fast = optimize_tree(model)
            oracle = optimize_tree(model, direct_leaf=True)
            mismatches += int(fast["object_cost"] != oracle["object_cost"])
        elif prefix == "baseline":
            optimize_tree(model)
        elif prefix == "joint":
            direct = direct_leaf_optimum(model, (0, 0))
            expected = None if direct is None else direct["cost"]
            for mode in ("auto", "optional_subset", "representative_tuple"):
                got = optimize_leaf(model, (0, 0), mode, 4096)
                joint_matches += int((None if got is None else got["cost"]) == expected)
                mismatches += int((None if got is None else got["cost"]) != expected)
        elif prefix == "padding":
            optimize_leaf(model, (0, 0), "auto", 4096)
        elif prefix == "many":
            for mode in ("auto", "representative_tuple", "optional_subset"):
                try:
                    optimize_leaf(model, (0, 0), mode, 4096)
                    admitted += 1
                except SearchRefusal:
                    refusals += 1
    report = {
        "input_acquisition": "retained exact JSON tables; no pseudorandom generation",
        "input_tables_loaded": len(files),
        "exact_tree_instances": counts["exact"],
        "baseline_instances": counts["baseline"],
        "joint_leaf_instances": counts["joint"],
        "padding_instances": counts["padding"],
        "many_relevant_instances": counts["many"],
        "joint_method_optimum_matches": joint_matches,
        "admitted_many_relevant_methods": admitted,
        "explicit_candidate_space_refusals": refusals,
        "mismatches": mismatches,
        "resource": {
            "cpu_seconds": time.process_time() - start_cpu,
            "wall_seconds": time.monotonic() - start_wall,
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "workers": 1,
        },
    }
    write_json(args.out, report)
    print(args.out)
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
