from __future__ import annotations

import copy
import itertools
import unittest

from pccfr.bytecode import ObjectFormatError, decode_object, encode_object
from pccfr.certificate import check_certificate, make_certificate
from pccfr.frontier import frontier_valid, selected_constraints, witness_valid
from pccfr.generate import (
    fault, emit, graph_model, many_relevant_model, observer_gap_model,
    one_row_profile,
    random_model, silent,
)
from pccfr.model import observe, partial_permutations, source_observation, validate_model
from pccfr.oracle import direct_tree_shape_optimum
from pccfr.optimize import (
    SearchRefusal, direct_leaf_optimum, optimize_leaf, optimize_tree,
    origin_refined_model,
)
from pccfr.schedule import conditions_hold, ready_schedule


class CoreTests(unittest.TestCase):
    def test_frontier_exhaustive_three_actions(self):
        for codes in itertools.product(range(5), repeat=3):
            model = one_row_profile(codes)
            row = model["rows"][0]
            for order in partial_permutations(model["actions"]):
                self.assertEqual(frontier_valid(row, order), observe(row, order) == source_observation(row))

    def test_witness_equivalence(self):
        model = one_row_profile([2, 3, 3])
        row = model["rows"][0]
        for order in partial_permutations(model["actions"]):
            exists = any(witness_valid(row, order, w) for w in [None, 0, 1, 2])
            self.assertEqual(frontier_valid(row, order), exists)

    def test_non_poset_four_orders(self):
        model = one_row_profile([3, 3, 2])
        row = model["rows"][0]
        valid = {p for p in itertools.permutations(range(3)) if frontier_valid(row, p)}
        self.assertEqual(valid, {(0,1,2),(0,2,1),(1,0,2),(1,2,0)})

    def test_ready_schedule(self):
        cond = [(frozenset({0, 1}), 2), (frozenset({2}), 3)]
        order, residual = ready_schedule(range(4), cond)
        self.assertEqual(residual, [])
        self.assertIsNotNone(order)
        self.assertTrue(conditions_hold(order, cond))

    def test_ready_schedule_obstruction(self):
        cond = [(frozenset({1}), 0), (frozenset({0}), 1)]
        order, residual = ready_schedule([0, 1], cond)
        self.assertIsNone(order)
        self.assertEqual(residual, [0, 1])

    def test_graph_selection_matches_cover(self):
        model = graph_model(4, [(0,1),(1,2),(2,3)])
        leaf = optimize_leaf(model, (0,0), "representative_tuple")
        self.assertIsNotNone(leaf)
        self.assertEqual(len(leaf["order"]), 2)

    def test_leaf_optimizers_agree(self):
        model = random_model(17, 2, 5)
        direct = direct_leaf_optimum(model, (0,0))
        expected = None if direct is None else direct["cost"]
        for mode in ("auto", "optional_subset", "representative_tuple"):
            got = optimize_leaf(model, (0,0), mode)
            self.assertEqual(None if got is None else got["cost"], expected)

    def test_tree_optimizer_oracle(self):
        model = random_model(19, 2, 4)
        self.assertEqual(optimize_tree(model)["object_cost"], direct_tree_shape_optimum(model)["object_cost"])

    def test_observer_gap(self):
        for b in range(4):
            model = observer_gap_model(b)
            self.assertEqual(optimize_tree(model)["object_cost"], 12)
            self.assertEqual(optimize_tree(origin_refined_model(model))["object_cost"], 8 * (1 << b) + 4)

    def test_bytecode_round_trip(self):
        model = random_model(23, 2, 4)
        result = optimize_tree(model)
        obj = encode_object(model, result["tree"])
        self.assertEqual(len(obj), result["object_cost"])
        decoded = decode_object(model, obj)
        self.assertEqual(decoded["object_size"], len(obj))

    def test_certificate_round_trip(self):
        model = random_model(29, 2, 4)
        result = optimize_tree(model)
        obj = encode_object(model, result["tree"])
        cert = make_certificate(model, obj)
        self.assertTrue(check_certificate(model, obj, cert, len(obj))["accepted"])

    def test_budget_rejection(self):
        model = observer_gap_model(1)
        result = optimize_tree(model)
        obj = encode_object(model, result["tree"])
        cert = make_certificate(model, obj)
        self.assertEqual(check_certificate(model, obj, cert, len(obj)-1)["reason"], "over-budget")

    def test_object_mutation_rejected(self):
        model = observer_gap_model(1)
        obj = bytearray(encode_object(model, optimize_tree(model)["tree"]))
        obj[0] ^= 1
        with self.assertRaises(ObjectFormatError):
            decode_object(model, bytes(obj))

    def test_explicit_search_refusal(self):
        model = many_relevant_model(16)
        with self.assertRaises(SearchRefusal):
            optimize_leaf(model, (0,0), "optional_subset", 4096)
        self.assertEqual(optimize_leaf(model, (0,0), "representative_tuple", 4096)["cost"], 9)

    def test_model_validation_rejects_incomplete_domain(self):
        model = observer_gap_model(1)
        model["rows"].pop()
        with self.assertRaises(ValueError):
            validate_model(model)


if __name__ == "__main__":
    unittest.main()
