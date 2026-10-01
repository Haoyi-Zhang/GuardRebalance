"""Exact bounded leaf and private-leaf decision-tree optimization."""
from __future__ import annotations

import copy
import itertools
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
LEAF_MODES = {"auto", "optional_subset", "representative_tuple"}


class SearchRefusal(RuntimeError):
    """A complete search space exceeded the declared admission limit."""

    def __init__(
        self,
        mode: str,
        candidates: int,
        limit: int,
        refusals: Sequence[Mapping[str, Any]] | None = None,
    ):
        super().__init__(f"{mode} complete candidate space {candidates} exceeds limit {limit}")
        self.mode = mode
        self.candidates = candidates
        self.limit = limit
        self.refusals = [dict(item) for item in (refusals or ())]


def _leaf_cost(model: Mapping[str, Any], cell: Cell, order: Sequence[int]) -> int:
    return 3 + sum(object_action_cost(model, action, cell) for action in order)


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
    """Return the exact admitted leaf optimum, ``None`` if infeasible.

    ``auto`` selects the smaller *complete* search space. Explicit modes are
    never rewritten. Exceeding the selected complete-space limit raises
    :class:`SearchRefusal`; it is not an infeasibility result.
    """
    if mode not in LEAF_MODES:
        raise ValueError("leaf search mode must be auto, optional_subset, or representative_tuple")
    if type(candidate_limit) is not int or candidate_limit < 0:
        raise ValueError("candidate_limit must be a nonnegative integer")

    rows = cell_rows(model, cell)
    req = requirements(rows)
    spaces = candidate_space(rows)
    requested_mode = mode
    if mode == "auto":
        mode = min(
            ("optional_subset", "representative_tuple"),
            key=lambda name: (spaces[name], name),
        )
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
        variable_goods = [sorted(good) for good in req["good_sets"] if len(good) > 1]
        fixed = prefix | {
            next(iter(good)) for good in req["good_sets"] if len(good) == 1
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
        lower = 3 + sum(object_action_cost(model, action, cell) for action in selected)
        if best is not None and lower > best["cost"]:
            continue
        candidate = _selected_solution(model, cell, rows, set(selected), mode)
        if _better(candidate, best):
            best = candidate
    if best is not None:
        best["requested_mode"] = requested_mode
        best["candidate_space"] = spaces[mode]
        best["candidates_tested"] = tested
        best["spaces"] = spaces
    return best


def leaf_search_outcome(
    model: Mapping[str, Any],
    cell: Cell,
    mode: str = "auto",
    candidate_limit: int = 4096,
) -> Dict[str, Any]:
    """Expose optimal, infeasible, and refused leaf states without conflation.

    ``search_mode`` always names the mode actually selected, including complete
    infeasible searches.  This makes retained-result replay sensitive to the
    auto-mode admission decision rather than only to its final cost.
    """
    if mode not in LEAF_MODES:
        raise ValueError("leaf search mode must be auto, optional_subset, or representative_tuple")
    actual_mode = mode
    if mode == "auto":
        spaces = candidate_space(cell_rows(model, cell))
        actual_mode = min(
            ("optional_subset", "representative_tuple"),
            key=lambda name: (spaces[name], name),
        )
    try:
        solution = optimize_leaf(model, cell, mode, candidate_limit)
    except SearchRefusal as exc:
        return {
            "status": "refused",
            "solution": None,
            "cost": None,
            "requested_mode": mode,
            "search_mode": exc.mode,
            "candidates": exc.candidates,
            "candidate_limit": exc.limit,
        }
    if solution is None:
        return {
            "status": "infeasible",
            "solution": None,
            "cost": None,
            "requested_mode": mode,
            "search_mode": actual_mode,
            "candidate_limit": candidate_limit,
        }
    return {
        "status": "optimal",
        "solution": solution,
        "cost": int(solution["cost"]),
        "requested_mode": mode,
        "search_mode": solution["search_mode"],
        "candidate_limit": candidate_limit,
    }


def direct_leaf_optimum(model: Mapping[str, Any], cell: Cell) -> Dict[str, Any] | None:
    """Independent direct-trace leaf oracle over all ordered subsets."""
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
            "requested_mode": "direct_trace",
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
    allow_incomplete: bool = False,
) -> Dict[str, Any]:
    """Optimize the private-leaf tree grammar.

    In strict mode (the default), any refused subproblem prevents an optimality
    claim and raises :class:`SearchRefusal`. Diagnostic mode may return the best
    feasible tree found so far with status ``incomplete`` and
    ``optimality_proven`` false. A completed search with no feasible tree is
    reported separately as ``infeasible``.
    """
    validate_model(model)
    if leaf_mode not in LEAF_MODES:
        raise ValueError("leaf search mode must be auto, optional_subset, or representative_tuple")
    memo: Dict[Cell, Tuple[Dict[str, Any] | None, bool]] = {}
    refusals: List[Dict[str, Any]] = []

    def solve(cell: Cell) -> Tuple[Dict[str, Any] | None, bool]:
        if cell in memo:
            node, complete = memo[cell]
            return copy.deepcopy(node), complete

        local_complete = True
        try:
            leaf = direct_leaf_optimum(model, cell) if direct_leaf else optimize_leaf(
                model, cell, leaf_mode, candidate_limit
            )
        except SearchRefusal as exc:
            leaf = None
            local_complete = False
            refusals.append({
                "cell": [cell[0], cell[1]],
                "mode": exc.mode,
                "candidates": exc.candidates,
                "limit": exc.limit,
            })

        best = leaf
        all_alternatives_complete = local_complete
        for bit in free_bits(model, cell):
            left_cell, right_cell = split_cell(cell, bit)
            left, left_complete = solve(left_cell)
            right, right_complete = solve(right_cell)
            branch_complete = left_complete and right_complete
            all_alternatives_complete = all_alternatives_complete and branch_complete
            if left is None or right is None:
                continue
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

        memo[cell] = (copy.deepcopy(best), all_alternatives_complete)
        return best, all_alternatives_complete

    tree, complete = solve((0, 0))
    if not complete and not allow_incomplete:
        first = refusals[0] if refusals else {
            "mode": "tree", "candidates": candidate_limit + 1, "limit": candidate_limit
        }
        raise SearchRefusal(
            "tree",
            int(first["candidates"]),
            int(first["limit"]),
            refusals=refusals,
        )

    if complete and tree is None:
        status = "infeasible"
    elif complete:
        status = "optimal"
    else:
        status = "incomplete"
    return {
        "status": status,
        "optimality_proven": status == "optimal",
        "feasible": tree is not None,
        "tree": tree,
        "object_cost": None if tree is None else 6 + tree["cost"],
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
        if leaf is None:
            raise AssertionError("a singleton cell must admit its source order")
        leaf_total += leaf["cost"]
    return 6 + 2 * (q - 1) + leaf_total


def branchless_cost(model: Mapping[str, Any], candidate_limit: int = 4096) -> Dict[str, Any]:
    """Return a non-conflating status for the root-cell leaf optimum."""
    outcome = leaf_search_outcome(model, (0, 0), "auto", candidate_limit)
    if outcome["status"] == "optimal":
        outcome["object_cost"] = 6 + int(outcome["cost"])
    else:
        outcome["object_cost"] = None
    return outcome


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
