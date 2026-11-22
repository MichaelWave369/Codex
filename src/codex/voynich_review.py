"""Hypothesis-blind Voynich region reviews with source-bound agreement receipts.

This module does not interpret manuscript imagery. It generates objective,
predefined rectangular regions and compares independently supplied labels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from codex.voynich_engine import OPERATORS
from codex.voynich_sources import AtlasError, blank_assignments

PROTOCOL_SCHEMA = "vgve-region-protocol/0.1"
SUBMISSION_SCHEMA = "vgve-region-review/0.1"
REPORT_SCHEMA = "vgve-review-agreement/0.1"
ABSTENTION_LABELS = frozenset({"NO_PATTERN", "UNDECIDED"})
ALLOWED_LABELS = OPERATORS | ABSTENTION_LABELS


class ReviewError(ValueError):
    """A review violates its preregistered protocol or provenance restrictions."""


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def _signed(value: dict[str, Any]) -> dict[str, Any]:
    value["receipt_sha256"] = hashlib.sha256(_canonical(value)).hexdigest()
    return value


def _verify(value: dict[str, Any], schema: str) -> None:
    if not isinstance(value, dict) or value.get("schema_version") != schema:
        raise ReviewError(f"Expected {schema} document")
    receipt = value.get("receipt_sha256")
    unsigned = {key: item for key, item in value.items() if key != "receipt_sha256"}
    if not isinstance(receipt, str) or receipt != hashlib.sha256(_canonical(unsigned)).hexdigest():
        raise ReviewError("Missing or invalid SHA-256 document receipt")


def create_protocol(
    atlas: dict[str, Any], folios: list[str], *, rows: int = 2, cols: int = 2
) -> dict[str, Any]:
    """Generate predetermined spatial cells from an intact Yale folio atlas."""
    if not 1 <= rows <= 8 or not 1 <= cols <= 8 or rows * cols > 64:
        raise ReviewError("Grid must have 1..8 rows/columns and at most 64 cells per folio")
    if len(folios) > 50:
        raise ReviewError("A protocol supports at most 50 selected folios")
    try:
        prepared = blank_assignments(atlas, folios)
    except AtlasError as error:
        raise ReviewError(str(error)) from error

    regions = []
    for item in prepared["assignments"]:
        for row in range(rows):
            for col in range(cols):
                regions.append(
                    {
                        "region_id": f"{item['folio']}:r{row + 1}c{col + 1}",
                        "folio": item["folio"],
                        "canvas_id": item["canvas_id"],
                        "image_url": item["image_url"],
                        "source_label": item["source_label"],
                        "bbox_per_mille": [
                            1000 * col // cols,
                            1000 * row // rows,
                            1000 * (col + 1) // cols,
                            1000 * (row + 1) // rows,
                        ],
                    }
                )
    protocol = {
        "schema_version": PROTOCOL_SCHEMA,
        "atlas_receipt_sha256": atlas["receipt_sha256"],
        "manifest_sha256": atlas["manifest_sha256"],
        "catalog_url": atlas["catalog_url"],
        "region_policy": "Predefined fixed grid, not manually selected symbolic features",
        "grid": {"rows": rows, "cols": cols},
        "labels": sorted(ALLOWED_LABELS),
        "regions": regions,
        "blinding_instruction": (
            "Independently annotate each rectangular region before viewing any other "
            "reviewer's answers or a preferred cosmological interpretation."
        ),
        "limitations": (
            "Regions are mechanical grid cells, not verified figures; labels are subjective "
            "and depend on a locked codebook. This is not a manuscript translation."
        ),
        "review_status": "PREPARED; NO HUMAN LABELS COLLECTED",
    }
    return _signed(protocol)


def blank_review(protocol: dict[str, Any], reviewer_id: str) -> dict[str, Any]:
    """Create an unfilled sheet with all required region identifiers."""
    _verify(protocol, PROTOCOL_SCHEMA)
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ReviewError("reviewer_id is required")
    return _signed(
        {
            "schema_version": SUBMISSION_SCHEMA,
            "protocol_receipt_sha256": protocol["receipt_sha256"],
            "atlas_receipt_sha256": protocol["atlas_receipt_sha256"],
            "reviewer_id": reviewer_id.strip(),
            "blinding_asserted": False,
            "annotations": [
                {
                    "region_id": item["region_id"],
                    "operator": None,
                    "evidence": "",
                    "counter_hypothesis": "",
                }
                for item in protocol["regions"]
            ],
            "status": "UNANNOTATED",
        }
    )


def _checked_annotations(
    protocol: dict[str, Any], submission: dict[str, Any]
) -> dict[str, dict[str, str]]:
    _verify(submission, SUBMISSION_SCHEMA)
    if submission.get("protocol_receipt_sha256") != protocol["receipt_sha256"]:
        raise ReviewError("Review is not bound to this protocol")
    if submission.get("atlas_receipt_sha256") != protocol["atlas_receipt_sha256"]:
        raise ReviewError("Review source atlas hash mismatch")
    if submission.get("blinding_asserted") is not True:
        raise ReviewError("Reviewer must assert independent, hypothesis-blind annotation")
    if submission.get("status") != "COMPLETE":
        raise ReviewError("Only COMPLETE review sheets may be scored")
    if not isinstance(submission.get("reviewer_id"), str) or not submission["reviewer_id"].strip():
        raise ReviewError("Review must identify its reviewer")

    expected = {region["region_id"] for region in protocol["regions"]}
    actual: dict[str, dict[str, str]] = {}
    annotations = submission.get("annotations")
    if not isinstance(annotations, list):
        raise ReviewError("Review annotations must be a list")
    for annotation in annotations:
        if not isinstance(annotation, dict):
            raise ReviewError("Each review annotation must be an object")
        region_id = annotation.get("region_id")
        if not isinstance(region_id, str) or region_id not in expected:
            raise ReviewError(f"Unknown review region: {region_id}")
        if region_id in actual:
            raise ReviewError(f"Duplicate review region: {region_id}")
        operator = annotation.get("operator")
        if not isinstance(operator, str) or operator not in ALLOWED_LABELS:
            raise ReviewError(f"Missing or invalid operator for {region_id}")
        evidence = annotation.get("evidence")
        counter = annotation.get("counter_hypothesis")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ReviewError(f"Missing observation/rationale for {region_id}")
        if operator not in ABSTENTION_LABELS and (
            not isinstance(counter, str) or not counter.strip()
        ):
            raise ReviewError(f"Counter-hypothesis required for {region_id}")
        actual[region_id] = annotation
    if set(actual) != expected:
        raise ReviewError("Review coverage does not equal the complete preselected region set")
    return actual


def seal_review(protocol: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    """Check a completed edited review against its protocol and update its checksum."""
    _verify(protocol, PROTOCOL_SCHEMA)
    if not isinstance(submission, dict):
        raise ReviewError("Review must be a JSON object")
    candidate = {key: value for key, value in submission.items() if key != "receipt_sha256"}
    _signed(candidate)
    _checked_annotations(protocol, candidate)
    return candidate


def compare_reviews(
    protocol: dict[str, Any], first: dict[str, Any], second: dict[str, Any]
) -> dict[str, Any]:
    """Calculate observed agreement and Cohen's kappa over locked region IDs."""
    _verify(protocol, PROTOCOL_SCHEMA)
    a = _checked_annotations(protocol, first)
    b = _checked_annotations(protocol, second)
    if first["reviewer_id"].strip() == second["reviewer_id"].strip():
        raise ReviewError("Reviews must come from two different reviewer identifiers")

    ids = [region["region_id"] for region in protocol["regions"]]
    labels_a = [a[key]["operator"] for key in ids]
    labels_b = [b[key]["operator"] for key in ids]
    n = len(ids)
    matches = sum(x == y for x, y in zip(labels_a, labels_b, strict=True))
    observed = matches / n
    freq_a, freq_b = Counter(labels_a), Counter(labels_b)
    expected = sum(freq_a[label] * freq_b[label] / (n * n) for label in ALLOWED_LABELS)
    if abs(1.0 - expected) < 1e-12:
        kappa = None
        kappa_note = "Undefined: both reviewers used a single identical label throughout"
    else:
        kappa = round((observed - expected) / (1 - expected), 6)
        kappa_note = "Descriptive inter-rater agreement, not validation of symbol meanings"

    disagreements = [
        {
            "region_id": key,
            "first_label": a[key]["operator"],
            "second_label": b[key]["operator"],
            "first_evidence": a[key]["evidence"],
            "second_evidence": b[key]["evidence"],
        }
        for key in ids
        if a[key]["operator"] != b[key]["operator"]
    ]
    return _signed(
        {
            "schema_version": REPORT_SCHEMA,
            "protocol_receipt_sha256": protocol["receipt_sha256"],
            "source_manifest_sha256": protocol["manifest_sha256"],
            "review_receipts": [
                first["receipt_sha256"],
                second["receipt_sha256"],
            ],
            "reviewers": [first["reviewer_id"], second["reviewer_id"]],
            "regions_compared": n,
            "raw_agreement": round(observed, 6),
            "chance_expected_agreement": round(expected, 6),
            "cohen_kappa": kappa,
            "kappa_note": kappa_note,
            "operator_disagreements": disagreements,
            "agreement_counts": {"agreed": matches, "disagreed": n - matches},
            "claim_label": "EMPIRICAL HYPOTHESIS",
            "review_status": "ANALYST AGREEMENT ONLY; HISTORICAL MEANING NOT VALIDATED",
            "limitations": (
                "High agreement can reflect shared training, cultural priming or an overly "
                "simple codebook; grid cells are not identified structures. Two reviewers "
                "are insufficient to establish an ancient decoding scheme."
            ),
        }
    )


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """CLI for building neutral review grids and scoring two completed reviews."""
    parser = argparse.ArgumentParser(description="VGVE blinded annotation agreement workflow")
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("protocol")
    setup.add_argument("atlas", type=Path)
    setup.add_argument("--folio", action="append", required=True)
    setup.add_argument("--rows", type=int, default=2)
    setup.add_argument("--cols", type=int, default=2)
    setup.add_argument("--out", type=Path, required=True)
    sheet = commands.add_parser("blank")
    sheet.add_argument("protocol", type=Path)
    sheet.add_argument("--reviewer", required=True)
    sheet.add_argument("--out", type=Path, required=True)
    seal = commands.add_parser("seal")
    seal.add_argument("protocol", type=Path)
    seal.add_argument("edited_review", type=Path)
    seal.add_argument("--out", type=Path, required=True)
    score = commands.add_parser("score")
    score.add_argument("protocol", type=Path)
    score.add_argument("first", type=Path)
    score.add_argument("second", type=Path)
    score.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    try:
        if args.command == "protocol":
            result = create_protocol(
                _read(args.atlas), args.folio, rows=args.rows, cols=args.cols
            )
        elif args.command == "blank":
            result = blank_review(_read(args.protocol), args.reviewer)
        elif args.command == "seal":
            result = seal_review(_read(args.protocol), _read(args.edited_review))
        else:
            result = compare_reviews(
                _read(args.protocol), _read(args.first), _read(args.second)
            )
    except (ReviewError, AtlasError, ValueError) as error:
        parser.error(str(error))
    _write(args.out, result)
    print(f"Wrote {args.out} (SHA-256: {result['receipt_sha256']})")


if __name__ == "__main__":
    main()
