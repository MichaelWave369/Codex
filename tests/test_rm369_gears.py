import hashlib
import json

import pytest

from codex.rm369 import audit, tile
from codex.rm369_gears import compose, coordinate, execute, inverse, report
from codex.rm369_sparse import SparseField


def test_group_laws():
    for a in range(8):
        assert compose(a, 0) == compose(0, a) == a
        assert compose(a, inverse(a)) == compose(inverse(a), a) == 0
        for b in range(8):
            for c in range(8):
                assert compose(a, compose(b, c)) == compose(compose(a, b), c)
            for r in range(3):
                for c in range(3):
                    x, y = coordinate(3, r, c, b)
                    u, v = coordinate(3, x, y, a)
                    assert (u, v) == coordinate(3, r, c, compose(a, b))
                    assert tile(compose(a, b))[u][v] == tile(0)[r][c]
    assert compose(1, 4) == 5
    assert compose(4, 1) == 7


def test_atomic_program_and_roundtrip():
    field = SparseField(3)
    field.set_orientation((8, 3), 7)
    field.set_orientation((0,), 5)
    initial = field.encode()
    operations = [[[8, 3], 1], [[], 4], [[8, 3], 4], [[0], 2]]
    output, receipt = execute(initial, operations, fuel=6)
    changed = SparseField.decode(output)
    assert changed.orientation((8, 3)) == compose(4, compose(1, 7))
    assert changed.orientation((0,)) == compose(2, 5)
    assert changed.orientation(()) == 4
    assert receipt["fuel_remaining"] == 2
    assert receipt["input_sha256"] == hashlib.sha256(initial).hexdigest()
    assert receipt["output_sha256"] == hashlib.sha256(output).hexdigest()
    restored, _ = execute(output, receipt["inverse_program"], fuel=4)
    assert restored == initial
    grid = [[changed.read(r, c) for c in range(27)] for r in range(27)]
    assert audit(grid)["all_lines"]
    assert audit(grid)["normal"]
    assert execute(initial, operations, fuel=6) == (output, receipt)
    digest = receipt.pop("receipt_sha256")
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(raw).hexdigest() == digest


def test_physical_slots_not_subtree_rotation():
    field = SparseField(2)
    field.set_orientation((0,), 7)
    snapshot = field.encode()
    output, _ = execute(snapshot, [[[], 1]], fuel=1)
    changed = SparseField.decode(output)
    assert changed.orientation((0,)) == 7
    assert changed.orientation((2,)) == 0
    # A genuine whole-grid rotation moves the original top-left cell.
    r, c = coordinate(9, 0, 0, 1)
    assert changed.read(r, c) != field.read(0, 0)


def test_refusals():
    snapshot = SparseField(2).encode()
    for ops in (
        [[[0], 1], [[9], 2]],
        [[[], True]],
        [[[], 8]],
        [[[0, 0], 1]],
        [[[], 1, 2]],
        [((), 1)],
    ):
        with pytest.raises(ValueError):
            execute(snapshot, ops, fuel=2)
    for fuel in (-1, True, 4097, 0):
        with pytest.raises(ValueError):
            execute(snapshot, [[[], 1]], fuel=fuel)
    with pytest.raises(ValueError):
        execute(b"bad", [], fuel=0)
    assert execute(snapshot, [], fuel=0)[0] == snapshot
    assert execute(snapshot, [[[], 0]], fuel=1)[0] == snapshot


def test_deep_demo():
    assert report()["roundtrip_exact"]
    field = SparseField(64)
    path = [8] * 63
    snapshot = field.encode()
    output, receipt = execute(snapshot, [[path, 5]], fuel=1)
    assert SparseField.decode(output).orientation(tuple(path)) == 5
    assert execute(output, receipt["inverse_program"], fuel=1)[0] == snapshot
