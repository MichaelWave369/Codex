"""Voynich-inspired cross-text hypothesis testing, not manuscript decipherment.

Operator assignments are *human-supplied interpretations*. The engine tests
whether their ordered transitions coincide more than shuffled controls do.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from itertools import combinations
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "vgve-cross-text/0.1"
OPERATORS = frozenset(
    {
        "BIND",
        "CYCLE",
        "DIFFERENTIATE",
        "DISSOLVE",
        "EMBODY",
        "EXPERIENCE",
        "FLOW",
        "GROW",
        "INTEGRATE",
        "MIRROR",
        "RECURSE",
        "RENEW",
        "RETURN",
        "TRANSFORM",
    }
)
CLAIM_LABELS = frozenset({"ARCHITECTURAL MAPPING", "EMPIRICAL HYPOTHESIS", "NON-CLAIM"})
BOUNDARY = (
    "Exploratory comparison of human-assigned symbolic operators only. "
    "This is not a Voynich decipherment, proof of a shared ancient source, "
    "or evidence for metaphysical or biological mechanisms."
)


class PacketError(ValueError):
    """A research packet lacks required provenance or epistemic safeguards."""


def _nonempty(value: Any, description: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PacketError(f"{description} must be non-empty text")
    return value.strip()


def _validate(packet: dict[str, Any]) -> list[dict[str, Any]]:
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise PacketError(f"schema_version must be {SCHEMA_VERSION}")
    _nonempty(packet.get("hypothesis"), "hypothesis")
    if packet.get("claimed_decipherment") is not False:
        raise PacketError("claimed_decipherment must explicitly be false")

    records = packet.get("records")
    if not isinstance(records, list) or len(records) < 2:
        raise PacketError("records must contain at least two source records")
    ids: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise PacketError("each record must be an object")
        identifier = _nonempty(record.get("id"), "record.id")
        if identifier in ids:
            raise PacketError(f"duplicate record.id: {identifier}")
        ids.add(identifier)
        _nonempty(record.get("tradition"), f"{identifier}.tradition")
        source = record.get("source")
        if not isinstance(source, dict):
            raise PacketError(f"{identifier}.source must be an object")
        for key in ("title", "reference"):
            _nonempty(source.get(key), f"{identifier}.source.{key}")
        if source.get("kind") not in {"synthetic", "historical"}:
            raise PacketError(f"{identifier}.source.kind must be synthetic or historical")
        if source["kind"] == "historical":
            _nonempty(source.get("url"), f"{identifier}.source.url")
        if record.get("claim_label") not in CLAIM_LABELS:
            raise PacketError(f"{identifier}.claim_label must be a supported claim label")
        _nonempty(record.get("counter_hypothesis"), f"{identifier}.counter_hypothesis")
        anchors = record.get("anchors")
        if not isinstance(anchors, list) or len(anchors) < 2:
            raise PacketError(f"{identifier}.anchors requires at least two ordered annotations")
        for index, anchor in enumerate(anchors):
            prefix = f"{identifier}.anchors[{index}]"
            if not isinstance(anchor, dict):
                raise PacketError(f"{prefix} must be an object")
            if anchor.get("operator") not in OPERATORS:
                raise PacketError(f"{prefix}.operator is not in the declared grammar")
            evidence = _nonempty(anchor.get("evidence"), f"{prefix}.evidence")
            _nonempty(anchor.get("location"), f"{prefix}.location")
            if anchor.get("kind") == "text":
                excerpt = _nonempty(source.get("text"), f"{identifier}.source.text")
                if evidence not in excerpt:
                    raise PacketError(f"{prefix}.evidence is not an exact source.text substring")
            elif anchor.get("kind") != "visual":
                raise PacketError(f"{prefix}.kind must be text or visual")
    return records


def _transitions(operators: list[str]) -> set[tuple[str, str]]:
    return set(zip(operators, operators[1:], strict=False))


def _score(first: list[str], second: list[str]) -> float:
    """Jaccard overlap between sets of adjacent operator transitions."""
    a, b = _transitions(first), _transitions(second)
    return len(a & b) / len(a | b) if a | b else 0.0


def _permutation_p(first: list[str], second: list[str], observed: float) -> float:
    """One-sided within-record shuffle baseline; exploratory, not confirmatory."""
    randomizer = random.Random(369)
    at_least_as_high = 0
    samples = 199
    for _ in range(samples):
        shuffled = second.copy()
        randomizer.shuffle(shuffled)
        if _score(first, shuffled) >= observed - 1e-12:
            at_least_as_high += 1
    return (1 + at_least_as_high) / (1 + samples)


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )


def compare(packet: dict[str, Any]) -> dict[str, Any]:
    """Run the guarded cross-text comparison and emit a verifiable receipt."""
    records = _validate(packet)
    comparisons = []
    for left, right in combinations(records, 2):
        if left["tradition"] == right["tradition"]:
            continue
        left_ops = [anchor["operator"] for anchor in left["anchors"]]
        right_ops = [anchor["operator"] for anchor in right["anchors"]]
        observed = _score(left_ops, right_ops)
        comparisons.append(
            {
                "left_id": left["id"],
                "right_id": right["id"],
                "transition_jaccard": round(observed, 6),
                "shuffle_p_exploratory": round(_permutation_p(left_ops, right_ops, observed), 6),
                "shared_transitions": [
                    list(pair) for pair in sorted(_transitions(left_ops) & _transitions(right_ops))
                ],
                "counter_hypotheses": [
                    left["counter_hypothesis"],
                    right["counter_hypothesis"],
                ],
            }
        )
    if not comparisons:
        raise PacketError("at least two distinct traditions are required for comparison")

    output = {
        "schema_version": SCHEMA_VERSION,
        "hypothesis": packet["hypothesis"],
        "claim_label": "ARCHITECTURAL MAPPING",
        "boundary": BOUNDARY,
        "analysis_steps": [
            "Observe",
            "Anchor",
            "Map",
            "Score",
            "Guard",
            "Counter-check",
            "Emit",
            "Receipt",
        ],
        "method": {
            "operators": sorted(OPERATORS),
            "similarity": "Jaccard overlap of adjacent human-assigned operator pairs",
            "null": "199 seeded shuffles of right-hand record (preserves label frequencies)",
            "seed": 369,
            "limitations": [
                "Annotations are supplied by analysts, not inferred from glyph meanings.",
                "A shuffled-label null does not control for cultural borrowing or annotation bias.",
                "Exploratory p-values are not corrected for multiple comparisons.",
                "Synthetic examples cannot establish historical or linguistic claims.",
            ],
        },
        "sources": [
            {
                "id": record["id"],
                "tradition": record["tradition"],
                "source": record["source"],
                "claim_label": record["claim_label"],
                "counter_hypothesis": record["counter_hypothesis"],
                "anchors": record["anchors"],
            }
            for record in records
        ],
        "comparisons": comparisons,
        "review_status": "NOT VALIDATED; HUMAN REVIEW REQUIRED",
    }
    output["receipt_sha256"] = hashlib.sha256(_canonical(output)).hexdigest()
    return output


def main() -> None:
    """Command-line JSON packet processor with no network access or third-party deps."""
    parser = argparse.ArgumentParser(description="Guarded Voynich symbolic comparison")
    parser.add_argument("input", type=Path, help="Path to annotated research packet JSON")
    parser.add_argument("--out", type=Path, help="Write the canonical JSON receipt to this path")
    args = parser.parse_args()
    try:
        packet = json.loads(args.input.read_text(encoding="utf-8"))
        result = compare(packet)
    except (PacketError, json.JSONDecodeError) as error:
        parser.error(str(error))
    rendered = json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.out} (SHA-256: {result['receipt_sha256']})")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
