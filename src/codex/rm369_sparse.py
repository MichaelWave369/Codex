"""RM-369 E1: sparse procedural field with canonical state snapshots."""

import hashlib
import json

from codex.rm369 import tile

_TILES = tuple(tile(o) for o in range(8))
_MAGIC = b"RM1"
_MAX_RECORDS = 1_000_000


def node_count(depth: int) -> int:
    if type(depth) is not int or not 1 <= depth <= 64:
        raise ValueError("depth must be an integer 1..64")
    return (9**depth - 1) // 8


def node_id(depth: int, path: tuple) -> int:
    node_count(depth)
    if (
        not isinstance(path, tuple)
        or len(path) >= depth
        or any(type(p) is not int or not 0 <= p < 9 for p in path)
    ):
        raise ValueError("invalid physical pocket address")
    result = 0
    for slot in path:
        result = 9 * result + 1 + slot
    return result


class SparseField:
    """Default orientation zero; store only nonzero D4 orientations."""

    def __init__(self, depth: int):
        self._nodes = node_count(depth)
        self._depth = depth
        self._overrides: dict[int, int] = {}

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def changed(self) -> int:
        return len(self._overrides)

    @property
    def key_bytes(self) -> int:
        return max(1, ((self._nodes - 1).bit_length() + 7) // 8)

    def set_orientation(self, path: tuple, orientation: int) -> None:
        key = node_id(self.depth, path)
        if type(orientation) is not int or not 0 <= orientation < 8:
            raise ValueError("invalid orientation")
        if orientation == 0:
            self._overrides.pop(key, None)
        else:
            if key not in self._overrides and self.changed >= _MAX_RECORDS:
                raise ValueError("sparse record cap exceeded")
            self._overrides[key] = orientation

    def read(self, row: int, col: int) -> int:
        side = 3**self.depth
        if any(type(v) is not int or not 0 <= v < side for v in (row, col)):
            raise ValueError("cell outside field")
        key = 0
        value = 0
        scale = side
        for _ in range(self.depth):
            scale //= 3
            r, c = row // scale % 3, col // scale % 3
            value = 9 * value + _TILES[self._overrides.get(key, 0)][r][c] - 1
            key = 9 * key + 1 + 3 * r + c
        return value + 1

    def encode(self) -> bytes:
        header = _MAGIC + bytes([self.depth]) + self.changed.to_bytes(4, "big")
        return header + b"".join(
            key.to_bytes(self.key_bytes, "big") + bytes([orientation])
            for key, orientation in sorted(self._overrides.items())
        )

    @classmethod
    def decode(cls, payload: bytes) -> "SparseField":
        if not isinstance(payload, bytes) or len(payload) < 8 or payload[:3] != _MAGIC:
            raise ValueError("invalid snapshot header")
        field = cls(payload[3])
        count = int.from_bytes(payload[4:8], "big")
        width = field.key_bytes + 1
        if count > min(field._nodes, _MAX_RECORDS) or len(payload) != 8 + count * width:
            raise ValueError("invalid snapshot length or count")
        previous = -1
        for offset in range(8, len(payload), width):
            key = int.from_bytes(payload[offset : offset + width - 1], "big")
            orientation = payload[offset + width - 1]
            if not previous < key < field._nodes or not 1 <= orientation < 8:
                raise ValueError("noncanonical or invalid sparse record")
            field._overrides[key] = orientation
            previous = key
        return field

    def storage(self) -> dict:
        """Logical serialized sizes, not Python heap or measured latency."""
        count = self.changed
        cells = 9**self.depth
        value_width = (cells.bit_length() + 7) // 8
        json_payload = json.dumps(sorted(self._overrides.items()), separators=(",", ":"))
        return {
            "depth": self.depth,
            "virtual_cells": cells,
            "orientation_nodes": self._nodes,
            "changed_nodes": count,
            "sparse_snapshot_bytes": len(self.encode()),
            "dense_packed_orientation_bytes": (3 * self._nodes + 7) // 8,
            "flat_fixed_width_cell_bytes": cells * value_width,
            "sparse_json_bytes": len(json_payload.encode()),
        }


def report() -> dict:
    cases = []
    for depth in (2, 4, 12):
        field = SparseField(depth)
        field.set_orientation((), 1)
        field.set_orientation((8,), 7)
        cases.append(field.storage())
    # Negative control: all ten orientation nodes at depth two are changed.
    field = SparseField(2)
    field.set_orientation((), 1)
    for slot in range(9):
        field.set_orientation((slot,), 1)
    cases.append(field.storage())
    result = {
        "schema": "rm369/e1",
        "evidence": "SIMULATED",
        "authority": "NONE",
        "cases": cases,
        "nonclaims": [
            "Serialized byte counts only; not measured memory or performance.",
            "Known D4 generating family only; no arbitrary-data compression.",
            "No advantage over a conventional sparse map with the same codec.",
        ],
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    return result


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
