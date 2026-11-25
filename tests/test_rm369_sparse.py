import hashlib
import json

import pytest

from codex.rm369 import cell, dense
from codex.rm369_sparse import SparseField, node_count, node_id, report


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_equivalence(depth):
    field = SparseField(depth)
    overrides = {(): 7}
    if depth > 1:
        overrides.update({(i,): (i + 1) % 8 for i in range(9)})
    if depth > 2:
        overrides[(8, 8)] = 5
    for path, orientation in overrides.items():
        field.set_orientation(path, orientation)
    expected = dense(depth, overrides)
    actual = [[field.read(r, c) for c in range(3**depth)] for r in range(3**depth)]
    assert actual == expected
    restored = SparseField.decode(field.encode())
    assert restored.encode() == field.encode()
    assert restored.read(0, 0) == cell(depth, 0, 0, overrides)


def test_sparse_updates_and_canonical_order():
    a, b = SparseField(4), SparseField(4)
    a.set_orientation((8, 8), 7)
    a.set_orientation((), 2)
    b.set_orientation((), 2)
    b.set_orientation((8, 8), 7)
    assert a.encode() == b.encode()
    a.set_orientation((), 0)
    a.set_orientation((8, 8), 0)
    assert a.encode() == SparseField(4).encode()
    assert a.changed == 0


def test_deep_random_access():
    field = SparseField(64)
    field.set_orientation((8,) * 63, 7)
    edge = 3**64 - 1
    assert field.read(edge, edge) == cell(64, edge, edge, {(8,) * 63: 7})
    assert node_id(64, (8,) * 63) == node_count(64) - 1
    assert SparseField.decode(field.encode()).read(edge, edge) == field.read(edge, edge)


def test_reject_invalid():
    field = SparseField(2)
    field.set_orientation((), 1)
    field.set_orientation((8,), 7)
    data = field.encode()
    for bad in (
        data[:-1],
        data + b"x",
        b"BAD" + data[3:],
        data[:3] + b"\x00" + data[4:],
        data[:8] + b"\x00\x00" + data[10:],
        data[:8] + b"\x09\x01" + b"\x09\x07",
        data[:8] + b"\x09\x07" + b"\x00\x01",
        data[:8] + b"\x00\x01" + b"\x0a\x07",
    ):
        with pytest.raises(ValueError):
            SparseField.decode(bad)
    for path in ((9,), (0, 0), (True,)):
        with pytest.raises(ValueError):
            field.set_orientation(path, 1)
    with pytest.raises(ValueError):
        field.set_orientation((), True)
    with pytest.raises(ValueError):
        field.read(-1, 0)


def test_storage_and_receipt():
    result = report()
    cases = result["cases"]
    assert cases[0]["sparse_snapshot_bytes"] == 12
    assert cases[0]["dense_packed_orientation_bytes"] == 4
    assert cases[1]["sparse_snapshot_bytes"] == 14
    assert cases[2]["sparse_snapshot_bytes"] == 20
    assert cases[2]["flat_fixed_width_cell_bytes"] == 9**12 * 5
    assert cases[3]["sparse_snapshot_bytes"] == 28
    assert cases[3]["dense_packed_orientation_bytes"] == 4
    digest = result.pop("receipt_sha256")
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    assert digest == hashlib.sha256(raw).hexdigest()
