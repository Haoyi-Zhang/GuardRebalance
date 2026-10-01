"""Finite snapshot-action semantics used by the artifact.

The model is deliberately small. Every action's inherited guard and raw
outcome are immutable functions of the entry input; actions do not mutate
values used by later outcomes. A false guard annuls the action before its raw
outcome is observed. Observable payloads are strict finite JSON values.
"""
from __future__ import annotations

import json
import math
from itertools import permutations
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Sequence, Tuple

Observation = Tuple[Tuple[Tuple[int, str], ...], Tuple[str, str | None]]
Cell = Tuple[int, int]  # (fixed_mask, fixed_value)


class ModelError(ValueError):
    """Raised when a model violates the public JSON contract."""


def _validate_json_value(value: Any, path: str, active: set[int], depth: int) -> None:
    """Validate the declared finite JSON signature domain.

    The semantic domain distinguishes every JSON kind: null, Boolean, integer,
    finite floating-point number, string, array, and object. Objects have string
    keys. In-memory cycles and non-JSON Python values are rejected even though a
    conforming JSON parser cannot construct them.
    """
    if depth > 64:
        raise ModelError(f"{path} exceeds the maximum JSON nesting depth")
    if value is None or type(value) is bool or type(value) is int or type(value) is str:
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ModelError(f"{path} must not contain NaN or infinity")
        return
    if type(value) is list:
        ident = id(value)
        if ident in active:
            raise ModelError(f"{path} contains a cycle")
        active.add(ident)
        try:
            for index, item in enumerate(value):
                _validate_json_value(item, f"{path}[{index}]", active, depth + 1)
        finally:
            active.remove(ident)
        return
    if type(value) is dict:
        ident = id(value)
        if ident in active:
            raise ModelError(f"{path} contains a cycle")
        active.add(ident)
        try:
            for key, item in value.items():
                if type(key) is not str:
                    raise ModelError(f"{path} object keys must be strings")
                _validate_json_value(item, f"{path}.{key}", active, depth + 1)
        finally:
            active.remove(ident)
        return
    raise ModelError(f"{path} contains unsupported non-JSON value type {type(value).__name__}")


def validate_json_value(value: Any, path: str = "value") -> None:
    _validate_json_value(value, path, set(), 0)


def freeze(value: Any) -> Any:
    """Return a type-tagged, immutable structural signature.

    Type tags are essential: without them, Python tuple equality merges ``{}``
    with ``[]``, an object with an array of key/value pairs, and ``False`` with
    ``0``. The frontier construction uses this representation only after model
    validation.
    """
    if value is None:
        return ("null",)
    if type(value) is bool:
        return ("bool", value)
    if type(value) is int:
        return ("integer", value)
    if type(value) is float:
        if not math.isfinite(value):
            raise ModelError("signature number must be finite")
        return ("float", value.hex())
    if type(value) is str:
        return ("string", value)
    if type(value) is list:
        return ("array", tuple(freeze(v) for v in value))
    if type(value) is dict:
        return ("object", tuple(sorted((k, freeze(v)) for k, v in value.items())))
    raise ModelError(f"signature contains unsupported non-JSON value type {type(value).__name__}")


def canonical_json(value: Any) -> str:
    """Independent direct-trace representation of a validated JSON value.

    This path deliberately does not reuse :func:`freeze`: direct execution and
    the frontier derivation therefore do not share the same equality encoding.
    """
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise ModelError(f"value is not strict finite JSON: {exc}") from exc


def validate_model(model: Mapping[str, Any]) -> None:
    if not isinstance(model, Mapping):
        raise ModelError("model must be an object")
    required = {"input_bits", "actions", "rows"}
    keys = set(model)
    if keys != required:
        missing = sorted(required - keys)
        extra = sorted(keys - required)
        raise ModelError(f"model fields do not match the closed schema; missing={missing}, extra={extra}")
    b = model["input_bits"]
    if type(b) is not int or not (0 <= b <= 8):
        raise ModelError("input_bits must be an integer in [0, 8]")
    actions = model["actions"]
    if type(actions) is not list or not actions:
        raise ModelError("actions must be a nonempty list")
    if any(type(action) is not int for action in actions):
        raise ModelError("action identities must be integers, not Booleans or reals")
    if actions != list(range(len(actions))):
        raise ModelError("actions must be consecutive integer identities starting at zero")
    if len(actions) > 65535:
        raise ModelError("the bytecode uses 16-bit action identities")
    rows = model["rows"]
    q = 1 << b
    if type(rows) is not list or len(rows) != q:
        raise ModelError(f"rows must contain exactly {q} entries")
    seen = set()
    for row_index, row in enumerate(rows):
        if type(row) is not dict:
            raise ModelError("each row must be an object")
        row_keys = set(row)
        row_required = {"input", "source", "outcomes"}
        if row_keys != row_required:
            raise ModelError(
                "row fields do not match the closed schema; "
                f"missing={sorted(row_required - row_keys)}, extra={sorted(row_keys - row_required)}"
            )
        x = row.get("input")
        if type(x) is not int or not (0 <= x < q) or x in seen:
            raise ModelError("row inputs must be unique integers in range")
        seen.add(x)
        source = row.get("source")
        if type(source) is not list:
            raise ModelError("each source must be a list permutation of actions")
        if any(type(action) is not int for action in source):
            raise ModelError("source action identities must be integers, not Booleans or reals")
        if len(source) != len(actions) or sorted(source) != actions:
            raise ModelError("each source must be a full permutation of actions")
        outcomes = row.get("outcomes")
        if type(outcomes) is not list or len(outcomes) != len(actions):
            raise ModelError("outcomes must have one entry per action")
        for action, out in enumerate(outcomes):
            if type(out) is not dict:
                raise ModelError("outcomes must be objects")
            if type(out.get("guard")) is not bool:
                raise ModelError("outcome.guard must be Boolean")
            kind = out.get("kind")
            if kind not in {"silent", "emit", "fault"}:
                raise ModelError("outcome.kind must be silent, emit, or fault")
            required_outcome = {"guard", "kind"} if kind == "silent" else {"guard", "kind", "value"}
            outcome_keys = set(out)
            if outcome_keys != required_outcome:
                raise ModelError(
                    "outcome fields do not match the closed schema; "
                    f"missing={sorted(required_outcome - outcome_keys)}, "
                    f"extra={sorted(outcome_keys - required_outcome)}"
                )
            if kind in {"emit", "fault"}:
                validate_json_value(out["value"], f"rows[{row_index}].outcomes[{action}].value")
    if seen != set(range(q)):
        raise ModelError("row inputs must form the complete entry-input domain")


def rows_by_input(model: Mapping[str, Any]) -> Dict[int, Mapping[str, Any]]:
    return {int(row["input"]): row for row in model["rows"]}


def order_in_domain(row: Mapping[str, Any], order: Sequence[int]) -> bool:
    """Whether ``order`` is a duplicate-free ordered subset of the row domain."""
    if isinstance(order, (str, bytes, bytearray)):
        return False
    try:
        values = list(order)
    except TypeError:
        return False
    n = len(row.get("outcomes", ()))
    if any(type(action) is not int or not (0 <= action < n) for action in values):
        return False
    return len(set(values)) == len(values)


def observe(row: Mapping[str, Any], order: Sequence[int]) -> Observation:
    if not order_in_domain(row, order):
        raise ModelError("target order must be a duplicate-free ordered subset of the action domain")
    events: List[Tuple[int, str]] = []
    outcomes = row["outcomes"]
    for action in order:
        out = outcomes[action]
        if not out["guard"]:
            continue
        kind = out["kind"]
        if kind == "silent":
            continue
        if kind == "emit":
            events.append((action, canonical_json(out["value"])))
            continue
        if kind == "fault":
            return (tuple(events), ("fault", canonical_json(out["value"])))
        raise AssertionError(f"validated model has unknown kind {kind!r}")
    return (tuple(events), ("return", None))


def source_observation(row: Mapping[str, Any]) -> Observation:
    return observe(row, row["source"])


def valid_on_rows(rows: Iterable[Mapping[str, Any]], order: Sequence[int]) -> bool:
    rows_list = list(rows)
    if rows_list and not order_in_domain(rows_list[0], order):
        return False
    return all(observe(row, order) == source_observation(row) for row in rows_list)


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
            prefix.append(a)
        elif out["kind"] == "fault":
            first_fault = a
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
    """Encode guards with input x in bit (x mod 8), least-significant bit first."""
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
