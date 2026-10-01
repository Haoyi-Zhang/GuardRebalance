#!/usr/bin/env python3
"""Run one deterministic confirmation phase."""
from __future__ import annotations

import argparse
import resource
from pathlib import Path

from pccfr.campaign import PHASES
from pccfr.util import measure, write_json


def _apply_limits() -> None:
    """Apply per-phase ceilings in the child process itself.

    Doing this after exec avoids the documented hazards of subprocess
    preexec_fn while still bounding every scientific phase.
    """
    address = 3_500 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (address, address))
    resource.setrlimit(resource.RLIMIT_CPU, (1800, 1800))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=sorted(PHASES))
    parser.add_argument("--out", type=Path, required=True)
    # Compatibility-only option documented for the bounded exhaustive phase.
    parser.add_argument("--actions", type=int, default=None)
    args = parser.parse_args()
    _apply_limits()
    if args.out.exists() or args.out.is_symlink():
        raise SystemExit(f"refusing to overwrite existing phase output directory: {args.out}")
    args.out.mkdir(parents=True, exist_ok=False)
    result = measure(lambda: PHASES[args.phase](args.out))
    write_json(args.out / f"{args.phase}.json", result)
    print(args.out / f"{args.phase}.json")
    return 0 if result.get("mismatches", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
