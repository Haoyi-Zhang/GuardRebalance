#!/usr/bin/env python3
"""Derive manuscript-facing CSV/TeX data from bound campaign JSON."""
from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

from pccfr.util import read_json, write_json

PHASES = (
    "exhaustive", "two-state", "trees", "and-or", "graphs", "observer-gap",
    "baselines", "controls", "search", "padding", "many-relevant",
    "retained-input-replay",
)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def macro(name: str, value: object) -> str:
    return f"\\newcommand{{\\{name}}}{{{value}}}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() or args.out.is_symlink():
        raise SystemExit(f"refusing to overwrite existing presentation directory: {args.out}")
    args.out.mkdir(parents=True, exist_ok=False)

    summary = read_json(args.results / "summary.json")
    binding = summary["binding_id"]
    phase_data = {name: read_json(args.results / f"{name}.json") for name in PHASES}
    for name, data in phase_data.items():
        if data.get("binding_id") != binding:
            raise SystemExit(f"{name}.json is not bound to summary binding {binding}")
        if int(data.get("mismatches", 0)) != 0:
            raise SystemExit(f"{name}.json contains mismatches")

    gap = phase_data["observer-gap"]["records"]
    write_csv(
        args.out / "observer-gap.csv",
        ["input_bits", "inputs", "coarse_bytes", "refined_bytes", "expected_refined_bytes"],
        gap,
    )

    baselines = phase_data["baselines"]["records"]
    baseline_rows: list[dict] = []
    for field in ("exact_private_tree", "fully_split", "origin_refined"):
        values = [int(record[field]) for record in baselines]
        baseline_rows.append({
            "method": field,
            "minimum": min(values),
            "median": statistics.median(values),
            "maximum": max(values),
            "instances": len(values),
        })
    branch = [int(record["branchless"]) for record in baselines if record["branchless_status"] == "optimal"]
    baseline_rows.append({
        "method": "branchless_feasible_only",
        "minimum": min(branch) if branch else "",
        "median": statistics.median(branch) if branch else "",
        "maximum": max(branch) if branch else "",
        "instances": len(branch),
    })
    write_csv(
        args.out / "baseline-summary.csv",
        ["method", "minimum", "median", "maximum", "instances"],
        baseline_rows,
    )

    campaign_rows = []
    for name in PHASES:
        data = phase_data[name]
        campaign_rows.append({
            "phase": name,
            "mismatches": data.get("mismatches", 0),
            "cpu_seconds": f'{data["resource"]["cpu_seconds"]:.6f}',
            "peak_rss_kib": data["resource"]["peak_rss_kib"],
            "binding_id": binding,
        })
    write_csv(
        args.out / "campaign-phases.csv",
        ["phase", "mismatches", "cpu_seconds", "peak_rss_kib", "binding_id"],
        campaign_rows,
    )

    exhaustive = phase_data["exhaustive"]
    trees = phase_data["trees"]
    andor = phase_data["and-or"]
    controls = phase_data["controls"]
    replay = phase_data["retained-input-replay"]
    macros = [
        macro("SemanticComparisons", f'{exhaustive["semantic_comparisons"]:,}'),
        macro("WitnessChecks", f'{exhaustive["witness_existence_checks"]:,}'),
        macro("CertificateObjectReplays", f'{exhaustive["certificate_object_replays"]:,}'),
        macro("CertificateFrontierRows", f'{exhaustive["certificate_frontier_row_checks"]:,}'),
        macro("CertificateDirectRows", f'{exhaustive["certificate_direct_row_checks"]:,}'),
        macro("ExactTreeInstances", trees["instances"]),
        macro("SemanticWaitingFamilies", andor["semantic_snapshot_models"]),
        macro("SemanticWaitingPermutations", f'{andor["semantic_permutation_comparisons"]:,}'),
        macro("DirectedControls", controls["cases"]),
        macro("RetainedInputs", replay["input_tables_loaded"]),
        macro("CampaignCPU", f'{summary["cumulative_cpu_seconds"]:.2f}'),
        macro("CampaignRSS", summary["maximum_process_peak_rss_kib"] // 1024),
    ]
    (args.out / "results-macros.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")
    write_json(args.out / "presentation-summary.json", {
        "binding_id": binding,
        "baseline_summary": baseline_rows,
        "observer_gap": gap,
        "campaign": summary,
        "evidence_layers": {
            "direct_semantic_comparisons": exhaustive["semantic_comparisons"],
            "witness_existence_checks": exhaustive["witness_existence_checks"],
            "object_certificate_replays": exhaustive["certificate_object_replays"],
            "independent_tree_instances": trees["independent_tree_instances"],
            "independent_tree_shapes_enumerated": trees["independent_tree_shapes_enumerated"],
            "semantic_waiting_models": andor["semantic_snapshot_models"],
            "semantic_waiting_permutation_comparisons": andor["semantic_permutation_comparisons"],
            "retained_input_tables": replay["input_tables_loaded"],
        },
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
