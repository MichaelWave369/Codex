"""RM-369 E0: exact, synthetic recursive magic-square Keyholes."""

import argparse
import hashlib
import json

SEED = ((6, 1, 8), (7, 5, 3), (2, 9, 4))


def tile(orientation: int = 0) -> tuple:
    """D4: reflect horizontally first, then rotate clockwise."""
    if type(orientation) is not int or not 0 <= orientation < 8:
        raise ValueError("orientation must be an integer 0..7")
    grid = SEED if orientation < 4 else tuple(row[::-1] for row in SEED)
    for _ in range(orientation % 4):
        grid = tuple(zip(*grid[::-1], strict=True))
    return grid


def _validate_depth(depth: int) -> None:
    if type(depth) is not int or not 1 <= depth <= 64:
        raise ValueError("depth must be an integer 1..64")


def cell(depth: int, row: int, col: int, overrides: dict | None = None) -> int:
    """Random access using physical child addresses; no dense allocation."""
    _validate_depth(depth)
    side = 3**depth
    if any(type(v) is not int or not 0 <= v < side for v in (row, col)):
        raise ValueError("cell outside field")
    overrides = {} if overrides is None else overrides
    for path, orientation in overrides.items():
        if (
            not isinstance(path, tuple)
            or len(path) >= depth
            or any(type(p) is not int or not 0 <= p < 9 for p in path)
        ):
            raise ValueError("invalid physical pocket address")
        tile(orientation)
    value = 0
    path = ()
    for exponent in range(depth - 1, -1, -1):
        scale = 3**exponent
        r, c = row // scale % 3, col // scale % 3
        value = value * 9 + tile(overrides.get(path, 0))[r][c] - 1
        path += (3 * r + c,)
    return value + 1


def constant(depth: int) -> int:
    _validate_depth(depth)
    n = 3**depth
    return n * (n * n + 1) // 2


def dense(depth: int, overrides: dict | None = None) -> list:
    _validate_depth(depth)
    if depth > 4:
        raise ValueError("dense audit capped at depth 4; use cell for deeper access")
    n = 3**depth
    return [[cell(depth, r, c, overrides) for c in range(n)] for r in range(n)]


def audit(grid: list) -> dict:
    """Check actual values and lines, not only the predicted constant."""
    n = len(grid)
    if not n or any(len(row) != n for row in grid):
        raise ValueError("expected nonempty square")
    target = n * (n * n + 1) // 2
    lines = [sum(row) for row in grid]
    lines += [sum(col) for col in zip(*grid, strict=True)]
    lines += [sum(grid[i][i] for i in range(n))]
    lines += [sum(grid[i][n - 1 - i] for i in range(n))]
    normal = sorted(v for row in grid for v in row) == list(range(1, n * n + 1))
    return {
        "side": n,
        "constant": target,
        "normal": normal,
        "all_lines": all(v == target for v in lines),
    }


def identify(observations: dict) -> list[int]:
    """Return every compatible orientation; empty means inconsistent."""
    for pos, value in observations.items():
        if (
            not isinstance(pos, tuple)
            or len(pos) != 2
            or any(type(i) is not int or not 0 <= i < 3 for i in pos)
            or type(value) is not int
        ):
            raise ValueError("invalid observation")
    return [o for o in range(8) if all(tile(o)[r][c] == v for (r, c), v in observations.items())]


def coupling(a: int, b: int) -> int:
    return sum(
        (x - 5) * (y - 5)
        for ar, br in zip(tile(a), tile(b), strict=True)
        for x, y in zip(ar, br, strict=True)
    )


def report() -> dict:
    # Nonuniform child orientations, chosen deterministically.
    rows = []
    for d in range(1, 5):
        changes = {(i,): i % 8 for i in range(9)} if d > 1 else {}
        rows.append(audit(dense(d, changes)))
    pair = [{(0, 0): tile(o)[0][0], (0, 1): tile(o)[0][1]} for o in range(8)]
    result = {
        "schema": "rm369/e0",
        "evidence": "SIMULATED",
        "authority": "NONE",
        "audits": rows,
        "couplings": [coupling(0, o) for o in range(8)],
        "corner_classes": len({tile(o)[0][0] for o in range(8)}),
        "pair_resolves_all": all(identify(p) == [o] for o, p in enumerate(pair)),
        "depth2_root_fixed_orientation_states": 8**9,
        "depth2_root_fixed_orientation_bits": 27,
        "nonclaims": [
            "No verified historical transcription or translation.",
            "No physical holography, neural compression or routing advantage.",
        ],
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(report(), indent=2))


if __name__ == "__main__":
    main()
