"""Certificate generation and replay for canonical object bytes."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping

from .bytecode import ObjectFormatError, decode_object
from .frontier import canonical_witness, witness_valid
from .model import cell_inputs, observe, rows_by_input, source_observation, validate_model
from .optimize import flatten_leaves


class CertificateError(ValueError):
    """Raised for malformed certificate structures."""


def make_certificate(model: Mapping[str, Any], object_bytes: bytes) -> Dict[str, Any]:
    decoded = decode_object(model, object_bytes)
    by_input = rows_by_input(model)
    leaves = []
    for leaf in flatten_leaves(decoded["tree"]):
        cell = tuple(leaf["cell"])
        witnesses: Dict[str, int | None] = {}
        for x in cell_inputs(model, cell):
            witnesses[str(x)] = canonical_witness(by_input[x], leaf["order"])
        leaves.append({
            "cell": list(cell),
            "order": list(leaf["order"]),
            "witnesses": witnesses,
        })
    return {
        "format": "pfc-certificate-1",
        "input_bits": int(model["input_bits"]),
        "object_size": len(object_bytes),
        "leaves": leaves,
    }


def _reject(reason: str, stage: str, **details: Any) -> Dict[str, Any]:
    """Return a structured rejection with the checker layer that rejected it."""
    return {"accepted": False, "reason": reason, "stage": stage, **details}


def check_certificate(
    model: Mapping[str, Any],
    object_bytes: bytes,
    certificate: Mapping[str, Any],
    budget: int,
) -> Dict[str, Any]:
    try:
        validate_model(model)
    except Exception as exc:  # precise reason is returned to the caller
        return _reject("invalid-model", "model", detail=str(exc))
    if type(budget) is not int or budget < 0:
        return _reject("invalid-budget", "budget")
    if not isinstance(object_bytes, (bytes, bytearray)):
        return _reject("invalid-object", "object", detail="object must be bytes")
    actual_size = len(object_bytes)
    if actual_size > budget:
        return _reject("over-budget", "budget", object_size=actual_size, budget=budget)
    try:
        decoded = decode_object(model, object_bytes)
    except ObjectFormatError as exc:
        return _reject("invalid-object", "object", detail=str(exc))
    if not isinstance(certificate, Mapping):
        return _reject("invalid-certificate", "certificate", detail="certificate must be an object")
    if set(certificate) != {"format", "input_bits", "object_size", "leaves"}:
        return _reject("invalid-certificate", "certificate", detail="certificate fields do not match the closed schema")
    if certificate.get("format") != "pfc-certificate-1":
        return _reject("invalid-certificate", "certificate", detail="unknown certificate format")
    if type(certificate.get("input_bits")) is not int or certificate["input_bits"] != model["input_bits"]:
        return _reject("invalid-certificate", "certificate", detail="input width mismatch")
    if type(certificate.get("object_size")) is not int or certificate["object_size"] != actual_size:
        return _reject("invalid-certificate", "certificate", detail="declared object size mismatch")
    supplied = certificate.get("leaves")
    if not isinstance(supplied, list):
        return _reject("invalid-certificate", "certificate", detail="leaves must be a list")
    actual = flatten_leaves(decoded["tree"])
    if len(supplied) != len(actual):
        return _reject("invalid-certificate", "certificate", detail="leaf count mismatch")

    by_input = rows_by_input(model)
    covered: List[int] = []
    frontier_checks = 0
    direct_checks = 0
    for index, (claim, leaf) in enumerate(zip(supplied, actual)):
        if not isinstance(claim, Mapping):
            return _reject("invalid-certificate", "certificate", detail=f"leaf {index} is not an object")
        if set(claim) != {"cell", "order", "witnesses"}:
            return _reject("invalid-certificate", "certificate", detail=f"leaf {index} fields do not match the closed schema")
        cell = list(leaf["cell"])
        order = list(leaf["order"])
        claimed_cell = claim.get("cell")
        claimed_order = claim.get("order")
        if (
            type(claimed_cell) is not list
            or any(type(value) is not int for value in claimed_cell)
            or type(claimed_order) is not list
            or any(type(value) is not int for value in claimed_order)
            or claimed_cell != cell
            or claimed_order != order
        ):
            return _reject("invalid-certificate", "certificate", detail=f"leaf {index} does not replay the decoded object")
        xs = cell_inputs(model, tuple(cell))
        witnesses = claim.get("witnesses")
        if not isinstance(witnesses, Mapping) or set(witnesses) != {str(x) for x in xs}:
            return _reject("invalid-certificate", "certificate", detail=f"leaf {index} witness domain mismatch")
        for x in xs:
            row = by_input[x]
            witness = witnesses[str(x)]
            if witness is not None and type(witness) is not int:
                return _reject("invalid-certificate", "certificate", detail=f"input {x} witness is not an action or null")
            frontier_checks += 1
            if not witness_valid(row, order, witness):
                return _reject("semantic-mismatch", "semantic", input=x, leaf=index, check="frontier-witness")
            # The direct interpreter is a defense-in-depth replay of the declared
            # finite table, not the argument used to prove Theorem 1.
            direct_checks += 1
            if observe(row, order) != source_observation(row):
                return _reject("semantic-mismatch", "semantic", input=x, leaf=index, check="direct-trace")
            covered.append(x)
    expected = list(range(1 << int(model["input_bits"])))
    if sorted(covered) != expected or len(covered) != len(set(covered)):
        return _reject("invalid-certificate", "certificate", detail="decoded leaves do not partition the input domain")
    return {
        "accepted": True,
        "reason": "ok",
        "stage": "accept",
        "object_size": actual_size,
        "budget": budget,
        "leaves": len(actual),
        "frontier_checks": frontier_checks,
        "direct_checks": direct_checks,
    }
