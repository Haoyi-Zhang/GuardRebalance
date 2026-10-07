"""Established AND/OR precedence feasibility routine."""
from __future__ import annotations

from heapq import heapify, heappop, heappush
from typing import Iterable, List, Sequence, Set, Tuple

from .frontier import Waiting


def ready_schedule(nodes: Iterable[int], conditions: Sequence[Waiting]) -> Tuple[List[int] | None, List[int]]:
    """Return a deterministic satisfying order or a closed residual witness.

    A node is ready iff every waiting condition targeting it already has an
    emitted predecessor.  Choosing any ready node preserves feasibility.
    """
    remaining: Set[int] = set(nodes)
    unmet = {node: 0 for node in remaining}
    incidences = {node: [] for node in remaining}
    targets: List[int] = []
    satisfied: List[bool] = []
    for predecessors, target in conditions:
        # Conditions for absent targets do not constrain this selected set.
        if target not in remaining:
            continue
        index = len(targets)
        targets.append(target)
        satisfied.append(False)
        unmet[target] += 1
        for predecessor in set(predecessors):
            if predecessor in remaining:
                incidences[predecessor].append(index)

    ready = [node for node in remaining if unmet[node] == 0]
    heapify(ready)
    order: List[int] = []
    while ready:
        node = heappop(ready)
        remaining.remove(node)
        order.append(node)
        for index in incidences[node]:
            # Several alternatives may emit; one condition decrements once.
            if satisfied[index]:
                continue
            satisfied[index] = True
            target = targets[index]
            unmet[target] -= 1
            if unmet[target] == 0:
                heappush(ready, target)
    if remaining:
        return None, sorted(remaining)
    return order, []


def conditions_hold(order: Sequence[int], conditions: Sequence[Waiting]) -> bool:
    pos = {a: i for i, a in enumerate(order)}
    if len(pos) != len(order):
        return False
    for predecessors, target in conditions:
        if target not in pos:
            return False
        if not any(p in pos and pos[p] < pos[target] for p in predecessors):
            return False
    return True
