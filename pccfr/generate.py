"""Deterministic finite models used by the confirmation campaign."""
from __future__ import annotations

import copy
import itertools
import math
import random
from typing import Any, Dict, Iterable, List, Sequence, Tuple


def silent(guard: bool = True) -> Dict[str, Any]:
    return {"guard": guard, "kind": "silent"}


def emit(value: Any = 0, guard: bool = True) -> Dict[str, Any]:
    return {"guard": guard, "kind": "emit", "value": value}


def fault(value: Any = 0, guard: bool = True) -> Dict[str, Any]:
    return {"guard": guard, "kind": "fault", "value": value}


def effective_outcome(code: int) -> Dict[str, Any]:
    if code == 0:
        return fault(0, False)
    if code == 1:
        return silent(True)
    if code == 2:
        return emit(0, True)
    if code == 3:
        return fault(0, True)
    if code == 4:
        return fault(1, True)
    raise ValueError(code)


def one_row_profile(codes: Sequence[int], source: Sequence[int] | None = None) -> Dict[str, Any]:
    n = len(codes)
    return {
        "input_bits": 0,
        "actions": list(range(n)),
        "rows": [{
            "input": 0,
            "source": list(range(n) if source is None else source),
            "outcomes": [effective_outcome(c) for c in codes],
        }],
    }


def two_row_profiles(
    codes0: Sequence[int], codes1: Sequence[int], source0: Sequence[int], source1: Sequence[int]
) -> Dict[str, Any]:
    n = len(codes0)
    return {
        "input_bits": 1,
        "actions": list(range(n)),
        "rows": [
            {"input": 0, "source": list(source0), "outcomes": [effective_outcome(c) for c in codes0]},
            {"input": 1, "source": list(source1), "outcomes": [effective_outcome(c) for c in codes1]},
        ],
    }


def random_model(seed: int, input_bits: int, actions: int, common_source: bool = False) -> Dict[str, Any]:
    rng = random.Random(seed)
    action_ids = list(range(actions))
    base_source = action_ids[:]
    rng.shuffle(base_source)
    rows = []
    for x in range(1 << input_bits):
        source = base_source[:] if common_source else action_ids[:]
        if not common_source:
            rng.shuffle(source)
        outcomes = []
        for a in action_ids:
            code = rng.randrange(5)
            out = effective_outcome(code)
            if out["kind"] == "emit":
                out["value"] = [x % 3, a % 2]
            elif out["kind"] == "fault" and out["guard"]:
                out["value"] = rng.randrange(3)
            outcomes.append(out)
        rows.append({"input": x, "source": source, "outcomes": outcomes})
    return {"input_bits": input_bits, "actions": action_ids, "rows": rows}


def graph_model(n: int, edges: Sequence[Tuple[int, int]]) -> Dict[str, Any]:
    if not edges:
        raise ValueError("graph model requires a nonempty edge set")
    b = math.ceil(math.log2(len(edges))) if len(edges) > 1 else 0
    q = 1 << b
    rows = []
    actions = list(range(n))
    for x in range(q):
        u, v = edges[x % len(edges)]
        source = [u, v] + [a for a in actions if a not in {u, v}]
        outcomes = [silent(False) for _ in actions]
        outcomes[u] = fault("edge", True)
        outcomes[v] = fault("edge", True)
        rows.append({"input": x, "source": source, "outcomes": outcomes})
    return {"input_bits": b, "actions": actions, "rows": rows}


def graph_edges(n: int, mask: int) -> List[Tuple[int, int]]:
    all_edges = list(itertools.combinations(range(n), 2))
    return [edge for i, edge in enumerate(all_edges) if mask & (1 << i)]


def observer_gap_model(bits: int) -> Dict[str, Any]:
    m = 1 << bits
    actions = list(range(m))
    rows = []
    for x in range(m):
        source = [x] + [a for a in actions if a != x]
        outcomes = [fault("coarse", True) for _ in actions]
        rows.append({"input": x, "source": source, "outcomes": outcomes})
    return {"input_bits": bits, "actions": actions, "rows": rows}


def pad_actions(model: Dict[str, Any], total_actions: int) -> Dict[str, Any]:
    out = copy.deepcopy(model)
    old = len(out["actions"])
    if total_actions < old:
        raise ValueError("cannot shrink with pad_actions")
    out["actions"] = list(range(total_actions))
    for row in out["rows"]:
        row["source"].extend(range(old, total_actions))
        row["outcomes"].extend(silent(True) for _ in range(old, total_actions))
    return out


def many_relevant_model(n: int) -> Dict[str, Any]:
    if n < 2 or n % 2:
        raise ValueError("n must be even")
    half = n // 2
    actions = list(range(n))
    rows = []
    for x in range(2):
        good = set(range(0, half) if x == 0 else range(half, n))
        source_first = min(good)
        source = [source_first] + [a for a in actions if a != source_first]
        outcomes = [fault(f"k{x}", True) if a in good else silent(True) for a in actions]
        rows.append({"input": x, "source": source, "outcomes": outcomes})
    return {"input_bits": 1, "actions": actions, "rows": rows}


def feasible_random_model(seed: int, input_bits: int = 2, actions: int = 5) -> Dict[str, Any]:
    """Random model with a common source, so at least one full leaf is valid."""
    return random_model(seed, input_bits, actions, common_source=True)
