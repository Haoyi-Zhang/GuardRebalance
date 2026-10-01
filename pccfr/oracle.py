"""Independent small-boundary direct semantic oracles.

This module does not import frontier constraints, the production optimizer, or
its dynamic-programming recurrence. It enumerates ordered leaf subsets directly
and enumerates every read-once private-leaf tree shape at the configured small
input widths.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Iterator, Mapping, Sequence, Tuple

from .model import (
    Cell,
    cell_rows,
    object_action_cost,
    partial_permutations,
    split_cell,
    valid_on_rows,
    validate_model,
)

Shape = Tuple[Any, ...]


def _tree_key(tree: Mapping[str, Any]) -> Tuple[Any, ...]:
    if tree["type"] == "leaf":
        return (0, tuple(tree["order"]))
    return (1, tree["bit"], _tree_key(tree["left"]), _tree_key(tree["right"]))


def direct_leaf_oracle(model: Mapping[str, Any], cell: Cell) -> Dict[str, Any] | None:
    rows = cell_rows(model, cell)
    best: Dict[str, Any] | None = None
    tested = 0
    valid = 0
    for order in partial_permutations(model["actions"]):
        tested += 1
        if not valid_on_rows(rows, order):
            continue
        valid += 1
        cost = 3 + sum(object_action_cost(model, action, cell) for action in order)
        candidate = {
            "type": "leaf",
            "cell": [cell[0], cell[1]],
            "order": list(order),
            "cost": cost,
        }
        if best is None or (cost, len(order), tuple(order)) < (
            best["cost"], len(best["order"]), tuple(best["order"])
        ):
            best = candidate
    if best is not None:
        best["candidates_tested"] = tested
        best["valid_candidates"] = valid
    return best


@lru_cache(maxsize=None)
def _shapes(bits: int, fixed_mask: int) -> Tuple[Shape, ...]:
    values: list[Shape] = [("L",)]
    for bit in range(bits):
        if fixed_mask & (1 << bit):
            continue
        child_mask = fixed_mask | (1 << bit)
        children = _shapes(bits, child_mask)
        for left in children:
            for right in children:
                values.append(("B", bit, left, right))
    return tuple(values)


def enumerate_tree_shapes(bits: int) -> Iterator[Shape]:
    yield from _shapes(bits, 0)


def direct_tree_shape_optimum(model: Mapping[str, Any]) -> Dict[str, Any]:
    """Enumerate every grammar tree shape and directly score each leaf."""
    validate_model(model)
    bits = int(model["input_bits"])
    leaf_cache: Dict[Cell, Dict[str, Any] | None] = {}

    def leaf(cell: Cell) -> Dict[str, Any] | None:
        if cell not in leaf_cache:
            leaf_cache[cell] = direct_leaf_oracle(model, cell)
        value = leaf_cache[cell]
        return None if value is None else dict(value)

    def instantiate(shape: Shape, cell: Cell) -> Dict[str, Any] | None:
        if shape[0] == "L":
            return leaf(cell)
        _, bit, left_shape, right_shape = shape
        left_cell, right_cell = split_cell(cell, int(bit))
        left = instantiate(left_shape, left_cell)
        right = instantiate(right_shape, right_cell)
        if left is None or right is None:
            return None
        return {
            "type": "branch",
            "cell": [cell[0], cell[1]],
            "bit": int(bit),
            "left": left,
            "right": right,
            "cost": 2 + left["cost"] + right["cost"],
        }

    best: Dict[str, Any] | None = None
    count = 0
    feasible = 0
    for shape in enumerate_tree_shapes(bits):
        count += 1
        tree = instantiate(shape, (0, 0))
        if tree is None:
            continue
        feasible += 1
        if best is None or (tree["cost"], _tree_key(tree)) < (best["cost"], _tree_key(best)):
            best = tree
    if best is None:
        return {
            "status": "infeasible",
            "optimality_proven": True,
            "tree": None,
            "object_cost": None,
            "shapes_enumerated": count,
            "feasible_shapes": feasible,
            "leaf_cells_scored": len(leaf_cache),
        }
    return {
        "status": "optimal",
        "optimality_proven": True,
        "tree": best,
        "object_cost": 6 + int(best["cost"]),
        "shapes_enumerated": count,
        "feasible_shapes": feasible,
        "leaf_cells_scored": len(leaf_cache),
    }
