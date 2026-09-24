#!/usr/bin/env python3
"""Run the complete bounded campaign sequentially with one worker.

The one-command driver executes phases in one bounded Python process.  Every
phase remains separately runnable through experiment.py for resumable hosts.
"""
from __future__ import annotations

import argparse
import resource
import time
from pathlib import Path

from pccfr.campaign import PHASES
from pccfr.util import measure, write_json

ORDER = list(PHASES)


def _apply_limits() -> None:
    # Project ceilings are 4 GiB and 45 minutes per individual run.  Keep a
    # margin for the host and stop well before either ceiling.
    address = 3_500 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (address, address))
    resource.setrlimit(resource.RLIMIT_CPU, (1800, 1800))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    _apply_limits()
    args.out.mkdir(parents=True, exist_ok=True)

    start_wall = time.monotonic()
    start_cpu = time.process_time()
    summaries = []
    for phase in ORDER:
        # Default-argument capture keeps the selected phase stable inside the
        # callback used by measure().
        result = measure(lambda selected=phase: PHASES[selected](args.out))
        write_json(args.out / f"{phase}.json", result)
        print(args.out / f"{phase}.json", flush=True)
        summaries.append(result)

    mismatches = sum(int(x.get("mismatches", 0)) for x in summaries)
    summary = {
        "phases": len(summaries),
        "phase_order": ORDER,
        "mismatches": mismatches,
        "cumulative_cpu_seconds": sum(float(x["resource"]["cpu_seconds"]) for x in summaries),
        "maximum_process_peak_rss_kib": max(int(x["resource"]["peak_rss_kib"]) for x in summaries),
        "workers": 1,
        "driver_and_child_cpu_seconds": time.process_time() - start_cpu,
        "driver_wall_seconds": time.monotonic() - start_wall,
    }
    write_json(args.out / "summary.json", summary)
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
