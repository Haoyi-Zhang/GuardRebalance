"""Bounded deterministic confirmation phases."""
from __future__ import annotations

import copy
import itertools
import math
import random
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from .bytecode import MAGIC, encode_object
from .certificate import check_certificate, make_certificate
from .frontier import canonical_witness, frontier_valid, requirements, witness_valid
from .generate import (
    effective_outcome,
    feasible_random_model,
    fault,
    graph_edges,
    graph_model,
    many_relevant_model,
    observer_gap_model,
    one_row_profile,
    pad_actions,
    random_model,
    silent,
    emit,
    two_row_profiles,
    waiting_family_model,
)
from .model import (
    cell_rows,
    observe,
    partial_permutations,
    source_observation,
    source_summary,
    valid_on_rows,
)
from .oracle import direct_tree_shape_optimum
from .optimize import (
    SearchRefusal,
    branchless_cost,
    candidate_space,
    direct_leaf_optimum,
    leaf_search_outcome,
    flatten_leaves,
    fully_split_cost,
    optimize_leaf,
    optimize_tree,
    origin_refined_model,
    tree_shape_count,
)
from .schedule import conditions_hold, ready_schedule
from .util import read_json, write_json

# NOTE: the conditional import spelling above is intentionally avoided below;
# origin_refined_model is imported from optimize, where it belongs.


def _certificate_exists(row: Mapping[str, Any], order: Sequence[int], actions: Sequence[int]) -> bool:
    return any(witness_valid(row, order, w) for w in [None, *actions])


def phase_exhaustive(_: Path) -> Dict[str, Any]:
    """Exhaustively compare direct, frontier, witness, and object-certificate paths.

    Semantic coverage uses all ordered subsets through five actions. Witness and
    full object/certificate coverage use all ordered subsets through four
    actions; at five actions they use the source order for every profile. This
    yields 45,885 checks in each certificate layer, not 5,885.
    """
    semantic = 0
    witness_checks = 0
    object_replays = 0
    replay_frontier_rows = 0
    replay_direct_rows = 0
    mismatches = 0
    by_actions = []
    for n in range(1, 6):
        local_sem = 0
        local_witness = 0
        local_replays = 0
        for codes in itertools.product(range(5), repeat=n):
            model = one_row_profile(codes)
            row = model["rows"][0]
            orders = list(partial_permutations(model["actions"]))
            for order in orders:
                direct = observe(row, order) == source_observation(row)
                front = frontier_valid(row, order)
                semantic += 1
                local_sem += 1
                if direct != front:
                    mismatches += 1

            certificate_orders: Iterable[Sequence[int]]
            if n <= 4:
                certificate_orders = orders
            else:
                certificate_orders = (tuple(row["source"]),)
            for order in certificate_orders:
                front = frontier_valid(row, order)
                witness = _certificate_exists(row, order, model["actions"])
                witness_checks += 1
                local_witness += 1
                if witness != front:
                    mismatches += 1

                obj = _leaf_object(model, order)
                cert = make_certificate(model, obj)
                checked = check_certificate(model, obj, cert, len(obj))
                object_replays += 1
                local_replays += 1
                replay_frontier_rows += int(checked.get("frontier_checks", 0))
                replay_direct_rows += int(checked.get("direct_checks", 0))
                if bool(checked["accepted"]) != front:
                    mismatches += 1
        by_actions.append({
            "actions": n,
            "semantic_comparisons": local_sem,
            "witness_existence_checks": local_witness,
            "certificate_object_replays": local_replays,
            "certificate_coverage": "all ordered subsets" if n <= 4 else "source order per profile",
        })
    return {
        "phase": "exhaustive",
        "semantic_comparisons": semantic,
        "witness_existence_checks": witness_checks,
        "certificate_object_replays": object_replays,
        "certificate_frontier_row_checks": replay_frontier_rows,
        "certificate_direct_row_checks": replay_direct_rows,
        "mismatches": mismatches,
        "by_actions": by_actions,
    }


def phase_two_state(_: Path) -> Dict[str, Any]:
    comparisons = 0
    mismatches = 0
    orders = [(), (0,), (1,), (0, 1), (1, 0)]
    sources = [([0, 1], [0, 1]), ([0, 1], [1, 0]), ([1, 0], [0, 1]), ([1, 0], [1, 0])]
    profiles = list(itertools.product(range(5), repeat=2))
    for p0 in profiles:
        for p1 in profiles:
            for s0, s1 in sources:
                model = two_row_profiles(p0, p1, s0, s1)
                for order in orders:
                    direct = valid_on_rows(model["rows"], order)
                    front = all(frontier_valid(row, order) for row in model["rows"])
                    cert = all(_certificate_exists(row, order, model["actions"]) for row in model["rows"])
                    comparisons += 1
                    if direct != front or front != cert:
                        mismatches += 1
    return {"phase": "two-state", "comparisons": comparisons, "mismatches": mismatches}


def _save_model(inputs: Path, name: str, model: Mapping[str, Any]) -> None:
    write_json(inputs / name, model)


def phase_trees(out: Path) -> Dict[str, Any]:
    inputs = out / "inputs"
    objects = out / "objects"
    objects.mkdir(parents=True, exist_ok=True)
    mismatches = 0
    certificate_replays = 0
    shape_enumerations = 0
    records = []
    spec = [(2, 4, 100), (3, 3, 30)]
    index = 0
    for bits, actions, count in spec:
        for _ in range(count):
            seed = 714031 + index
            model = random_model(seed, bits, actions)
            identifier = f"exact-{index:03d}"
            _save_model(inputs, f"{identifier}.json", model)
            fast = optimize_tree(model, leaf_mode="auto", candidate_limit=4096)
            oracle = direct_tree_shape_optimum(model)
            shape_enumerations += int(oracle["shapes_enumerated"])
            if fast["status"] != "optimal" or oracle["status"] != "optimal":
                mismatches += 1
            if fast["object_cost"] != oracle["object_cost"]:
                mismatches += 1
            obj = encode_object(model, fast["tree"])
            (objects / f"{identifier}.pfc").write_bytes(obj)
            cert = make_certificate(model, obj)
            checked = check_certificate(model, obj, cert, len(obj))
            certificate_replays += 1
            if not checked["accepted"] or len(obj) != fast["object_cost"]:
                mismatches += 1
            records.append({
                "id": identifier,
                "bits": bits,
                "actions": actions,
                "seed": seed,
                "optimizer_status": fast["status"],
                "optimizer_cost": fast["object_cost"],
                "oracle_status": oracle["status"],
                "oracle_cost": oracle["object_cost"],
                "tree_shapes_in_grammar": tree_shape_count(bits),
                "tree_shapes_enumerated": oracle["shapes_enumerated"],
                "object_file": f"objects/{identifier}.pfc",
                "object_size": len(obj),
                "certificate_accepted": checked["accepted"],
            })
            index += 1
    return {
        "phase": "trees",
        "instances": len(records),
        "independent_tree_instances": len(records),
        "independent_tree_shapes_enumerated": shape_enumerations,
        "certificate_object_replays": certificate_replays,
        "mismatches": mismatches,
        "records": records,
    }


def _all_waiting_conditions() -> List[Tuple[frozenset[int], int]]:
    conditions = []
    for target in range(3):
        others = [x for x in range(3) if x != target]
        conditions.extend([
            (frozenset({others[0]}), target),
            (frozenset({others[1]}), target),
            (frozenset(others), target),
        ])
    return conditions


def phase_andor(_: Path) -> Dict[str, Any]:
    base = _all_waiting_conditions()
    mismatches = 0
    feasible = 0
    semantic_permutation_comparisons = 0
    construction_rows = 0
    for mask in range(1 << len(base)):
        family = [base[i] for i in range(len(base)) if mask & (1 << i)]
        order, residual = ready_schedule(range(3), family)
        condition_orders = [p for p in itertools.permutations(range(3)) if conditions_hold(p, family)]
        model = waiting_family_model(family, nodes=3)
        construction_rows += len(model["rows"])
        semantic_orders = []
        for permutation in itertools.permutations(range(3)):
            semantic_permutation_comparisons += 1
            if valid_on_rows(model["rows"], permutation):
                semantic_orders.append(permutation)
        if set(condition_orders) != set(semantic_orders):
            mismatches += 1
        if order is not None:
            feasible += 1
            if tuple(order) not in semantic_orders or not condition_orders:
                mismatches += 1
        elif condition_orders or semantic_orders or not residual:
            mismatches += 1
    return {
        "phase": "and-or",
        "families": 512,
        "feasible_families": feasible,
        "semantic_snapshot_models": 512,
        "semantic_rows_constructed": construction_rows,
        "semantic_permutation_comparisons": semantic_permutation_comparisons,
        "mismatches": mismatches,
    }


def _min_vertex_cover(n: int, edges: Sequence[Tuple[int, int]]) -> Tuple[int, Tuple[int, ...]]:
    for size in range(n + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return size, subset
    raise AssertionError("finite graph always has a vertex cover")


def phase_graphs(_: Path) -> Dict[str, Any]:
    instances = 0
    mismatches = 0
    records = []
    for n in range(2, 6):
        edge_count = n * (n - 1) // 2
        for mask in range(1, 1 << edge_count):
            edges = graph_edges(n, mask)
            model = graph_model(n, edges)
            leaf = optimize_leaf(model, (0, 0), "representative_tuple", 4096)
            assert leaf is not None
            cover_size, cover = _min_vertex_cover(n, edges)
            selected = len(leaf["order"])
            if selected != cover_size:
                mismatches += 1
            refined = origin_refined_model(model)
            refined_leaf = optimize_leaf(refined, (0, 0), "auto", 4096)
            expected_refined = len({min(u, v) for u, v in edges})
            if refined_leaf is None or len(refined_leaf["order"]) != expected_refined:
                mismatches += 1
            instances += 1
            if len(records) < 12:
                records.append({"n": n, "edges": edges, "cover": list(cover), "selected": leaf["order"]})
    return {"phase": "graphs", "instances": instances, "mismatches": mismatches, "examples": records}


def phase_observer_gap(_: Path) -> Dict[str, Any]:
    records = []
    mismatches = 0
    for bits in range(4):
        model = observer_gap_model(bits)
        coarse = optimize_tree(model)
        refined = optimize_tree(origin_refined_model(model))
        m = 1 << bits
        expected_coarse = 12
        expected_refined = 8 * m + 4
        if coarse["object_cost"] != expected_coarse or refined["object_cost"] != expected_refined:
            mismatches += 1
        records.append({
            "input_bits": bits,
            "inputs": m,
            "coarse_bytes": coarse["object_cost"],
            "refined_bytes": refined["object_cost"],
            "expected_refined_bytes": expected_refined,
        })
    return {"phase": "observer-gap", "instances": 4, "mismatches": mismatches, "records": records}


def phase_baselines(out: Path) -> Dict[str, Any]:
    inputs = out / "inputs"
    records = []
    mismatches = 0
    status_counts = {"optimal": 0, "infeasible": 0, "refused": 0}
    for i in range(64):
        bits = 1 + (i % 4)
        actions = 2 + (i % 7)
        seed = 901337 + i
        model = random_model(seed, bits, actions)
        identifier = f"baseline-{i:03d}"
        _save_model(inputs, f"{identifier}.json", model)
        exact = optimize_tree(model)
        split = fully_split_cost(model)
        branchless = branchless_cost(model)
        status_counts[branchless["status"]] += 1
        refined = optimize_tree(origin_refined_model(model))
        if exact["object_cost"] > split:
            mismatches += 1
        if branchless["status"] == "optimal" and exact["object_cost"] > branchless["object_cost"]:
            mismatches += 1
        records.append({
            "id": identifier,
            "bits": bits,
            "actions": actions,
            "seed": seed,
            "exact_private_tree": exact["object_cost"],
            "fully_split": split,
            "branchless_status": branchless["status"],
            "branchless": branchless["object_cost"],
            "branchless_search_mode": branchless.get("search_mode"),
            "origin_refined": refined["object_cost"],
        })
    return {
        "phase": "baselines",
        "instances": 64,
        "branchless_status_counts": status_counts,
        "mismatches": mismatches,
        "records": records,
    }


def _leaf_object(model: Mapping[str, Any], order: Sequence[int]) -> bytes:
    return encode_object(model, {"type": "leaf", "cell": [0, 0], "order": list(order)})


def _semantic_cases() -> List[Tuple[Dict[str, Any], List[int]]]:
    def m(outcomes: List[Dict[str, Any]], source: List[int], order: List[int]) -> Tuple[Dict[str, Any], List[int]]:
        return ({"input_bits": 0, "actions": list(range(len(outcomes))), "rows": [
            {"input": 0, "source": source, "outcomes": outcomes}
        ]}, order)
    return [
        m([emit("e"), fault("k")], [0, 1], [1]),
        m([emit("a"), emit("b"), fault("k")], [0, 1, 2], [1, 0, 2]),
        m([fault("a"), fault("b")], [0, 1], [1]),
        m([fault("k"), emit("extra")], [0, 1], [1, 0]),
        m([fault("good"), fault("bad")], [0, 1], [1, 0]),
        m([fault("k")], [0], []),
        m([emit("e"), fault("k"), fault("k")], [0, 1, 2], [2, 0]),
    ]


def phase_controls(out: Path) -> Dict[str, Any]:
    accepted = 0
    rejected = 0
    wrong = 0
    records = []

    def record(
        name: str,
        expected_accept: bool,
        expected_reason: str,
        expected_stage: str,
        result: Mapping[str, Any],
    ) -> None:
        nonlocal accepted, rejected, wrong
        actual_stage = result.get("stage")
        matched = (
            bool(result.get("accepted")) == expected_accept
            and result.get("reason") == expected_reason
            and actual_stage == expected_stage
        )
        records.append({
            "name": name,
            "expected": "accept" if expected_accept else "reject",
            "expected_reason": expected_reason,
            "expected_stage": expected_stage,
            "actual_stage": actual_stage,
            "matched_expected_outcome_reason_and_stage": matched,
            "result": dict(result),
        })
        if result.get("accepted"):
            accepted += 1
        else:
            rejected += 1
        wrong += int(not matched)

    # A canonical object with one retained root-cell guard mask.
    model = {
        "input_bits": 1,
        "actions": [0],
        "rows": [
            {"input": 0, "source": [0], "outcomes": [fault("k", True)]},
            {"input": 1, "source": [0], "outcomes": [fault("k", False)]},
        ],
    }
    obj = _leaf_object(model, [0])
    cert = make_certificate(model, obj)
    for name, budget, supplied in [
        ("valid-exact-budget", len(obj), cert),
        ("valid-larger-budget", len(obj) + 100, copy.deepcopy(cert)),
        ("valid-json-key-order-independent", len(obj), dict(reversed(list(cert.items())))),
    ]:
        record(name, True, "ok", "accept", check_certificate(model, obj, supplied, budget))

    # Seven format-valid semantic attacks.
    for i, (bad_model, order) in enumerate(_semantic_cases()):
        bad_obj = _leaf_object(bad_model, order)
        bad_cert = make_certificate(bad_model, bad_obj)
        record(
            f"semantic-{i:02d}",
            False,
            "semantic-mismatch",
            "semantic",
            check_certificate(bad_model, bad_obj, bad_cert, len(bad_obj)),
        )

    object_mutations: List[Tuple[str, Mapping[str, Any], bytes, Mapping[str, Any], int]] = []
    b = bytearray(obj); b[0] ^= 1
    object_mutations.append(("bad-magic", model, bytes(b), cert, len(obj)))
    b = bytearray(obj); b[4] = 0
    object_mutations.append(("wrong-input-width", model, bytes(b), cert, len(obj)))
    b = bytearray(obj); b[5] = 1
    object_mutations.append(("reserved-byte", model, bytes(b), cert, len(obj)))
    object_mutations.append(("magic-only-truncated", model, MAGIC, cert, len(obj)))
    object_mutations.append(("trailing-byte", model, obj + b"x", cert, len(obj) + 1))
    b = bytearray(obj); b[9:11] = (65535).to_bytes(2, "little")
    object_mutations.append(("unknown-action", model, bytes(b), cert, len(obj)))
    duplicate = obj[:7] + (2).to_bytes(2, "little") + obj[9:] + obj[9:]
    object_mutations.append(("duplicate-action", model, duplicate, cert, len(duplicate)))
    b = bytearray(obj); b[11] = 2
    object_mutations.append(("unknown-action-flag", model, bytes(b), cert, len(obj)))
    b = bytearray(obj); b[12] ^= 0x02
    object_mutations.append(("wrong-guard-mask", model, bytes(b), cert, len(obj)))
    implicit = obj[:11] + b"\x00"
    object_mutations.append(("noncanonical-implicit-guard", model, implicit, cert, len(implicit)))

    all_true_model = {
        "input_bits": 1,
        "actions": [0],
        "rows": [
            {"input": 0, "source": [0], "outcomes": [fault("k", True)]},
            {"input": 1, "source": [0], "outcomes": [fault("k", True)]},
        ],
    }
    all_true_obj = _leaf_object(all_true_model, [0])
    all_true_cert = make_certificate(all_true_model, all_true_obj)
    explicit = all_true_obj[:11] + b"\x01\x03"
    object_mutations.append((
        "noncanonical-explicit-guard", all_true_model, explicit, all_true_cert, len(explicit)
    ))

    repeated_bit = MAGIC + b"\x01\x00" + b"B\x00B\x00"
    object_mutations.append(("repeated-branch-bit", model, repeated_bit, cert, len(repeated_bit)))

    for name, supplied_model, bad_obj, bad_cert, budget in object_mutations:
        record(
            name,
            False,
            "invalid-object",
            "object",
            check_certificate(supplied_model, bad_obj, bad_cert, budget),
        )

    certificate_mutations: List[Tuple[str, Mapping[str, Any], str, str]] = []
    c = copy.deepcopy(cert); c["format"] = "unknown"
    certificate_mutations.append(("cert-format", c, "invalid-certificate", "certificate"))
    c = copy.deepcopy(cert); c["object_size"] += 1
    certificate_mutations.append(("cert-object-size", c, "invalid-certificate", "certificate"))
    c = copy.deepcopy(cert); c["leaves"] = []
    certificate_mutations.append(("cert-leaf-count", c, "invalid-certificate", "certificate"))
    c = copy.deepcopy(cert); c["leaves"][0]["order"] = []
    certificate_mutations.append(("cert-order", c, "invalid-certificate", "certificate"))
    c = copy.deepcopy(cert); c["leaves"][0]["witnesses"].pop("1")
    certificate_mutations.append(("cert-witness-domain", c, "invalid-certificate", "certificate"))
    c = copy.deepcopy(cert); c["leaves"][0]["witnesses"]["0"] = 99
    certificate_mutations.append(("wrong-witness-identity", c, "semantic-mismatch", "semantic"))

    for name, bad_cert, reason, stage in certificate_mutations:
        record(name, False, reason, stage, check_certificate(model, obj, bad_cert, len(obj)))

    record(
        "budget-one-short", False, "over-budget", "budget",
        check_certificate(model, obj, cert, len(obj) - 1),
    )
    record(
        "budget-negative", False, "invalid-budget", "budget",
        check_certificate(model, obj, cert, -1),
    )

    example = out / "example"
    example.mkdir(parents=True, exist_ok=True)
    (example / "region.pfc").write_bytes(obj)
    write_json(example / "model.json", model)
    write_json(example / "certificate.json", cert)
    write_json(example / "check.json", check_certificate(model, obj, cert, len(obj)))
    return {
        "phase": "controls",
        "cases": len(records),
        "expected_acceptances": 3,
        "expected_rejections": 27,
        "accepted": accepted,
        "rejected": rejected,
        "mismatches": wrong,
        "records": records,
    }


def _solution_cost(value: Mapping[str, Any] | None) -> int | None:
    return None if value is None else int(value["cost"])


def _sparsify(model: Mapping[str, Any], order: Sequence[int]) -> List[int]:
    keep = set()
    for row in model["rows"]:
        summary = source_summary(row)
        keep.update(summary["prefix"])
        if not summary["returns"]:
            for a in order:
                out = row["outcomes"][a]
                if out["guard"] and out["kind"] == "fault":
                    keep.add(a)
                    break
    return [a for a in order if a in keep]


def phase_search(out: Path) -> Dict[str, Any]:
    inputs = out / "inputs"
    mismatches = 0
    comparisons = 0
    records = []
    for i in range(128):
        model = random_model(860311 + i, 2, 5)
        _save_model(inputs, f"joint-{i:03d}.json", model)
        direct = direct_leaf_optimum(model, (0, 0))
        methods = {
            "auto": optimize_leaf(model, (0, 0), "auto", 4096),
            "optional_subset": optimize_leaf(model, (0, 0), "optional_subset", 4096),
            "representative_tuple": optimize_leaf(model, (0, 0), "representative_tuple", 4096),
        }
        expected = _solution_cost(direct)
        for name, value in methods.items():
            comparisons += 1
            if _solution_cost(value) != expected:
                mismatches += 1
        records.append({
            "id": f"joint-{i:03d}",
            "direct": expected,
            **{k: _solution_cost(v) for k, v in methods.items()},
            "actual_search_modes": {
                k: (None if v is None else v.get("search_mode"))
                for k, v in methods.items()
            },
        })

    # 2,343 valid leaves, each checked by completion and sparsification.
    transformations = 0
    seed = 990001
    model_index = 0
    while transformations < 4686:
        model = feasible_random_model(seed + model_index, 2, 5)
        model_index += 1
        for order in partial_permutations(model["actions"]):
            if not valid_on_rows(model["rows"], order):
                continue
            completed = list(order) + [a for a in model["actions"] if a not in order]
            if not valid_on_rows(model["rows"], completed):
                mismatches += 1
            transformations += 1
            if transformations >= 4686:
                break
            sparse = _sparsify(model, order)
            if not valid_on_rows(model["rows"], sparse):
                mismatches += 1
            transformations += 1
            if transformations >= 4686:
                break
    return {
        "phase": "search", "instances": 128, "optimum_comparisons": comparisons,
        "completion_sparsification_checks": transformations, "mismatches": mismatches,
        "records": records,
    }


def phase_padding(out: Path) -> Dict[str, Any]:
    inputs = out / "inputs"
    # Stratified stress: four instances each at 128, 512, and 2,048 actions;
    # the remaining 52 exercise independent 32-action cores.
    targets = [2048 if i % 16 == 0 else 512 if i % 16 == 1 else 128 if i % 16 == 2 else 32 for i in range(64)]
    records = []
    mismatches = 0
    for i in range(64):
        core = feasible_random_model(611953 + i, 2, 5)
        core_leaf = optimize_leaf(core, (0, 0), "auto", 4096)
        target = targets[i]
        model = pad_actions(core, target)
        _save_model(inputs, f"padding-{i:03d}.json", model)
        padded = optimize_leaf(model, (0, 0), "auto", 4096)
        if _solution_cost(core_leaf) != _solution_cost(padded):
            mismatches += 1
        records.append({"id": f"padding-{i:03d}", "actions": target, "cost": _solution_cost(padded)})
    return {"phase": "padding", "instances": 64, "mismatches": mismatches, "records": records}


def phase_many_relevant(out: Path) -> Dict[str, Any]:
    inputs = out / "inputs"
    sizes = [8, 16, 32, 64, 128]
    records = []
    mismatches = 0
    admitted = 0
    refusals = 0
    expected_cost = 9  # leaf: 3 bytes plus two unconditional action copies
    for i, n in enumerate(sizes):
        model = many_relevant_model(n)
        identifier = f"many-{i:03d}"
        _save_model(inputs, f"{identifier}.json", model)
        spaces = candidate_space(model["rows"])
        outcomes = {
            mode: leaf_search_outcome(model, (0, 0), mode, 4096)
            for mode in ("auto", "representative_tuple", "optional_subset")
        }
        method_records = {}
        for requested, outcome in outcomes.items():
            if outcome["status"] == "optimal":
                admitted += 1
                if outcome["cost"] != expected_cost:
                    mismatches += 1
            elif outcome["status"] == "refused":
                refusals += 1
            else:
                mismatches += 1
            actual_mode = outcome.get("search_mode")
            method_records[requested] = {
                "status": outcome["status"],
                "cost": outcome["cost"],
                "actual_search_mode": actual_mode,
                "candidate_space": spaces.get(actual_mode),
            }

        expected_auto_mode = min(
            ("optional_subset", "representative_tuple"),
            key=lambda name: (spaces[name], name),
        )
        if method_records["auto"]["actual_search_mode"] != expected_auto_mode:
            mismatches += 1
        if method_records["representative_tuple"]["actual_search_mode"] != "representative_tuple":
            mismatches += 1
        if method_records["optional_subset"]["actual_search_mode"] != "optional_subset":
            mismatches += 1
        expected_optional_status = "optimal" if spaces["optional_subset"] <= 4096 else "refused"
        if method_records["optional_subset"]["status"] != expected_optional_status:
            mismatches += 1

        records.append({
            "id": identifier,
            "actions": n,
            "spaces": spaces,
            "expected_leaf_cost": expected_cost,
            "methods": method_records,
        })
    return {
        "phase": "many-relevant",
        "instances": 5,
        "admitted_methods": admitted,
        "explicit_refusals": refusals,
        "mismatches": mismatches,
        "records": records,
    }


def phase_replay(out: Path) -> Dict[str, Any]:
    inputs = out / "inputs"
    files = sorted(inputs.glob("*.json"))
    expected_ids = (
        {f"exact-{i:03d}" for i in range(130)}
        | {f"baseline-{i:03d}" for i in range(64)}
        | {f"joint-{i:03d}" for i in range(128)}
        | {f"padding-{i:03d}" for i in range(64)}
        | {f"many-{i:03d}" for i in range(5)}
    )
    actual_ids = {path.stem for path in files}
    missing = sorted(expected_ids - actual_ids)
    unexpected = sorted(actual_ids - expected_ids)
    mismatches = int(not files or bool(missing) or bool(unexpected))
    parsed = 0
    for path in files:
        model = read_json(path)
        parsed += 1
        if path.stem.startswith("many-"):
            optimize_leaf(model, (0, 0), "representative_tuple", 4096)
        elif path.stem.startswith("padding-") or path.stem.startswith("joint-"):
            optimize_leaf(model, (0, 0), "auto", 4096)
        else:
            optimize_tree(model)
    families = {
        prefix: sum(identifier.startswith(prefix + "-") for identifier in actual_ids)
        for prefix in ("exact", "baseline", "joint", "padding", "many")
    }
    return {
        "phase": "retained-input-replay",
        "loading_status": "ok" if mismatches == 0 else "failed",
        "input_tables_loaded": len(files),
        "input_tables_parsed": parsed,
        "stable_ids_expected": len(expected_ids),
        "stable_ids_present": len(actual_ids),
        "missing_ids": missing,
        "unexpected_ids": unexpected,
        "families": families,
        "mismatches": mismatches,
        "input_acquisition": "retained exact JSON tables; no pseudorandom generation",
    }


PHASES = {
    "exhaustive": phase_exhaustive,
    "two-state": phase_two_state,
    "trees": phase_trees,
    "and-or": phase_andor,
    "graphs": phase_graphs,
    "observer-gap": phase_observer_gap,
    "baselines": phase_baselines,
    "controls": phase_controls,
    "search": phase_search,
    "padding": phase_padding,
    "many-relevant": phase_many_relevant,
    "retained-input-replay": phase_replay,
}
