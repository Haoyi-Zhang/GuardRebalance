"""Established AND/OR precedence feasibility routine."""
from __future__ import annotations

from typing import Iterable, List, Sequence, Set, Tuple

from .frontier import Waiting


def ready_schedule(nodes: Iterable[int], conditions: Sequence[Waiting]) -> Tuple[List[int] | None, List[int]]:
    """Return a deterministic satisfying order or a closed residual witness.

    A node is ready iff every waiting condition targeting it already has an
    emitted predecessor.  Choosing any ready node preserves feasibility.
    """
    remaining: Set[int] = set(nodes)
    emitted: Set[int] = set()
    order: List[int] = []
    while remaining:
        ready = []
        for node in sorted(remaining):
            ok = True
            for predecessors, target in conditions:
                if target == node and not (set(predecessors) & emitted):
                    ok = False
                    break
            if ok:
                ready.append(node)
        if not ready:
            return None, sorted(remaining)
        node = ready[0]
        remaining.remove(node)
        emitted.add(node)
        order.append(node)
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
