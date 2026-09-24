#!/usr/bin/env python3
"""Optimize or check one finite snapshot-action model."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pccfr.bytecode import encode_object
from pccfr.certificate import check_certificate, make_certificate
from pccfr.model import validate_model
from pccfr.optimize import SearchRefusal, optimize_tree
from pccfr.util import atomic_write, read_json, write_json


def command_optimize(args: argparse.Namespace) -> int:
    model = read_json(args.model)
    validate_model(model)
    try:
        result = optimize_tree(model, leaf_mode=args.leaf_mode, candidate_limit=args.candidate_limit)
    except SearchRefusal as exc:
        write_json(args.out / "optimization.json", {
            "status": "refused", "mode": exc.mode, "candidates": exc.candidates,
            "candidate_limit": exc.limit,
        })
        return 2
    obj = encode_object(model, result["tree"])
    if len(obj) != result["object_cost"]:
        raise AssertionError("optimizer byte cost and encoder length disagree")
    cert = make_certificate(model, obj)
    args.out.mkdir(parents=True, exist_ok=True)
    atomic_write(args.out / "region.pfc", obj)
    write_json(args.out / "certificate.json", cert)
    write_json(args.out / "optimization.json", result)
    check = check_certificate(model, obj, cert, len(obj))
    write_json(args.out / "check.json", check)
    print(json.dumps({"object_size": len(obj), "accepted": check["accepted"]}, sort_keys=True))
    return 0 if check["accepted"] else 2


def command_check(args: argparse.Namespace) -> int:
    model = read_json(args.model)
    obj = args.object.read_bytes()
    cert = read_json(args.certificate)
    result = check_certificate(model, obj, cert, args.budget)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["accepted"] else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("optimize")
    p.add_argument("model", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--leaf-mode", choices=["auto", "optional_subset", "representative_tuple"], default="auto")
    p.add_argument("--candidate-limit", type=int, default=4096)
    p.set_defaults(func=command_optimize)
    p = sub.add_parser("check")
    p.add_argument("model", type=Path)
    p.add_argument("object", type=Path)
    p.add_argument("certificate", type=Path)
    p.add_argument("--budget", type=int, required=True)
    p.set_defaults(func=command_check)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
