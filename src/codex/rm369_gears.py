"""RM-369 E2: reversible physical-pocket gears, not live ABL execution."""

import hashlib
import json

from codex.rm369_sparse import SparseField, node_id

_MAX_OPS = 4096


def _gear(value: int) -> int:
    if type(value) is not int or not 0 <= value < 8:
        raise ValueError("gear must be an integer 0..7")
    return value


def compose(after: int, before: int) -> int:
    """Return after composed with before, in E0's R^r F^f convention."""
    a, b = _gear(after), _gear(before)
    rotation = (a % 4 + (-1 if a >= 4 else 1) * (b % 4)) % 4
    reflection = (a >= 4) != (b >= 4)
    return rotation + 4 * int(reflection)


def inverse(gear: int) -> int:
    g = _gear(gear)
    return g if g >= 4 else (-g) % 4


def coordinate(side: int, row: int, col: int, gear: int) -> tuple[int, int]:
    """Active coordinate transform; does not change any stored pocket."""
    g = _gear(gear)
    if type(side) is not int or side < 1:
        raise ValueError("invalid side")
    if any(type(v) is not int or not 0 <= v < side for v in (row, col)):
        raise ValueError("coordinate outside field")
    if g >= 4:
        col = side - 1 - col
    for _ in range(g % 4):
        row, col = col, side - 1 - row
    return row, col


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def execute(snapshot: bytes, operations: list, *, fuel: int) -> tuple[bytes, dict]:
    """Apply a bounded local-edit program atomically to an immutable snapshot.

    Each instruction is [physical_path, gear]. Paths are lists of slots.
    The caller supplies fuel; it is a step budget, not CPU/memory metering.
    """
    if type(fuel) is not int or not 0 <= fuel <= _MAX_OPS:
        raise ValueError("invalid fuel")
    if not isinstance(operations, list) or len(operations) > fuel:
        raise ValueError("invalid program or insufficient fuel")
    field = SparseField.decode(snapshot)
    parsed = []
    for instruction in operations:
        if not isinstance(instruction, list) or len(instruction) != 2:
            raise ValueError("invalid instruction")
        raw_path, gear = instruction
        if not isinstance(raw_path, list):
            raise ValueError("path must be a list")
        path = tuple(raw_path)
        node_id(field.depth, path)
        parsed.append((path, _gear(gear)))
    steps = []
    undo = []
    for path, gear in parsed:
        before = field.orientation(path)
        after = compose(gear, before)
        field.set_orientation(path, after)
        steps.append({"path": list(path), "gear": gear, "before": before, "after": after})
        undo.append([list(path), inverse(gear)])
    output = field.encode()
    receipt = {
        "schema": "rm369/e2",
        "evidence": "SIMULATED",
        "authority": "NONE",
        "operation_kind": "physical_slot_local_orientation",
        "input_sha256": _digest(snapshot),
        "output_sha256": _digest(output),
        "fuel_initial": fuel,
        "fuel_remaining": fuel - len(steps),
        "steps": steps,
        "inverse_program": undo[::-1],
    }
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = _digest(raw)
    return output, receipt


def report() -> dict:
    field = SparseField(12)
    field.set_orientation((8, 3, 6), 7)
    original = field.encode()
    ops = [[[8, 3, 6], 1], [[8, 3, 6], 4], [[], 2]]
    output, receipt = execute(original, ops, fuel=3)
    restored, _ = execute(output, receipt["inverse_program"], fuel=3)
    return {
        "schema": "rm369/e2-demo",
        "evidence": "SIMULATED",
        "authority": "NONE",
        "rotate_after_reflect": compose(1, 4),
        "reflect_after_rotate": compose(4, 1),
        "roundtrip_exact": restored == original,
        "receipt": receipt,
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
