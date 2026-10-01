"""Deterministic regression report for the repaired scientific failure modes.

The report is generated from the executable implementation and the freshly
produced campaign directory. It is not a substitute for the unit tests or the
handwritten proofs; it preserves the exact outcomes of the review-blocking
microexamples in machine-readable form.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .bytecode import MAGIC, ObjectFormatError, _Cursor, decode_object, encode_object
from .certificate import check_certificate, make_certificate
from .frontier import frontier_valid
from .generate import fault, many_relevant_model, silent
from .model import ModelError, observe, source_observation, validate_model
from .optimize import (
    SearchRefusal,
    branchless_cost,
    leaf_search_outcome,
    optimize_tree,
)
from .oracle import direct_leaf_oracle
from .util import read_json


def _tree_refusal_model() -> Dict[str, Any]:
    return {
        "input_bits": 1,
        "actions": [0, 1, 2],
        "rows": [
            {
                "input": 0,
                "source": [0, 1, 2],
                "outcomes": [fault("a"), fault("a"), fault("x")],
            },
            {
                "input": 1,
                "source": [1, 0, 2],
                "outcomes": [fault("x"), fault("b"), fault("b")],
            },
        ],
    }


def _signature_collision_model() -> Dict[str, Any]:
    return {
        "input_bits": 0,
        "actions": [0, 1],
        "rows": [{
            "input": 0,
            "source": [0, 1],
            "outcomes": [fault({}), fault([])],
        }],
    }


def build_repair_report(artifact_root: Path, results: Path, binding_id: str) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    errors: list[str] = []

    # Search-mode admission and requested/actual mode preservation.
    many_rows = []
    for actions in (8, 16, 32, 64, 128):
        model = many_relevant_model(actions)
        methods = {}
        for requested in ("auto", "optional_subset", "representative_tuple"):
            outcome = leaf_search_outcome(model, (0, 0), requested, 4096)
            methods[requested] = {
                "status": outcome["status"],
                "requested_mode": outcome["requested_mode"],
                "actual_search_mode": outcome["search_mode"],
                "cost": outcome["cost"],
                "candidates": outcome.get("candidates"),
            }
            if outcome["requested_mode"] != requested:
                errors.append(f"explicit/requested search mode changed for n={actions}, {requested}")
        if methods["auto"]["actual_search_mode"] != "representative_tuple":
            errors.append(f"auto mode selected wrong complete space for n={actions}")
        many_rows.append({"actions": actions, "methods": methods})
    admitted = sum(
        method["status"] == "optimal"
        for row in many_rows for method in row["methods"].values()
    )
    refused = sum(
        method["status"] == "refused"
        for row in many_rows for method in row["methods"].values()
    )
    if (admitted, refused) != (11, 4):
        errors.append(f"many-relevant admission matrix is {(admitted, refused)}, expected (11, 4)")
    checks["many_relevant_search_modes"] = {
        "candidate_limit": 4096,
        "admitted": admitted,
        "refused": refused,
        "records": many_rows,
    }

    # Type-preserving JSON signatures and an independent direct-trace oracle.
    collision_model = _signature_collision_model()
    row = collision_model["rows"][0]
    source_trace = source_observation(row)
    target_trace = observe(row, [1])
    direct = direct_leaf_oracle(collision_model, (0, 0))
    collision_ok = source_trace != target_trace and not frontier_valid(row, [1]) and direct is not None and direct["order"] == [0]
    if not collision_ok:
        errors.append("typed-signature microexample was not rejected by all required paths")
    checks["typed_signature_microexample"] = {
        "input_bits": 0,
        "source": [0, 1],
        "target": [1],
        "source_observation": source_trace,
        "target_observation": target_trace,
        "frontier_valid": frontier_valid(row, [1]),
        "direct_leaf_order": None if direct is None else direct["order"],
        "accepted": collision_ok,
    }

    # Refusal/infeasibility/optimality separation for tree and branchless search.
    tree_model = _tree_refusal_model()
    root_leaf = direct_leaf_oracle(tree_model, (0, 0))
    direct_object_cost = None if root_leaf is None else 6 + int(root_leaf["cost"])
    strict_refused = False
    try:
        optimize_tree(tree_model, candidate_limit=2)
    except SearchRefusal:
        strict_refused = True
    diagnostic = optimize_tree(tree_model, candidate_limit=2, allow_incomplete=True)
    branchless = branchless_cost(tree_model, 2)
    tree_ok = (
        strict_refused
        and direct_object_cost == 12
        and diagnostic["status"] == "incomplete"
        and diagnostic["optimality_proven"] is False
        and diagnostic["object_cost"] == 20
        and branchless["status"] == "refused"
        and branchless["object_cost"] is None
    )
    if not tree_ok:
        errors.append("tree refusal state was conflated with optimality or infeasibility")
    checks["tree_refusal_microexample"] = {
        "good_sets": [[0, 1], [1, 2]],
        "candidate_limit": 2,
        "direct_single_leaf_order": None if root_leaf is None else root_leaf["order"],
        "direct_single_leaf_object_bytes": direct_object_cost,
        "strict_refused": strict_refused,
        "diagnostic_status": diagnostic["status"],
        "diagnostic_optimality_proven": diagnostic["optimality_proven"],
        "diagnostic_candidate_object_bytes": diagnostic["object_cost"],
        "branchless_status": branchless["status"],
        "accepted": tree_ok,
    }

    # Object parsing at every truncation and the real certificate checker path.
    golden = artifact_root / "fixtures" / "golden-pfc1"
    golden_model = read_json(golden / "model.json")
    golden_tree = read_json(golden / "tree.json")
    golden_bytes = encode_object(golden_model, golden_tree)
    certificate = make_certificate(golden_model, golden_bytes)
    structured_rejections = 0
    for cut in range(len(golden_bytes)):
        truncated = golden_bytes[:cut]
        try:
            decode_object(golden_model, truncated)
        except ObjectFormatError:
            pass
        else:
            errors.append(f"decoder accepted truncation at byte {cut}")
        outcome = check_certificate(golden_model, truncated, certificate, len(golden_bytes))
        if outcome.get("reason") == "invalid-object":
            structured_rejections += 1
        else:
            errors.append(f"checker did not structurally reject truncation at byte {cut}")
    cursor = _Cursor(b"x")
    cursor_position_before = cursor.pos
    negative_take_rejected = False
    try:
        cursor.take(-1)
    except ObjectFormatError:
        negative_take_rejected = True
    cursor_unchanged = cursor.pos == cursor_position_before
    expected_golden = bytes.fromhex("50 46 43 31 01 00 4c 01 00 00 00 01 01")
    golden_ok = golden_bytes == expected_golden and (golden / "region.pfc").read_bytes() == expected_golden
    if not (structured_rejections == len(golden_bytes) and negative_take_rejected and cursor_unchanged and golden_ok):
        errors.append("PFC1 truncation/cursor/golden-byte checks failed")
    checks["pfc1_parser_and_golden_bytes"] = {
        "object_bytes": len(golden_bytes),
        "all_truncation_positions_tested": len(golden_bytes),
        "structured_invalid_object_rejections": structured_rejections,
        "magic_only_reason": check_certificate(golden_model, MAGIC, certificate, len(golden_bytes))["reason"],
        "negative_take_rejected": negative_take_rejected,
        "cursor_position_unchanged": cursor_unchanged,
        "golden_hex": golden_bytes.hex(),
        "little_endian_u16": True,
        "guard_mask_bit_order": "LSB-first; input x is bit x mod 8 of byte floor(x/8)",
        "accepted": structured_rejections == len(golden_bytes) and negative_take_rejected and cursor_unchanged and golden_ok,
    }

    # Non-integral source actions must be rejected by validation and checker.
    float_source = {
        "input_bits": 0,
        "actions": [0],
        "rows": [{"input": 0, "source": [0.0], "outcomes": [fault("k")]}],
    }
    validation_rejected = False
    try:
        validate_model(float_source)
    except ModelError:
        validation_rejected = True
    checker_reason = check_certificate(float_source, MAGIC, {}, 100).get("reason")
    if not validation_rejected or checker_reason != "invalid-model":
        errors.append("floating source action was not uniformly rejected")
    checks["source_integer_validation"] = {
        "input": [0.0],
        "validator_rejected": validation_rejected,
        "checker_reason": checker_reason,
        "accepted": validation_rejected and checker_reason == "invalid-model",
    }

    # Duplicate emissions/faults and out-of-domain action identities.
    emission_row = {"input": 0, "source": [0, 1], "outcomes": [
        {"guard": True, "kind": "emit", "value": "e"}, fault("k")
    ]}
    fault_row = {"input": 0, "source": [0, 1], "outcomes": [fault("k"), silent()]}
    duplicate_cases = [
        ("duplicate-emission", emission_row, [0, 0, 1]),
        ("duplicate-fault", fault_row, [0, 0]),
        ("negative-action", fault_row, [-1]),
        ("large-action", fault_row, [2]),
        ("boolean-action", fault_row, [False]),
    ]
    duplicate_records = []
    for name, duplicate_row, order in duplicate_cases:
        valid = frontier_valid(duplicate_row, order)
        duplicate_records.append({"name": name, "order": order, "frontier_valid": valid})
        if valid:
            errors.append(f"frontier accepted invalid action order {name}")
    checks["frontier_action_domain"] = {
        "records": duplicate_records,
        "accepted": all(not record["frontier_valid"] for record in duplicate_records),
    }

    # Bind the repaired headline layers to the freshly generated campaign.
    exhaustive = read_json(results / "exhaustive.json")
    trees = read_json(results / "trees.json")
    andor = read_json(results / "and-or.json")
    controls = read_json(results / "controls.json")
    replay = read_json(results / "retained-input-replay.json")
    provenance = read_json(results / "provenance.json")
    campaign_ok = (
        exhaustive.get("semantic_comparisons") == 1_061_510
        and exhaustive.get("witness_existence_checks") == 45_885
        and exhaustive.get("certificate_object_replays") == 45_885
        and trees.get("independent_tree_instances") == 130
        and andor.get("semantic_snapshot_models") == 512
        and andor.get("semantic_permutation_comparisons") == 3_072
        and controls.get("cases") == 30
        and controls.get("mismatches") == 0
        and all(
            record.get("matched_expected_outcome_reason_and_stage") is True
            for record in controls.get("records", [])
        )
        and replay.get("input_tables_loaded") == 391
        and provenance.get("binding_id") == binding_id
    )
    if not campaign_ok:
        errors.append("fresh campaign evidence layers or binding do not match the repaired protocol")
    checks["campaign_evidence_layers"] = {
        "binding_id": binding_id,
        "semantic_comparisons": exhaustive.get("semantic_comparisons"),
        "witness_existence_checks": exhaustive.get("witness_existence_checks"),
        "object_certificate_replays": exhaustive.get("certificate_object_replays"),
        "certificate_frontier_row_checks": exhaustive.get("certificate_frontier_row_checks"),
        "certificate_direct_row_checks": exhaustive.get("certificate_direct_row_checks"),
        "independent_tree_instances": trees.get("independent_tree_instances"),
        "independent_tree_shapes_enumerated": trees.get("independent_tree_shapes_enumerated"),
        "semantic_waiting_models": andor.get("semantic_snapshot_models"),
        "semantic_waiting_permutation_comparisons": andor.get("semantic_permutation_comparisons"),
        "directed_controls": controls.get("cases"),
        "retained_input_tables": replay.get("input_tables_loaded"),
        "accepted": campaign_ok,
    }

    return {
        "accepted": not errors,
        "binding_id": binding_id,
        "scope": (
            "Regression evidence for the repaired finite snapshot-action/PFC1 implementation; "
            "not a mechanized proof, production-compiler evaluation, or performance claim."
        ),
        "checks": checks,
        "errors": errors,
    }
