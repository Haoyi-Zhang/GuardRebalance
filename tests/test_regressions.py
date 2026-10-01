from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pccfr.bytecode import MAGIC, ObjectFormatError, _Cursor, decode_object, encode_object
from pccfr.campaign import phase_controls
from pccfr.certificate import check_certificate, make_certificate
from pccfr.frontier import frontier_valid, witness_valid
from pccfr.generate import emit, fault, many_relevant_model, silent, waiting_family_model
from pccfr.model import (
    ModelError,
    freeze,
    observe,
    source_observation,
    source_summary,
    validate_model,
    valid_on_rows,
)
from pccfr.oracle import direct_tree_shape_optimum
from pccfr.optimize import (
    SearchRefusal,
    branchless_cost,
    direct_leaf_optimum,
    leaf_search_outcome,
    optimize_leaf,
    optimize_tree,
)
from pccfr.schedule import conditions_hold
from pccfr.util import StrictJSONError, read_json
from safe_output import UnsafeOutputPath, validate_paths


class RegressionTests(unittest.TestCase):
    def test_auto_mode_and_explicit_modes_are_not_overwritten(self):
        model = many_relevant_model(16)
        auto = leaf_search_outcome(model, (0, 0), "auto", 4096)
        representative = leaf_search_outcome(model, (0, 0), "representative_tuple", 4096)
        optional = leaf_search_outcome(model, (0, 0), "optional_subset", 4096)
        self.assertEqual((auto["status"], auto["search_mode"], auto["cost"]), ("optimal", "representative_tuple", 9))
        self.assertEqual((representative["status"], representative["search_mode"], representative["cost"]), ("optimal", "representative_tuple", 9))
        self.assertEqual((optional["status"], optional["search_mode"]), ("refused", "optional_subset"))

    def test_many_relevant_small_family_admission_matrix(self):
        expected_optional = {8: "optimal", 16: "refused", 32: "refused", 64: "refused", 128: "refused"}
        for n, status in expected_optional.items():
            model = many_relevant_model(n)
            outcomes = {
                mode: leaf_search_outcome(model, (0, 0), mode, 4096)
                for mode in ("auto", "representative_tuple", "optional_subset")
            }
            self.assertEqual(outcomes["auto"]["status"], "optimal")
            self.assertEqual(outcomes["auto"]["search_mode"], "representative_tuple")
            self.assertEqual(outcomes["representative_tuple"]["search_mode"], "representative_tuple")
            self.assertEqual(outcomes["optional_subset"]["search_mode"], "optional_subset")
            self.assertEqual(outcomes["optional_subset"]["status"], status)

    def test_typed_json_signatures_do_not_collide(self):
        pairs = [
            ({}, []),
            ({"k": 1}, [["k", 1]]),
            (False, 0),
            (True, 1),
        ]
        for left, right in pairs:
            self.assertNotEqual(freeze(left), freeze(right))

    def test_structural_signature_microexample_rejects_target_one(self):
        model = {
            "input_bits": 0,
            "actions": [0, 1],
            "rows": [{
                "input": 0,
                "source": [0, 1],
                "outcomes": [fault({}), fault([])],
            }],
        }
        validate_model(model)
        row = model["rows"][0]
        self.assertNotEqual(source_observation(row), observe(row, [1]))
        self.assertEqual(source_summary(row)["good"], frozenset({0}))
        self.assertFalse(frontier_valid(row, [1]))
        self.assertFalse(witness_valid(row, [1], 1))
        direct = direct_leaf_optimum(model, (0, 0))
        self.assertEqual(direct["order"], [0])

    def test_tree_refusal_is_not_reported_as_optimal(self):
        model = {
            "input_bits": 1,
            "actions": [0, 1, 2],
            "rows": [
                {"input": 0, "source": [0, 1, 2], "outcomes": [fault("a"), fault("a"), fault("x")]},
                {"input": 1, "source": [1, 0, 2], "outcomes": [fault("x"), fault("b"), fault("b")]},
            ],
        }
        direct = direct_leaf_optimum(model, (0, 0))
        self.assertEqual(6 + direct["cost"], 12)
        with self.assertRaises(SearchRefusal):
            optimize_tree(model, candidate_limit=2)
        diagnostic = optimize_tree(model, candidate_limit=2, allow_incomplete=True)
        self.assertEqual(diagnostic["status"], "incomplete")
        self.assertFalse(diagnostic["optimality_proven"])
        self.assertEqual(diagnostic["object_cost"], 20)
        self.assertEqual(branchless_cost(model, 2)["status"], "refused")

    def test_branchless_statuses_are_distinct(self):
        optimal_model = {
            "input_bits": 0,
            "actions": [0],
            "rows": [{"input": 0, "source": [0], "outcomes": [fault("k")]}],
        }
        infeasible_model = {
            "input_bits": 1,
            "actions": [0, 1],
            "rows": [
                {"input": 0, "source": [0, 1], "outcomes": [emit("a"), emit("b")]},
                {"input": 1, "source": [1, 0], "outcomes": [emit("a"), emit("b")]},
            ],
        }
        refused_model = many_relevant_model(16)
        self.assertEqual(branchless_cost(optimal_model)["status"], "optimal")
        self.assertEqual(branchless_cost(infeasible_model)["status"], "infeasible")
        self.assertEqual(branchless_cost(refused_model, 2)["status"], "refused")

    def test_cursor_rejects_negative_and_truncated_reads_without_moving(self):
        cursor = _Cursor(b"x")
        with self.assertRaises(ObjectFormatError):
            cursor.take(2)
        self.assertEqual(cursor.pos, 0)
        with self.assertRaises(ObjectFormatError):
            cursor.take(-1)
        self.assertEqual(cursor.pos, 0)
        empty = _Cursor(b"")
        with self.assertRaises(ObjectFormatError):
            empty.u8()
        self.assertEqual(empty.pos, 0)

    def test_all_object_truncations_are_structured_rejections(self):
        model = {
            "input_bits": 1,
            "actions": [0],
            "rows": [
                {"input": 0, "source": [0], "outcomes": [fault("k", True)]},
                {"input": 1, "source": [0], "outcomes": [fault("k", False)]},
            ],
        }
        tree = {"type": "leaf", "cell": [0, 0], "order": [0]}
        obj = encode_object(model, tree)
        cert = make_certificate(model, obj)
        self.assertGreater(len(obj), len(MAGIC))
        for cut in range(len(obj)):
            truncated = obj[:cut]
            with self.assertRaises(ObjectFormatError):
                decode_object(model, truncated)
            result = check_certificate(model, truncated, cert, len(obj))
            self.assertFalse(result["accepted"], cut)
            self.assertEqual(result["reason"], "invalid-object", cut)
            self.assertEqual(result["stage"], "object", cut)
        magic_only = check_certificate(model, MAGIC, cert, len(obj))
        self.assertEqual(magic_only["reason"], "invalid-object")
        self.assertEqual(magic_only["stage"], "object")

    def test_float_source_is_invalid_model_in_checker_and_cli(self):
        model = {
            "input_bits": 0,
            "actions": [0],
            "rows": [{"input": 0, "source": [0.0], "outcomes": [fault("k")]}],
        }
        result = check_certificate(model, MAGIC, {}, 100)
        self.assertEqual(result["reason"], "invalid-model")
        self.assertEqual(result["stage"], "model")
        with self.assertRaises(ModelError):
            validate_model(model)
        artifact = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "model.json").write_text(json.dumps(model), encoding="utf-8")
            (tmp_path / "object.pfc").write_bytes(MAGIC)
            (tmp_path / "certificate.json").write_text("{}", encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(artifact / "run.py"), "check", str(tmp_path / "model.json"), str(tmp_path / "object.pfc"), str(tmp_path / "certificate.json"), "--budget", "100"],
                cwd=artifact,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(process.returncode, 2)
            payload = json.loads(process.stdout)
            self.assertEqual(payload["reason"], "invalid-model")

    def test_frontier_rejects_duplicate_and_out_of_domain_actions(self):
        emission_row = {
            "input": 0,
            "source": [0, 1],
            "outcomes": [emit("e"), fault("k")],
        }
        fault_row = {
            "input": 0,
            "source": [0, 1],
            "outcomes": [fault("k"), silent()],
        }
        for row, order in (
            (emission_row, [0, 0, 1]),
            (fault_row, [0, 0]),
            (fault_row, [-1]),
            (fault_row, [2]),
            (fault_row, [False]),
        ):
            self.assertFalse(frontier_valid(row, order))
            self.assertFalse(witness_valid(row, order, 0))

    def test_golden_bytes_little_endian_and_lsb_first_mask(self):
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "golden-pfc1"
        mask_model = read_json(fixture / "model.json")
        mask_tree = read_json(fixture / "tree.json")
        expected_mask = bytes.fromhex((fixture / "region.hex").read_text(encoding="utf-8"))
        self.assertEqual((fixture / "region.pfc").read_bytes(), expected_mask)
        self.assertEqual(encode_object(mask_model, mask_tree), expected_mask)
        self.assertEqual(decode_object(mask_model, expected_mask)["tree"]["guard_masks"]["0"], "01")
        cert = make_certificate(mask_model, expected_mask)
        self.assertTrue(check_certificate(mask_model, expected_mask, cert, len(expected_mask))["accepted"])

        tree_model = {
            "input_bits": 1,
            "actions": [0, 1],
            "rows": [
                {"input": 0, "source": [1, 0], "outcomes": [silent(False), fault("F", True)]},
                {"input": 1, "source": [0, 1], "outcomes": [fault("F", True), silent(False)]},
            ],
        }
        tree = {
            "type": "branch", "cell": [0, 0], "bit": 0,
            "left": {"type": "leaf", "cell": [1, 0], "order": [1]},
            "right": {"type": "leaf", "cell": [1, 1], "order": [0]},
        }
        expected_tree = bytes.fromhex(
            "50 46 43 31 01 00 42 00 "
            "4c 01 00 01 00 00 "
            "4c 01 00 00 00 00"
        )
        self.assertEqual(encode_object(tree_model, tree), expected_tree)
        cert = make_certificate(tree_model, expected_tree)
        self.assertTrue(check_certificate(tree_model, expected_tree, cert, len(expected_tree))["accepted"])

    def test_waiting_family_has_true_semantic_realization(self):
        family = [(frozenset({0, 1}), 2), (frozenset({2}), 0)]
        model = waiting_family_model(family)
        for order in __import__("itertools").permutations(range(3)):
            self.assertEqual(valid_on_rows(model["rows"], order), conditions_hold(order, family))

    def test_controls_require_the_expected_rejection_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = phase_controls(Path(tmp))
        self.assertEqual(result["cases"], 30)
        self.assertEqual(result["mismatches"], 0)
        by_name = {record["name"]: record for record in result["records"]}
        for name in ("repeated-branch-bit", "noncanonical-implicit-guard", "noncanonical-explicit-guard"):
            self.assertEqual(by_name[name]["result"]["reason"], "invalid-object")
        self.assertEqual(by_name["wrong-witness-identity"]["result"]["reason"], "semantic-mismatch")
        self.assertTrue(all(
            record["matched_expected_outcome_reason_and_stage"]
            and record["actual_stage"] == record["expected_stage"]
            for record in result["records"]
        ))

    def test_model_schema_rejects_signature_alias_and_extra_fields(self):
        alias_model = {
            "input_bits": 0,
            "actions": [0],
            "rows": [{
                "input": 0,
                "source": [0],
                "outcomes": [{"guard": True, "kind": "fault", "value": "k", "signature": "k"}],
            }],
        }
        with self.assertRaisesRegex(ModelError, "closed schema"):
            validate_model(alias_model)
        extra_model = {
            "input_bits": 0,
            "actions": [0],
            "rows": [{
                "input": 0,
                "source": [0],
                "outcomes": [{"guard": True, "kind": "fault", "value": "k"}],
                "extra": 1,
            }],
        }
        with self.assertRaisesRegex(ModelError, "closed schema"):
            validate_model(extra_model)

    def test_strict_json_rejects_duplicate_keys_and_nonfinite_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"x":1,"x":2}', encoding="utf-8")
            with self.assertRaises(StrictJSONError):
                read_json(path)
            path.write_text('{"x":NaN}', encoding="utf-8")
            with self.assertRaises(StrictJSONError):
                read_json(path)

    def test_optimize_cli_refuses_existing_output_directory(self):
        artifact = Path(__file__).resolve().parents[1]
        model = {
            "input_bits": 0,
            "actions": [0],
            "rows": [{"input": 0, "source": [0], "outcomes": [fault("k")]}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            model_path = tmp_path / "model.json"
            model_path.write_text(json.dumps(model), encoding="utf-8")
            output = tmp_path / "existing"
            output.mkdir()
            sentinel = output / "sentinel"
            sentinel.write_text("keep", encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(artifact / "run.py"), "optimize", str(model_path), "--out", str(output)],
                cwd=artifact,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(process.returncode, 2)
            self.assertEqual(json.loads(process.stdout)["reason"], "unsafe-output")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_safe_output_validation_never_deletes_or_follows_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "artifact"
            results = root / "results"
            results.mkdir(parents=True)
            (results / "confirmed").mkdir()
            valid = validate_paths(root, [Path("results/reproduced-test"), Path("results/reproduced-test.json")])
            self.assertEqual(len(valid), 2)
            existing = results / "reproduced-existing"
            existing.mkdir()
            with self.assertRaises(UnsafeOutputPath):
                validate_paths(root, [existing])
            with self.assertRaises(UnsafeOutputPath):
                validate_paths(root, [results / "confirmed"])
            outside = Path(tmp) / "outside"
            outside.mkdir()
            link = results / "reproduced-link"
            link.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(UnsafeOutputPath):
                validate_paths(root, [link])
            with self.assertRaises(UnsafeOutputPath):
                validate_paths(root, [Path("results/reproduced-traverse/../confirmed")])
            self.assertTrue(existing.is_dir())
            self.assertTrue((results / "confirmed").is_dir())
            self.assertTrue(outside.is_dir())

        with tempfile.TemporaryDirectory() as tmp:
            real_root = Path(tmp) / "real-artifact"
            real_results = real_root / "results"
            real_results.mkdir(parents=True)
            linked_root = Path(tmp) / "linked-artifact"
            linked_root.symlink_to(real_root, target_is_directory=True)
            with self.assertRaises(UnsafeOutputPath):
                validate_paths(linked_root, [Path("results/reproduced-link-root")])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "artifact"
            root.mkdir()
            real_results = Path(tmp) / "real-results"
            real_results.mkdir()
            (root / "results").symlink_to(real_results, target_is_directory=True)
            with self.assertRaises(UnsafeOutputPath):
                validate_paths(root, [Path("results/reproduced-link-results")])

    def test_verify_results_separates_loading_json_and_pfc_failures(self):
        artifact = Path(__file__).resolve().parents[1]
        verifier = artifact / "verify_results.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = root / "reference"
            candidate = root / "candidate"
            (reference / "inputs").mkdir(parents=True)
            (reference / "objects").mkdir()
            (candidate / "inputs").mkdir(parents=True)
            (candidate / "objects").mkdir()
            (reference / "summary.json").write_text('{"value": 1}\n', encoding="utf-8")
            (reference / "inputs" / "case.json").write_text('{"input": 0}\n', encoding="utf-8")
            (reference / "objects" / "case.pfc").write_bytes(b"PFC1")
            (candidate / "summary.json").write_text('{"value": 1}\n', encoding="utf-8")
            (candidate / "inputs" / "case.json").write_text('{"input": 0}\n', encoding="utf-8")

            missing_pfc = subprocess.run(
                [sys.executable, str(verifier), "--reference", str(reference), "--candidate", str(candidate)],
                cwd=artifact,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(missing_pfc.returncode, 1)
            pfc_report = json.loads(missing_pfc.stdout)
            self.assertEqual(pfc_report["loading"]["status"], "failed")
            self.assertEqual(pfc_report["numeric_json_reproduction"]["status"], "ok")
            self.assertEqual(pfc_report["pfc_byte_reproduction"]["status"], "failed")
            self.assertEqual(pfc_report["loading"]["missing_pfc"], ["objects/case.pfc"])

            (candidate / "objects" / "case.pfc").write_bytes(b"PFC1")
            (candidate / "summary.json").unlink()
            missing_json = subprocess.run(
                [sys.executable, str(verifier), "--reference", str(reference), "--candidate", str(candidate)],
                cwd=artifact,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(missing_json.returncode, 1)
            json_report = json.loads(missing_json.stdout)
            self.assertEqual(json_report["loading"]["status"], "failed")
            self.assertEqual(json_report["numeric_json_reproduction"]["status"], "failed")
            self.assertEqual(json_report["pfc_byte_reproduction"]["status"], "ok")
            self.assertEqual(json_report["loading"]["missing_json"], ["summary.json"])

    def test_independent_tree_shape_oracle_matches_small_optimizer(self):
        model = {
            "input_bits": 1,
            "actions": [0, 1],
            "rows": [
                {"input": 0, "source": [0, 1], "outcomes": [emit("a"), fault("k")]},
                {"input": 1, "source": [1, 0], "outcomes": [silent(), fault("k")]},
            ],
        }
        fast = optimize_tree(model)
        oracle = direct_tree_shape_optimum(model)
        self.assertEqual(fast["object_cost"], oracle["object_cost"])
        self.assertEqual(oracle["shapes_enumerated"], 2)


if __name__ == "__main__":
    unittest.main()
