"""Canonical byte grammar for certified private-leaf decision trees."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .model import Cell, guard_mask_bytes, guard_true_on_cell, split_cell, validate_model

MAGIC = b"PFC1"
HEADER_SIZE = 6
BRANCH_TAG = ord("B")
LEAF_TAG = ord("L")


class ObjectFormatError(ValueError):
    """Raised for malformed or noncanonical object bytes."""


@dataclass
class _Cursor:
    data: bytes
    pos: int = 0

    def take(self, n: int) -> bytes:
        if type(n) is not int or n < 0:
            raise ObjectFormatError("byte count must be a nonnegative integer")
        if self.pos < 0 or n > len(self.data) - self.pos:
            raise ObjectFormatError("truncated object")
        out = self.data[self.pos : self.pos + n]
        self.pos += n
        return out

    def u8(self) -> int:
        return self.take(1)[0]

    def u16(self) -> int:
        return int.from_bytes(self.take(2), "little")


def _encode_node(model: Mapping[str, Any], node: Mapping[str, Any], cell: Cell) -> bytes:
    if tuple(node.get("cell", cell)) != tuple(cell):
        raise ObjectFormatError("tree cell annotation disagrees with traversal")
    kind = node.get("type")
    if kind == "branch":
        bit = node.get("bit")
        b = int(model["input_bits"])
        if type(bit) is not int or not (0 <= bit < b) or (cell[0] & (1 << bit)):
            raise ObjectFormatError("branch bit is invalid or already fixed")
        left_cell, right_cell = split_cell(cell, bit)
        return (
            bytes((BRANCH_TAG, bit))
            + _encode_node(model, node["left"], left_cell)
            + _encode_node(model, node["right"], right_cell)
        )
    if kind != "leaf":
        raise ObjectFormatError("node type must be branch or leaf")
    order = node.get("order")
    if not isinstance(order, list) or len(order) > 65535 or len(set(order)) != len(order):
        raise ObjectFormatError("leaf order must be a duplicate-free list")
    if any(type(a) is not int or a not in model["actions"] for a in order):
        raise ObjectFormatError("leaf contains an unknown action")
    out = bytearray((LEAF_TAG,))
    out += len(order).to_bytes(2, "little")
    for action in order:
        out += int(action).to_bytes(2, "little")
        if guard_true_on_cell(model, action, cell):
            out.append(0)
        else:
            out.append(1)
            out += guard_mask_bytes(model, action)
    return bytes(out)


def encode_object(model: Mapping[str, Any], tree: Mapping[str, Any]) -> bytes:
    validate_model(model)
    b = int(model["input_bits"])
    return MAGIC + bytes((b, 0)) + _encode_node(model, tree, (0, 0))


def _decode_node(model: Mapping[str, Any], cur: _Cursor, cell: Cell) -> Dict[str, Any]:
    start = cur.pos
    tag = cur.u8()
    if tag == BRANCH_TAG:
        bit = cur.u8()
        b = int(model["input_bits"])
        if not (0 <= bit < b):
            raise ObjectFormatError("branch bit is outside the input domain")
        if cell[0] & (1 << bit):
            raise ObjectFormatError("branch repeats a bit on one path")
        left_cell, right_cell = split_cell(cell, bit)
        left = _decode_node(model, cur, left_cell)
        right = _decode_node(model, cur, right_cell)
        return {
            "type": "branch",
            "cell": [cell[0], cell[1]],
            "bit": bit,
            "left": left,
            "right": right,
            "encoded_offset": start,
            "encoded_size": cur.pos - start,
        }
    if tag != LEAF_TAG:
        raise ObjectFormatError(f"unknown node tag 0x{tag:02x}")
    count = cur.u16()
    order = []
    masks: Dict[str, str | None] = {}
    q = 1 << int(model["input_bits"])
    width = (q + 7) // 8
    for _ in range(count):
        action = cur.u16()
        if action not in model["actions"]:
            raise ObjectFormatError("leaf contains an unknown action")
        if action in order:
            raise ObjectFormatError("leaf repeats an action")
        flag = cur.u8()
        all_true = guard_true_on_cell(model, action, cell)
        if flag == 0:
            if not all_true:
                raise ObjectFormatError("implicit guard used where the guard is not true on the leaf cell")
            masks[str(action)] = None
        elif flag == 1:
            raw = cur.take(width)
            expected = guard_mask_bytes(model, action)
            if raw != expected:
                raise ObjectFormatError("retained guard mask does not match the supplied semantic table")
            if all_true:
                raise ObjectFormatError("noncanonical explicit guard where omission is required")
            masks[str(action)] = raw.hex()
        else:
            raise ObjectFormatError("action flag must be 0 or 1")
        order.append(action)
    return {
        "type": "leaf",
        "cell": [cell[0], cell[1]],
        "order": order,
        "guard_masks": masks,
        "encoded_offset": start,
        "encoded_size": cur.pos - start,
    }


def decode_object(model: Mapping[str, Any], data: bytes) -> Dict[str, Any]:
    validate_model(model)
    if not isinstance(data, (bytes, bytearray)):
        raise ObjectFormatError("object must be bytes")
    cur = _Cursor(bytes(data))
    if cur.take(4) != MAGIC:
        raise ObjectFormatError("bad object magic")
    encoded_bits = cur.u8()
    if encoded_bits != int(model["input_bits"]):
        raise ObjectFormatError("object input width disagrees with the semantic table")
    if cur.u8() != 0:
        raise ObjectFormatError("reserved header byte must be zero")
    tree = _decode_node(model, cur, (0, 0))
    if cur.pos != len(data):
        raise ObjectFormatError("trailing bytes after the decision tree")
    return {"tree": tree, "object_size": len(data), "input_bits": encoded_bits}
