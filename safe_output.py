#!/usr/bin/env python3
"""Validate fresh project-local reproduction outputs without deleting data.

Every accepted output is a new direct child of ``artifact/results`` whose
basename begins with ``reproduced-``.  Existing paths (including broken
symlinks), symlinked project/result roots, ancestors, retained evidence, and
paths outside this project are rejected before any scientific command runs.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable


class UnsafeOutputPath(ValueError):
    """Raised when a reproduction output could overwrite or escape the project."""


def _lexists(path: Path) -> bool:
    return os.path.lexists(os.fspath(path))


def _absolute_lexical(path: Path) -> Path:
    """Normalize ``.``/``..`` without resolving symlinks."""
    return Path(os.path.abspath(os.fspath(path)))


def validate_paths(artifact_root: Path, paths: Iterable[Path]) -> list[Path]:
    supplied_root = _absolute_lexical(artifact_root)
    if not supplied_root.is_dir():
        raise UnsafeOutputPath(f"artifact root is not a directory: {supplied_root}")
    if supplied_root.is_symlink():
        raise UnsafeOutputPath(f"artifact root must not be a symbolic link: {supplied_root}")
    root = supplied_root.resolve(strict=True)

    results_lexical = supplied_root / "results"
    if not results_lexical.is_dir():
        raise UnsafeOutputPath(f"results directory is missing: {results_lexical}")
    if results_lexical.is_symlink():
        raise UnsafeOutputPath(f"results directory must not be a symbolic link: {results_lexical}")
    results = results_lexical.resolve(strict=True)
    if results.parent != root:
        raise UnsafeOutputPath("results directory is not the direct project child")

    protected = {
        root,
        results,
        (results / "confirmed").resolve(strict=False),
        (results / "presentation").resolve(strict=False),
    }
    accepted: list[Path] = []
    for supplied in paths:
        lexical = supplied if supplied.is_absolute() else supplied_root / supplied
        lexical = _absolute_lexical(lexical)

        # Direct-child membership is checked lexically and after resolving the
        # existing parent. This rejects traversal spellings and unrelated roots.
        if lexical.parent != results_lexical:
            raise UnsafeOutputPath(
                f"output must be a direct child of {results_lexical}: {lexical}"
            )
        if lexical.name in {"", ".", ".."} or not lexical.name.startswith("reproduced-"):
            raise UnsafeOutputPath(
                f"output basename must start with 'reproduced-': {lexical.name}"
            )
        if _lexists(lexical):
            raise UnsafeOutputPath(f"refusing existing output path: {lexical}")

        candidate = results / lexical.name
        if candidate in protected or candidate == root or candidate in root.parents:
            raise UnsafeOutputPath(f"protected project path: {candidate}")
        if candidate.parent != results:
            raise UnsafeOutputPath(f"output escapes project results directory: {candidate}")
        accepted.append(candidate)

    if not accepted:
        raise UnsafeOutputPath("at least one output path is required")
    if len(set(accepted)) != len(accepted):
        raise UnsafeOutputPath("output paths must be distinct")
    return accepted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    values = validate_paths(args.artifact_root, args.paths)
    for value in values:
        print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
