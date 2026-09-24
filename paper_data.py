#!/usr/bin/env python3
"""Derive manuscript-facing CSV/TeX data from raw campaign JSON."""
from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

from pccfr.util import read_json, write_json


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    gap = read_json(args.results / "observer-gap.json")["records"]
    write_csv(args.out / "observer-gap.csv", ["input_bits", "inputs", "coarse_bytes", "refined_bytes", "expected_refined_bytes"], gap)
    baselines = read_json(args.results / "baselines.json")["records"]
    summaries = []
    for field in ("exact_private_tree", "fully_split", "origin_refined"):
        values = [r[field] for r in baselines]
        summaries.append({"method": field, "minimum": min(values), "median": statistics.median(values), "maximum": max(values)})
    branch = [r["branchless"] for r in baselines if r["branchless"] is not None]
    summaries.append({"method": "branchless_feasible_only", "minimum": min(branch) if branch else "", "median": statistics.median(branch) if branch else "", "maximum": max(branch) if branch else ""})
    write_csv(args.out / "baseline-summary.csv", ["method", "minimum", "median", "maximum"], summaries)
    counts = []
    for name in ("exhaustive", "two-state", "trees", "and-or", "graphs", "observer-gap", "baselines", "controls", "search", "padding", "many-relevant", "retained-input-replay"):
        data = read_json(args.results / f"{name}.json")
        counts.append({"phase": name, "mismatches": data.get("mismatches", 0), "cpu_seconds": f'{data["resource"]["cpu_seconds"]:.6f}', "peak_rss_kib": data["resource"]["peak_rss_kib"]})
    write_csv(args.out / "campaign-phases.csv", ["phase", "mismatches", "cpu_seconds", "peak_rss_kib"], counts)
    summary = read_json(args.results / "summary.json")
    macros = [
        f"\\newcommand{{\\SemanticComparisons}}{{{read_json(args.results / 'exhaustive.json')['semantic_comparisons']:,}}}",
        f"\\newcommand{{\\CertificateComparisons}}{{{read_json(args.results / 'exhaustive.json')['certificate_comparisons']:,}}}",
        f"\\newcommand{{\\ExactTreeInstances}}{{{read_json(args.results / 'trees.json')['instances']}}}",
        f"\\newcommand{{\\CampaignCPU}}{{{summary['cumulative_cpu_seconds']:.2f}}}",
        f"\\newcommand{{\\CampaignRSS}}{{{summary['maximum_process_peak_rss_kib'] // 1024}}}",
    ]
    (args.out / "results-macros.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")
    write_json(args.out / "presentation-summary.json", {"baseline_summary": summaries, "observer_gap": gap, "campaign": summary})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
