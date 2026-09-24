"""Exact bounded leaf and private-leaf decision-tree optimization."""
from __future__ import annotations

import copy
import itertools
import math
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Set, Tuple

from .frontier import requirements, selected_constraints
from .model import (
    Cell,
    cell_rows,
    free_bits,
    object_action_cost,
    partial_permutations,
    split_cell,
    valid_on_rows,
    validate_model,
)
from .schedule import ready_schedule

INF = 10**30


class SearchRefusal(RuntimeError):
    def __init__(self, mode: str, candidates: int, limit: int):
        super().__init__(f"{mode} complete candidate space {candidates} exceeds limit {limit}")
        self.mode = mode
        self.candidates = candidates
        self.limit = limit


def _leaf_cost(model: Mapping[str, Any], cell: Cell, order: Sequence[int]) -> int:
    return 3 + sum(object_action_cost(model, a, cell) for a in order)


def _better(candidate: Dict[str, Any] | None, incumbent: Dict[str, Any] | None) -> bool:
    if candidate is None:
        return False
    if incumbent is None:
        return True
    key_c = (candidate["cost"], len(candidate.get("order", [])), tuple(candidate.get("order", [])))
    key_i = (incumbent["cost"], len(incumbent.get("order", [])), tuple(incumbent.get("order", [])))
    return key_c < key_i


def candidate_space(rows: Sequence[Mapping[str, Any]]) -> Dict[str, int]:
    req = requirements(rows)
    optional = set(req["relevant"]) - set(req["mandatory"])
    subset_count = 1 << len(optional)
    product_count = 1
    for good in req["good_sets"]:
        if len(good) > 1:
            product_count *= len(good)
    return {
        "optional_subset": subset_count,
        "representative_tuple": product_count,
        "relevant_actions": len(req["relevant"]),
        "mandatory_actions": len(req["mandatory"]),
        "distinct_good_sets": len(req["good_sets"]),
    }


def _selected_solution(
    model: Mapping[str, Any],
    cell: Cell,
    rows: Sequence[Mapping[str, Any]],
    selected: Set[int],
    search_mode: str,
) -> Dict[str, Any] | None:
    covered, constraints = selected_constraints(rows, selected)
    if not covered:
        return None
    order, residual = ready_schedule(selected, constraints)
    if order is None:
        return None
    return {
        "type": "leaf",
        "cell": [cell[0], cell[1]],
        "order": order,
        "cost": _leaf_cost(model, cell, order),
        "search_mode": search_mode,
        "constraints": len(constraints),
        "residual": residual,
    }


def optimize_leaf(
    model: Mapping[str, Any],
    cell: Cell,
    mode: str = "auto",
    candidate_limit: int = 4096,
) -> Dict[str, Any] | None:
    rows = cell_rows(model, cell)
    req = requirements(rows)
    spaces = candidate_space(rows)
    if mode != "auto":
        mode = min(
            ("optional_subset", "representative_tuple"),
            key=lambda name: (spaces[name], name),
        )
    if mode not in {"optional_subset", "representative_tuple"}:
        raise ValueError("leaf search mode must be auto, optional_subset, or representative_tuple")
    if spaces[mode] > candidate_limit:
        raise SearchRefusal(mode, spaces[mode], candidate_limit)

    best: Dict[str, Any] | None = None
    seen: Set[frozenset[int]] = set()
    if mode == "optional_subset":
        mandatory = set(req["mandatory"])
        optional = sorted(set(req["relevant"]) - mandatory)
        iterator: Iterable[Set[int]] = (
            mandatory | {optional[i] for i in range(len(optional)) if mask & (1 << i)}
            for mask in range(1 << len(optional))
        )
    else:
        prefix = set(req["prefix_union"])
        variable_goods = [sorted(g) for g in req["good_sets"] if len(g) > 1]
        fixed = prefix | {
            next(iter(g)) for g in req["good_sets"] if len(g) == 1
        }
        if variable_goods:
            iterator = (fixed | set(choice) for choice in itertools.product(*variable_goods))
        else:
            iterator = iter([fixed])

    tested = 0
    for selected in iterator:
        frozen = frozenset(selected)
        if frozen in seen:
            continue
        seen.add(frozen)
        tested += 1
        # Positive costs permit a simple incumbent lower-bound prune.
        lower = 3 + sum(object_action_cost(model, a, cell) for a in selected)
        if best is not None and lower > best["cost"]:
            continue
        candidate = _selected_solution(model, cell, rows, set(selected), mode)
        if _better(candidate, best):
            best = candidate
    if best is not None:
        best["candidate_space"] = spaces[mode]
        best["candidates_tested"] = tested
        best["spaces"] = spaces
    return best


def direct_leaf_optimum(model: Mapping[str, Any], cell: Cell) -> Dict[str, Any] | None:
    rows = cell_rows(model, cell)
    best: Dict[str, Any] | None = None
    tested = 0
    valid = 0
    for order in partial_permutations(model["actions"]):
        tested += 1
        if not valid_on_rows(rows, order):
            continue
        valid += 1
        candidate = {
            "type": "leaf",
            "cell": [cell[0], cell[1]],
            "order": list(order),
            "cost": _leaf_cost(model, cell, order),
            "search_mode": "direct_trace",
        }
        if _better(candidate, best):
            best = candidate
    if best is not None:
        best["candidates_tested"] = tested
        best["valid_candidates"] = valid
    return best


def _tree_key(tree: Dict[str, Any]) -> Tuple[Any, ...]:
    if tree["type"] == "leaf":
        return (0, tuple(tree["order"]))
    return (1, tree["bit"], _tree_key(tree["left"]), _tree_key(tree["right"]))


def optimize_tree(
    model: Mapping[str, Any],
    leaf_mode: str = "auto",
    candidate_limit: int = 4096,
    direct_leaf: bool = False,
) -> Dict[str, Any]:
    validate_model(model)
    memo: Dict[Cell, Dict[str, Any]] = {}
    refusals: List[Dict[str, Any]] = []

    def solve(cell: Cell) -> Dict[str, Any]:
        if cell in memo:
            return copy.deepcopy(memo[cell])
        try:
            leaf = direct_leaf_optimum(model, cell) if direct_leaf else optimize_leaf(
                model, cell, leaf_mode, candidate_limit
            )
        except SearchRefusal as exc:
            leaf = None
            refusals.append({
                "cell": [cell[0], cell[1]],
                "mode": exc.mode,
                "candidates": exc.candidates,
                "limit": exc.limit,
            })
        best = leaf
        for bit in free_bits(model, cell):
            left_cell, right_cell = split_cell(cell, bit)
            left = solve(left_cell)
            right = solve(right_cell)
            candidate = {
                "type": "branch",
                "cell": [cell[0], cell[1]],
                "bit": bit,
                "left": left,
                "right": right,
                "cost": 2 + left["cost"] + right["cost"],
            }
            if best is None or (candidate["cost"], _tree_key(candidate)) < (
                best["cost"], _tree_key(best)
            ):
                best = candidate
        if best is None:
            # A singleton cell always has its source order as a valid leaf, so
            # this can only occur if all complete search modes were refused.
            raise SearchRefusal("tree", candidate_limit + 1, candidate_limit)
        memo[cell] = copy.deepcopy(best)
        return best

    tree = solve((0, 0))
    return {
        "tree": tree,
        "object_cost": 6 + tree["cost"],
        "leaf_mode": "direct_trace" if direct_leaf else leaf_mode,
        "candidate_limit": candidate_limit,
        "refusals": refusals,
        "cells_solved": len(memo),
    }


def fully_split_cost(model: Mapping[str, Any], candidate_limit: int = 4096) -> int:
    b = int(model["input_bits"])
    q = 1 << b
    leaf_total = 0
    for x in range(q):
        leaf = optimize_leaf(model, ((1 << b) - 1, x), "auto", candidate_limit)
        assert leaf is not None
        leaf_total += leaf["cost"]
    return 6 + 2 * (q - 1) + leaf_total


def branchless_cost(model: Mapping[str, Any], candidate_limit: int = 4096) -> int | None:
    try:
        leaf = optimize_leaf(model, (0, 0), "auto", candidate_limit)
    except SearchRefusal:
        return None
    return None if leaf is None else 6 + leaf["cost"]


def origin_refined_model(model: Mapping[str, Any]) -> Dict[str, Any]:
    """Conservative baseline: the identity of every fault is observed."""
    refined = copy.deepcopy(model)
    for row in refined["rows"]:
        for action, out in enumerate(row["outcomes"]):
            if out["kind"] == "fault":
                out["value"] = [out.get("value"), action]
    return refined


def tree_shape_count(bits: int) -> int:
    value = 1
    for b in range(1, bits + 1):
        value = 1 + b * value * value
    return value


def flatten_leaves(tree: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    if tree["type"] == "leaf":
        return [tree]
    return flatten_leaves(tree["left"]) + flatten_leaves(tree["right"])
