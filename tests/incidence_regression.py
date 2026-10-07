"""Small public references for deterministic AND/OR incidence scheduling."""
from __future__ import annotations

import copy
import itertools
import json
import unittest

from pccfr.bytecode import encode_object
from pccfr.certificate import check_certificate, make_certificate
from pccfr.optimize import SearchRefusal, leaf_search_outcome, optimize_leaf, optimize_tree
from pccfr.schedule import conditions_hold, ready_schedule


def prefix_reference(nodes, conditions):
    """Enumerate legal prefixes, not a readiness algorithm (at most four nodes)."""
    nodes = tuple(sorted(set(nodes)))
    if len(nodes) > 4:
        raise ValueError("finite reference supports at most four nodes")
    reachable = set()
    full = []
    for length in range(len(nodes) + 1):
        for prefix in itertools.permutations(nodes, length):
            positions = {node: index for index, node in enumerate(prefix)}
            if all(
                target not in positions
                or any(p in positions and positions[p] < positions[target] for p in predecessors)
                for predecessors, target in conditions
            ):
                reachable.update(prefix)
                if length == len(nodes):
                    full.append(prefix)
    return (list(min(full)), []) if full else (None, sorted(set(nodes) - reachable))


def outcome(code):
    if code == 0:
        return {"guard": False, "kind": "fault", "value": "wrong"}
    if code == 1:
        return {"guard": True, "kind": "silent"}
    return {"guard": True, "kind": "emit" if code == 2 else "fault",
            "value": "good" if code in (2, 3) else "wrong"}


def two_rows(first, second):
    return {
        "input_bits": 1, "actions": list(range(len(first))),
        "rows": [
            {"input": 0, "source": list(range(len(first))), "outcomes": list(map(outcome, first))},
            {"input": 1, "source": list(reversed(range(len(second)))), "outcomes": list(map(outcome, second))},
        ],
    }


def observation(row, order):
    """Test-local interpreter of the raw table; no frontier/model helper."""
    events = []
    for action in order:
        item = row["outcomes"][action]
        if not item["guard"]:
            continue
        value = json.dumps(item.get("value"), sort_keys=True, allow_nan=False)
        if item["kind"] == "emit":
            events.append((action, value))
        elif item["kind"] == "fault":
            return tuple(events), ("fault", value)
    return tuple(events), ("return",)


def leaf_reference(model):
    """All 65 ordered subsets of four actions; independent raw charge formula."""
    if model["input_bits"] != 1 or len(model["actions"]) > 4:
        raise ValueError("finite reference supports two rows and at most four actions")
    valid = []
    rows = model["rows"]
    for length in range(len(model["actions"]) + 1):
        for order in itertools.permutations(model["actions"], length):
            if all(observation(row, order) == observation(row, row["source"]) for row in rows):
                charge = 3 + sum(
                    3 if all(row["outcomes"][a]["guard"] for row in rows) else 4 for a in order
                )
                valid.append((charge, length, order))
    return None if not valid else min(valid)


class IncidenceRegression(unittest.TestCase):
    def test_all_512_three_node_wait_families(self):
        possible = []
        for target in range(3):
            others = [n for n in range(3) if n != target]
            for mask in range(1, 4):
                possible.append((frozenset(others[i] for i in range(2) if mask & (1 << i)), target))
        self.assertEqual(len(possible), 9)
        for bits in range(512):
            waits = [wait for i, wait in enumerate(possible) if bits & (1 << i)]
            self.assertEqual(ready_schedule(range(3), waits), prefix_reference(range(3), waits), bits)

    def test_all_64_four_node_forward_edge_sets(self):
        edges = list(itertools.combinations(range(4), 2))
        for bits in range(64):
            waits = [(frozenset({a}), b) for i, (a, b) in enumerate(edges) if bits & (1 << i)]
            order, residual = ready_schedule(reversed(range(4)), waits)
            self.assertEqual((order, residual), prefix_reference(range(4), waits), bits)
            self.assertTrue(conditions_hold(order, waits))

    def test_closed_residual_duplicates_and_alternatives(self):
        cases = [
            ([], [(frozenset(), 9)]),
            ([0, 1, 2, 3], [(frozenset({2}), 0)]),
            ([0, 1, 2], [(frozenset({0, 1}), 2), (frozenset({1}), 2)]),
            ([0, 1, 2], [(frozenset({0, 1}), 2)] * 3),
            ([0, 1, 2, 3], [(frozenset({1}), 0), (frozenset({0}), 1)]),
            ([0, 1, 2], [(frozenset(), 0), (frozenset({0}), 1)]),
            ([0, 0, 1, 2], [(frozenset({9}), 0), (frozenset({0, 1}), 2), (frozenset(), 8)]),
            ([0, 1, 2], [(frozenset({0}), 0), (frozenset({0, 1}), 2)]),
        ]
        for nodes, waits in cases:
            self.assertEqual(ready_schedule(iter(nodes), waits), prefix_reference(nodes, waits))
        self.assertEqual(ready_schedule([0, 1, 2, 3], cases[1][1]), ([1, 2, 0, 3], []))

    def test_64_raw_two_row_leaf_optima(self):
        profiles = [
            (0, 0, 0, 0), (1, 1, 1, 1), (2, 3, 3, 4), (3, 3, 2, 1),
            (4, 2, 3, 0), (2, 1, 2, 1), (0, 3, 1, 3), (1, 4, 3, 2),
        ]
        for first, second in itertools.product(profiles, repeat=2):
            model = two_rows(first, second)
            reference = leaf_reference(model)
            for mode in ("auto", "optional_subset", "representative_tuple"):
                result = optimize_leaf(model, (0, 0), mode)
                if reference is None:
                    self.assertIsNone(result)
                else:
                    self.assertEqual((result["cost"], len(result["order"]), tuple(result["order"])), reference)

    def test_certificate_bytes_counters_and_negative_controls(self):
        model = two_rows((3, 3), (3, 3))
        obj = encode_object(model, {"type": "leaf", "order": [0]})
        cert = make_certificate(model, obj)
        self.assertEqual(check_certificate(model, obj, cert, len(obj)), {
            "accepted": True, "reason": "ok", "stage": "accept", "object_size": 12,
            "budget": 12, "leaves": 1, "frontier_checks": 2, "direct_checks": 2,
        })
        self.assertEqual(check_certificate(model, obj, cert, len(obj) - 1)["reason"], "over-budget")
        bad = copy.deepcopy(cert)
        bad["leaves"][0]["witnesses"]["0"] = 1
        rejected = check_certificate(model, obj, bad, len(obj))
        self.assertEqual((rejected["reason"], rejected["stage"]), ("semantic-mismatch", "semantic"))
        bad = copy.deepcopy(cert)
        bad["input_bits"] = True
        self.assertEqual(check_certificate(model, obj, bad, len(obj))["reason"], "invalid-certificate")
        self.assertEqual(check_certificate(model, obj[:-1], cert, len(obj))["reason"], "invalid-object")

    def test_complete_space_refusal_is_not_infeasibility(self):
        model = two_rows((3, 3, 4), (4, 3, 3))
        self.assertEqual(leaf_reference(model), (6, 1, (1,)))
        refused = leaf_search_outcome(model, (0, 0), "representative_tuple", 3)
        self.assertEqual(refused, {
            "status": "refused", "solution": None, "cost": None,
            "requested_mode": "representative_tuple", "search_mode": "representative_tuple",
            "candidates": 4, "candidate_limit": 3,
        })
        admitted = leaf_search_outcome(model, (0, 0), "representative_tuple", 4)
        self.assertEqual((admitted["status"], admitted["cost"], admitted["solution"]["order"]), ("optimal", 6, [1]))
        with self.assertRaises(SearchRefusal):
            optimize_tree(model, candidate_limit=3)
        diagnostic = optimize_tree(model, candidate_limit=3, allow_incomplete=True)
        self.assertEqual((diagnostic["status"], diagnostic["optimality_proven"]), ("incomplete", False))


if __name__ == "__main__":
    unittest.main()
