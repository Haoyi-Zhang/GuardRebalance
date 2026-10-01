#!/usr/bin/env python3
"""Optimize or check one finite snapshot-action model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pccfr.bytecode import ObjectFormatError, encode_object
from pccfr.certificate import check_certificate, make_certificate
from pccfr.model import ModelError, validate_model
from pccfr.optimize import SearchRefusal, optimize_tree
from pccfr.util import StrictJSONError, atomic_write, read_json, write_json


def _print_rejection(reason: str, detail: str) -> int:
    print(json.dumps({"accepted": False, "reason": reason, "detail": detail}, indent=2, sort_keys=True))
    return 2


def command_optimize(args: argparse.Namespace) -> int:
    if args.out.exists() or args.out.is_symlink():
        return _print_rejection("unsafe-output", f"refusing existing output path: {args.out}")
    try:
        model = read_json(args.model)
        validate_model(model)
    except (StrictJSONError, ModelError, OSError) as exc:
        args.out.mkdir(parents=True, exist_ok=True)
        write_json(args.out / "optimization.json", {"status": "invalid-model", "detail": str(exc)})
        return _print_rejection("invalid-model", str(exc))
    try:
        result = optimize_tree(model, leaf_mode=args.leaf_mode, candidate_limit=args.candidate_limit)
    except SearchRefusal as exc:
        args.out.mkdir(parents=True, exist_ok=True)
        write_json(args.out / "optimization.json", {
            "status": "refused",
            "mode": exc.mode,
            "candidates": exc.candidates,
            "candidate_limit": exc.limit,
            "refusals": exc.refusals,
        })
        return _print_rejection("search-refused", str(exc))
    if result["status"] != "optimal" or result["tree"] is None:
        args.out.mkdir(parents=True, exist_ok=True)
        write_json(args.out / "optimization.json", result)
        return _print_rejection(result["status"], "no certified optimal tree")
    try:
        obj = encode_object(model, result["tree"])
    except ObjectFormatError as exc:
        return _print_rejection("invalid-object", str(exc))
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
    try:
        model = read_json(args.model)
        obj = args.object.read_bytes()
        cert = read_json(args.certificate)
    except (StrictJSONError, OSError) as exc:
        return _print_rejection("invalid-input", str(exc))
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
