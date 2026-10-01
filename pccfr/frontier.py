"""Fault-frontier characterization and constraint extraction."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set, Tuple

from .model import observe, order_in_domain, source_observation, source_summary

Waiting = Tuple[frozenset[int], int]


def _positions(order: Sequence[int]) -> Dict[int, int]:
    return {a: i for i, a in enumerate(order)}


def frontier_valid(row: Mapping[str, Any], order: Sequence[int]) -> bool:
    """Implement Theorem 1 directly."""
    if not order_in_domain(row, order):
        return False
    summary = source_summary(row)
    selected = set(order)
    pos = _positions(order)
    prefix = summary["prefix"]

    # 1. Coverage of the uniquely tagged source prefix.
    if any(a not in selected for a in prefix):
        return False
    # 2. Prefix order.
    if any(pos[a] >= pos[b] for a, b in zip(prefix, prefix[1:])):
        return False
    if summary["returns"]:
        return True

    good = set(summary["good"])
    faults = set(summary["fault_actions"])
    emissions = set(summary["emission_actions"])

    # 3. At least one acceptable selected fault.
    selected_good = selected & good
    if not selected_good:
        return False
    # 4. Every selected enabled fault waits for the last required emission.
    if prefix:
        last = prefix[-1]
        if any(pos[last] >= pos[f] for f in selected & faults):
            return False
    # 5. Each selected barrier has an earlier acceptable fault.
    barriers = ((emissions - set(prefix)) | (faults - good)) & selected
    for barrier in barriers:
        if not any(pos[g] < pos[barrier] for g in selected_good):
            return False
    return True


def direct_and_frontier_agree(row: Mapping[str, Any], order: Sequence[int]) -> bool:
    return frontier_valid(row, order) == (observe(row, order) == source_observation(row))


def witness_valid(row: Mapping[str, Any], order: Sequence[int], witness: int | None) -> bool:
    """Check the compact one-witness certificate obligations for one input."""
    if not order_in_domain(row, order):
        return False
    summary = source_summary(row)
    selected = set(order)
    pos = _positions(order)
    prefix = summary["prefix"]
    if any(a not in selected for a in prefix):
        return False
    if any(pos[a] >= pos[b] for a, b in zip(prefix, prefix[1:])):
        return False
    if summary["returns"]:
        return witness is None
    if witness is None or witness not in selected or witness not in summary["good"]:
        return False
    if prefix:
        last = prefix[-1]
        if any(pos[last] >= pos[f] for f in selected & set(summary["fault_actions"])):
            return False
    barriers = (
        (set(summary["emission_actions"]) - set(prefix))
        | (set(summary["fault_actions"]) - set(summary["good"]))
    ) & selected
    return all(pos[witness] < pos[v] for v in barriers)


def canonical_witness(row: Mapping[str, Any], order: Sequence[int]) -> int | None:
    """Return the first selected enabled fault, or None for normal return.

    For a valid faulting order this action is necessarily an acceptable fault.
    """
    if not order_in_domain(row, order):
        return None
    summary = source_summary(row)
    if summary["returns"]:
        return None
    outcomes = row["outcomes"]
    for a in order:
        out = outcomes[a]
        if out["guard"] and out["kind"] == "fault":
            return int(a)
    return None


def requirements(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    summaries = [source_summary(row) for row in rows]
    prefix_union: Set[int] = set()
    good_sets: List[frozenset[int]] = []
    for summary in summaries:
        prefix_union.update(summary["prefix"])
        if not summary["returns"]:
            good_sets.append(summary["good"])
    distinct_good = []
    seen = set()
    for good in good_sets:
        if good not in seen:
            seen.add(good)
            distinct_good.append(good)
    mandatory = set(prefix_union)
    for good in distinct_good:
        if len(good) == 1:
            mandatory.update(good)
    relevant = set(prefix_union)
    for good in distinct_good:
        relevant.update(good)
    return {
        "summaries": summaries,
        "prefix_union": frozenset(prefix_union),
        "good_sets": tuple(distinct_good),
        "mandatory": frozenset(mandatory),
        "relevant": frozenset(relevant),
    }


def selected_constraints(rows: Sequence[Mapping[str, Any]], selected: Set[int]) -> Tuple[bool, List[Waiting]]:
    """Build exact AND/OR waiting conditions for a fixed selected set."""
    constraints: List[Waiting] = []
    for row in rows:
        summary = source_summary(row)
        prefix = summary["prefix"]
        if any(a not in selected for a in prefix):
            return False, []
        constraints.extend((frozenset({a}), b) for a, b in zip(prefix, prefix[1:]))
        if summary["returns"]:
            continue
        good = set(summary["good"]) & selected
        if not good:
            return False, []
        faults = set(summary["fault_actions"]) & selected
        if prefix:
            last = prefix[-1]
            constraints.extend((frozenset({last}), f) for f in faults if f != last)
        barriers = (
            (set(summary["emission_actions"]) - set(prefix))
            | (set(summary["fault_actions"]) - set(summary["good"]))
        ) & selected
        constraints.extend((frozenset(good), v) for v in barriers)
    # Remove exact duplicates while preserving deterministic order.
    unique: List[Waiting] = []
    seen = set()
    for cond in constraints:
        if cond not in seen:
            seen.add(cond)
            unique.append(cond)
    return True, unique
