"""Bounded deterministic confirmation phases."""
from __future__ import annotations

import copy
import itertools
import math
import random
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from .bytecode import encode_object
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
)
from .model import (
    cell_rows,
    observe,
    partial_permutations,
    source_observation,
    source_summary,
    valid_on_rows,
)
from .optimize import (
    SearchRefusal,
    branchless_cost,
    candidate_space,
    direct_leaf_optimum,
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
    semantic = 0
    certificate = 0
    mismatches = 0
    by_actions = []
    for n in range(1, 6):
        local_sem = 0
        local_cert = 0
        for codes in itertools.product(range(5), repeat=n):
            model = one_row_profile(codes)
            row = model["rows"][0]
            if n < 4:
                orders = partial_permutations(model["actions"])
                for order in orders:
                    direct = observe(row, order) != source_observation(row)
                    front = frontier_valid(row, order)
                    semantic += 1
                    local_sem += 1
                    if direct != front:
                        mismatches += 1
                    cert = _certificate_exists(row, order, model["actions"])
                    certificate += 1
                    local_cert += 1
                    if cert != front:
                        mismatches += 1
            else:
                for order in partial_permutations(model["actions"]):
                    direct = observe(row, order) == source_observation(row)
                    front = frontier_valid(row, order)
                    semantic += 1
                    local_sem += 1
                    if direct != front:
                        mismatches += 1
                order = row["source"]
                cert = _certificate_exists(row, order, model["actions"])
                certificate += 1
                local_cert += 1
                if not cert:
                    mismatches += 1
        by_actions.append({"actions": n, "semantic_comparisons": local_sem, "certificate_comparisons": local_cert})
    return {
        "phase": "exhaustive",
        "semantic_comparisons": semantic,
        "certificate_comparisons": certificate,
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
    mismatches = 0
    records = []
    spec = [(2, 4, 100), (3, 3, 30)]
    index = 0
    for bits, actions, count in spec:
        for j in range(count):
            seed = 714031 + index
            model = random_model(seed, bits, actions)
            _save_model(inputs, f"exact-{index:03d}.json", model)
            fast = optimize_tree(model, leaf_mode="auto", candidate_limit=4096)
            oracle = optimize_tree(model, direct_leaf=True, candidate_limit=4096)
            if fast["object_cost"] != oracle["object_cost"]:
                mismatches += 1
            records.append({
                "id": f"exact-{index:03d}",
                "bits": bits,
                "actions": actions,
                "seed": seed,
                "optimizer_cost": fast["object_cost"],
                "oracle_cost": oracle["object_cost"],
                "tree_shapes_in_grammar": tree_shape_count(bits),
            })
            index += 1
    return {"phase": "trees", "instances": len(records), "mismatches": mismatches, "records": records}


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
    for mask in range(1 << len(base)):
        family = [base[i] for i in range(len(base)) if mask & (1 << i)]
        order, residual = ready_schedule(range(3), family)
        brute = [p for p in itertools.permutations(range(3)) if conditions_hold(p, family)]
        if order is not None:
            feasible += 1
            if not conditions_hold(order, family) or not brute:
                mismatches += 1
        else:
            if brute or not residual:
                mismatches += 1
    return {"phase": "and-or", "families": 512, "feasible_families": feasible, "mismatches": mismatches}


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
    for i in range(64):
        bits = 1 + (i % 4)
        actions = 2 + (i % 7)
        seed = 901337 + i
        model = random_model(seed, bits, actions)
        _save_model(inputs, f"baseline-{i:03d}.json", model)
        exact = optimize_tree(model)
        split = fully_split_cost(model)
        branchless = branchless_cost(model)
        refined = optimize_tree(origin_refined_model(model))
        if exact["object_cost"] > split:
            mismatches += 1
        if branchless is not None and exact["object_cost"] > branchless:
            mismatches += 1
        records.append({
            "id": f"baseline-{i:03d}", "bits": bits, "actions": actions, "seed": seed,
            "exact_private_tree": exact["object_cost"], "fully_split": split,
            "branchless": branchless, "origin_refined": refined["object_cost"],
        })
    return {"phase": "baselines", "instances": 64, "mismatches": mismatches, "records": records}


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

    # A valid object with one retained guard mask supports byte-format attacks.
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
    for name, budget, c in [
        ("valid-exact-budget", len(obj), cert),
        ("valid-larger-budget", len(obj) + 100, copy.deepcopy(cert)),
        ("valid-json-key-order-independent", len(obj), dict(reversed(list(cert.items())))),
    ]:
        result = check_certificate(model, obj, c, budget)
        records.append({"name": name, "expected": "accept", "result": result})
        accepted += int(result["accepted"])
        wrong += int(not result["accepted"])

    # Seven semantic attacks use format-valid objects and syntactically replayable certificates.
    for i, (bad_model, order) in enumerate(_semantic_cases()):
        bad_obj = _leaf_object(bad_model, order)
        bad_cert = make_certificate(bad_model, bad_obj)
        result = check_certificate(bad_model, bad_obj, bad_cert, len(bad_obj))
        records.append({"name": f"semantic-{i:02d}", "expected": "reject", "result": result})
        rejected += int(not result["accepted"])
        wrong += int(result["accepted"])

    mutations: List[Tuple[str, bytes, Mapping[str, Any], int]] = []
    b = bytearray(obj); b[0] ^= 1; mutations.append(("bad-magic", bytes(b), cert, len(obj)))
    b = bytearray(obj); b[4] = 0; mutations.append(("wrong-input-width", bytes(b), cert, len(obj)))
    b = bytearray(obj); b[5] = 1; mutations.append(("reserved-byte", bytes(b), cert, len(obj)))
    b = bytearray(obj); b[6] = 0; mutations.append(("unknown-root-tag", bytes(b), cert, len(obj)))
    mutations.append(("truncated", obj[:-1], cert, len(obj)))
    mutations.append(("trailing-byte", obj + b"x", cert, len(obj) + 1))
    b = bytearray(obj); b[9:11] = (65535).to_bytes(2, "little"); mutations.append(("unknown-action", bytes(b), cert, len(obj)))
    duplicate = obj[:7] + (2).to_bytes(2, "little") + obj[9:] + obj[9:]
    mutations.append(("duplicate-action", duplicate, cert, len(duplicate)))
    b = bytearray(obj); b[11] = 2; mutations.append(("unknown-action-flag", bytes(b), cert, len(obj)))
    b = bytearray(obj); b[12] ^= 0x02; mutations.append(("wrong-guard-mask", bytes(b), cert, len(obj)))

    # Certificate attacks.
    cert_mutations: List[Tuple[str, Mapping[str, Any]]] = []
    c = copy.deepcopy(cert); c["format"] = "unknown"; cert_mutations.append(("cert-format", c))
    c = copy.deepcopy(cert); c["input_bits"] = 0; cert_mutations.append(("cert-input-width", c))
    c = copy.deepcopy(cert); c["object_size"] += 1; cert_mutations.append(("cert-object-size", c))
    c = copy.deepcopy(cert); c["leaves"] = "bad"; cert_mutations.append(("cert-leaves-type", c))
    c = copy.deepcopy(cert); c["leaves"] = []; cert_mutations.append(("cert-leaf-count", c))
    c = copy.deepcopy(cert); c["leaves"][0]["cell"] = [1, 0]; cert_mutations.append(("cert-cell", c))
    c = copy.deepcopy(cert); c["leaves"][0]["order"] = []; cert_mutations.append(("cert-order", c))
    c = copy.deepcopy(cert); c["leaves"][0]["witnesses"].pop("1"); cert_mutations.append(("cert-witness-domain", c))

    for name, bad_obj, bad_cert, budget in mutations:
        result = check_certificate(model, bad_obj, bad_cert, budget)
        records.append({"name": name, "expected": "reject", "result": result})
        rejected += int(not result["accepted"]); wrong += int(result["accepted"])
    for name, bad_cert in cert_mutations:
        result = check_certificate(model, obj, bad_cert, len(obj))
        records.append({"name": name, "expected": "reject", "result": result})
        rejected += int(not result["accepted"]); wrong += int(result["accepted"])
    for name, budget in [("budget-one-short", len(obj) - 1), ("budget-negative", -1)]:
        result = check_certificate(model, obj, cert, budget)
        records.append({"name": name, "expected": "reject", "result": result})
        rejected += int(not result["accepted"]); wrong += int(result["accepted"])

    example = out / "example"
    example.mkdir(parents=True, exist_ok=True)
    (example / "region.pfc").write_bytes(obj)
    write_json(example / "model.json", model)
    write_json(example / "certificate.json", cert)
    write_json(example / "check.json", check_certificate(model, obj, cert, len(obj)))
    return {
        "phase": "controls", "cases": len(records), "expected_acceptances": 3,
        "expected_rejections": 27, "accepted": accepted, "rejected": rejected,
        "mismatches": wrong, "records": records,
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
        records.append({"id": f"joint-{i:03d}", "direct": expected, **{k: _solution_cost(v) for k, v in methods.items()}})

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
    for i, n in enumerate(sizes):
        model = many_relevant_model(n)
        _save_model(inputs, f"many-{i:03d}.json", model)
        spaces = candidate_space(model["rows"])
        auto = optimize_leaf(model, (0, 0), "auto", 4096)
        rep = optimize_leaf(model, (0, 0), "representative_tuple", 4096)
        admitted += 2
        optional_cost = None
        try:
            optional = optimize_leaf(model, (0, 0), "optional_subset", 4096)
            optional_cost = _solution_cost(optional)
            admitted += 1
        except SearchRefusal:
            refusals += 1
        expected = 9  # leaf: 3 bytes plus two unconditional actions at 3 bytes each
        if _solution_cost(auto) != expected or _solution_cost(rep) != expected:
            mismatches += 1
        if optional_cost is not None and optional_cost != expected:
            mismatches += 1
        records.append({
            "id": f"many-{i:03d}", "actions": n, "spaces": spaces,
            "leaf_cost": _solution_cost(auto), "optional_cost": optional_cost,
        })
    return {
        "phase": "many-relevant", "instances": 5, "admitted_methods": admitted,
        "explicit_refusals": refusals, "mismatches": mismatches, "records": records,
    }


def phase_replay(out: Path) -> Dict[str, Any]:
    inputs = out / "inputs"
    files = sorted(inputs.glob("*.json"))
    expected = {"exact": 130, "baseline": 64, "joint": 128, "padding": 64, "many": 5}
    actual = {key: sum(p.name.startswith(key + "-") for p in files) for key in expected}
    mismatches = int(actual != expected)
    # Parse and minimally execute every exact retained table without regeneration.
    for p in files:
        model = read_json(p)
        if p.name.startswith("many-"):
            optimize_leaf(model, (0, 0), "representative_tuple", 4096)
        elif p.name.startswith("padding-"):
            optimize_leaf(model, (0, 0), "auto", 4096)
        elif p.name.startswith("joint-"):
            optimize_leaf(model, (0, 0), "auto", 4096)
        else:
            optimize_tree(model)
    return {
        "phase": "retained-input-replay", "input_tables_loaded": len(files),
        "families": actual, "mismatches": mismatches,
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
