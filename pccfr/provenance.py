"""Aggregate source/input binding for deterministic scientific results."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Iterable


def _aggregate(root: Path, files: Iterable[Path]) -> Dict[str, Any]:
    selected = sorted({path.resolve() for path in files if path.is_file()})
    digest = hashlib.sha256()
    total = 0
    for path in selected:
        rel = path.relative_to(root.resolve()).as_posix()
        data = path.read_bytes()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
        total += len(data)
    return {
        "algorithm": "sha256",
        "aggregate": digest.hexdigest(),
        "files": len(selected),
        "bytes": total,
    }


def scientific_source_summary(artifact_root: Path) -> Dict[str, Any]:
    root = artifact_root.resolve()
    files = list((root / "pccfr").glob("*.py"))
    files += list((root / "tests").glob("*.py"))
    files += [path for path in (root / "fixtures").rglob("*") if path.is_file()]
    for name in (
        "experiment.py",
        "paper_data.py",
        "replay_inputs.py",
        "reproduce.py",
        "run.py",
        "safe_output.py",
        "verify_results.py",
        "reproduce-clean.sh",
    ):
        path = root / name
        if path.exists():
            files.append(path)
    return _aggregate(root, files)


def input_summary(inputs: Path) -> Dict[str, Any]:
    inputs = inputs.resolve()
    files = sorted(inputs.glob("*.json"))
    summary = _aggregate(inputs, files)
    summary["families"] = {
        prefix: sum(path.stem.startswith(prefix + "-") for path in files)
        for prefix in ("exact", "baseline", "joint", "padding", "many")
    }
    return summary


def object_summary(objects: Path) -> Dict[str, Any]:
    objects = objects.resolve()
    return _aggregate(objects, objects.glob("*.pfc")) if objects.exists() else {
        "algorithm": "sha256", "aggregate": hashlib.sha256().hexdigest(), "files": 0, "bytes": 0
    }


def binding_id(source: Dict[str, Any], inputs: Dict[str, Any]) -> str:
    digest = hashlib.sha256()
    digest.update(source["aggregate"].encode("ascii"))
    digest.update(b"\0")
    digest.update(inputs["aggregate"].encode("ascii"))
    return digest.hexdigest()
