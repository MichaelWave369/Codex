import hashlib
import json

import pytest

from codex.rm369 import audit, cell, constant, coupling, dense, identify, report, tile


def test_orientations():
    assert len({tile(o) for o in range(8)}) == 8
    for o in range(8):
        grid = tile(o)
        assert audit(grid)["all_lines"]
        assert audit(grid)["normal"]
        assert identify({(0, 0): grid[0][0], (0, 1): grid[0][1]}) == [o]
        assert len(identify({(0, 0): grid[0][0]})) == 2
    assert identify({(1, 1): 5}) == list(range(8))
    assert identify({(1, 1): 6}) == []
    assert [coupling(0, o) for o in range(8)] == [60, 0, -60, 0, 36, 48, -36, -48]


@pytest.mark.parametrize("depth,target", [(1, 15), (2, 369), (3, 9855), (4, 265761)])
def test_recursive_invariance(depth, target):
    overrides = {(): 7}
    if depth > 1:
        overrides.update({(i,): i % 8 for i in range(9)})
    if depth > 2:
        overrides[(8, 8)] = 5
    grid = dense(depth, overrides)
    assert audit(grid) == {
        "side": 3**depth,
        "constant": target,
        "normal": True,
        "all_lines": True,
    }
    assert constant(depth) == target


def test_negative_controls():
    grid = dense(2)
    grid[0][0], grid[0][1] = grid[0][1], grid[0][0]
    assert audit(grid)["normal"]
    assert not audit(grid)["all_lines"]
    for invalid in ({(9,): 0}, {(0, 0): 1}, {(): 8}):
        with pytest.raises(ValueError):
            cell(2, 0, 0, invalid)
    with pytest.raises(ValueError):
        cell(2, -1, 0)
    with pytest.raises(ValueError):
        dense(5)


def test_sparse_access_and_receipt():
    depth = 32
    center = (3**depth - 1) // 2
    assert cell(depth, center, center) == (9**depth + 1) // 2
    result = report()
    assert result == report()
    digest = result.pop("receipt_sha256")
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    assert digest == hashlib.sha256(raw).hexdigest()
