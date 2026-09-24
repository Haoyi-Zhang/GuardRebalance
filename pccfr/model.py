"""Finite snapshot-action semantics used by the artifact.

The model is deliberately small.  Every action's guard and raw outcome are
functions of the entry input; actions do not mutate values used by later
outcomes.  A false guard annuls the action before its raw outcome is observed.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Sequence, Tuple

Observation = Tuple[Tuple[Tuple[int, Any], ...], Tuple[str, Any]]
Cell = Tuple[int, int]  # (fixed_mask, fixed_value)


class ModelError(ValueError):
    """Raised when a model violates the public JSON contract."""


def freeze(value: Any) -> Any:
    """Convert JSON-like values to equality-stable immutable values."""
    if isinstance(value, list):
        return tuple(freeze(v) for v in value)
    if isinstance(value, dict):
        return tuple(sorted((str(k), freeze(v)) for k, v in value.items()))
    return value


def validate_model(model: Mapping[str, Any]) -> None:
    required = {"input_bits", "actions", "rows"}
    missing = required - set(model)
    if missing:
        raise ModelError(f"missing model keys: {sorted(missing)}")
    b = model["input_bits"]
    if not isinstance(b, int) or not (0 <= b <= 8):
        raise ModelError("input_bits must be an integer in [0, 8]")
    actions = model["actions"]
    if not isinstance(actions, list) or not actions:
        raise ModelError("actions must be a nonempty list")
    if actions != list(range(len(actions))):
        raise ModelError("actions must be consecutive integer identities starting at zero")
    if len(actions) > 65535:
        raise ModelError("the bytecode uses 16-bit action identities")
    rows = model["rows"]
    q = 1 << b
    if not isinstance(rows, list) or len(rows) != q:
        raise ModelError(f"rows must contain exactly {q} entries")
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ModelError("each row must be an object")
        x = row.get("input")
        if not isinstance(x, int) or not (0 <= x < q) or x in seen:
            raise ModelError("row inputs must be unique integers in range")
        seen.add(x)
        source = row.get("source")
        if source is None or sorted(source) != actions:
            raise ModelError("each source must be a full permutation of actions")
        outcomes = row.get("outcomes")
        if not isinstance(outcomes, list) or len(outcomes) != len(actions):
            raise ModelError("outcomes must have one entry per action")
        for out in outcomes:
            if not isinstance(out, dict):
                raise ModelError("outcomes must be objects")
            if not isinstance(out.get("guard"), bool):
                raise ModelError("outcome.guard must be Boolean")
            kind = out.get("kind")
            if kind not in {"silent", "emit", "fault"}:
                raise ModelError("outcome.kind must be silent, emit, or fault")
            if kind in {"emit", "fault"} and "value" not in out:
                raise ModelError("emit/fault outcomes require value")
    if seen != set(range(q)):
        raise ModelError("row inputs must form the complete entry-input domain")


def rows_by_input(model: Mapping[str, Any]) -> Dict[int, Mapping[str, Any]]:
    return {int(row["input"]): row for row in model["rows"]}


def observe(row: Mapping[str, Any], order: Sequence[int]) -> Observation:
    events: List[Tuple[int, Any]] = []
    outcomes = row["outcomes"]
    for action in order:
        out = outcomes[action]
        if not out["guard"]:
            continue
        kind = out["kind"]
        if kind == "silent":
            continue
        if kind == "emit":
            events.append((int(action), freeze(out["value"])))
            continue
        if kind == "fault":
            return (tuple(events), ("fault", freeze(out["value"])))
        raise AssertionError(f"validated model has unknown kind {kind!r}")
    return (tuple(events), ("return", None))


def source_observation(row: Mapping[str, Any]) -> Observation:
    return observe(row, row["source"])


def valid_on_rows(rows: Iterable[Mapping[str, Any]], order: Sequence[int]) -> bool:
    return all(observe(row, order) == source_observation(row) for row in rows)


def source_summary(row: Mapping[str, Any]) -> Dict[str, Any]:
    outcomes = row["outcomes"]
    fault_actions = {
        a for a, out in enumerate(outcomes) if out["guard"] and out["kind"] == "fault"
    }
    emission_actions = {
        a for a, out in enumerate(outcomes) if out["guard"] and out["kind"] == "emit"
    }
    prefix: List[int] = []
    terminal_signature: Any = None
    first_fault: int | None = None
    for a in row["source"]:
        out = outcomes[a]
        if not out["guard"]:
            continue
        if out["kind"] == "emit":
            prefix.append(int(a))
        elif out["kind"] == "fault":
            first_fault = int(a)
            terminal_signature = freeze(out["value"])
            break
    if first_fault is None:
        good: set[int] = set()
        returns = True
    else:
        good = {
            a
            for a in fault_actions
            if freeze(outcomes[a]["value"]) == terminal_signature
        }
        returns = False
    return {
        "prefix": tuple(prefix),
        "fault_actions": frozenset(fault_actions),
        "emission_actions": frozenset(emission_actions),
        "good": frozenset(good),
        "returns": returns,
        "signature": terminal_signature,
        "first_fault": first_fault,
    }


def cell_inputs(model: Mapping[str, Any], cell: Cell) -> List[int]:
    mask, value = cell
    q = 1 << int(model["input_bits"])
    return [x for x in range(q) if (x & mask) == value]


def cell_rows(model: Mapping[str, Any], cell: Cell) -> List[Mapping[str, Any]]:
    by_input = rows_by_input(model)
    return [by_input[x] for x in cell_inputs(model, cell)]


def split_cell(cell: Cell, bit: int) -> Tuple[Cell, Cell]:
    mask, value = cell
    bitmask = 1 << bit
    if mask & bitmask:
        raise ValueError("cannot split a cell on a fixed bit")
    new_mask = mask | bitmask
    return (new_mask, value & ~bitmask), (new_mask, value | bitmask)


def free_bits(model: Mapping[str, Any], cell: Cell) -> List[int]:
    mask, _ = cell
    return [i for i in range(int(model["input_bits"])) if not (mask & (1 << i))]


def partial_permutations(actions: Sequence[int]) -> Iterator[Tuple[int, ...]]:
    """Yield every non-repeating ordered subset, including the empty tuple."""
    values = tuple(actions)
    for length in range(len(values) + 1):
        yield from permutations(values, length)


def guard_vector(model: Mapping[str, Any], action: int) -> List[bool]:
    return [bool(row["outcomes"][action]["guard"]) for row in sorted(model["rows"], key=lambda r: r["input"])]


def guard_true_on_cell(model: Mapping[str, Any], action: int, cell: Cell) -> bool:
    return all(row["outcomes"][action]["guard"] for row in cell_rows(model, cell))


def guard_mask_bytes(model: Mapping[str, Any], action: int) -> bytes:
    q = 1 << int(model["input_bits"])
    width = (q + 7) // 8
    bits = 0
    for row in model["rows"]:
        if row["outcomes"][action]["guard"]:
            bits |= 1 << int(row["input"])
    return bits.to_bytes(width, "little")


def object_action_cost(model: Mapping[str, Any], action: int, cell: Cell) -> int:
    q = 1 << int(model["input_bits"])
    width = (q + 7) // 8
    return 3 if guard_true_on_cell(model, action, cell) else 3 + width
