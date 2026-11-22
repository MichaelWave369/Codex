"""Regressions for hypothesis-blind annotation protocol and inter-rater review."""

import copy
import hashlib
import json

import pytest

from codex.voynich_review import (
    ReviewError,
    blank_review,
    compare_reviews,
    create_protocol,
    seal_review,
)
from codex.voynich_sources import MANIFEST_URL, atlas_from_manifest


def _atlas() -> dict:
    """All source details below are artificial IIIF test data, not real folios."""
    raw = json.dumps(
        {
            "id": MANIFEST_URL,
            "type": "Manifest",
            "items": [
                {
                    "id": "https://example.org/fictional-canvas",
                    "label": {"en": ["f78r"]},
                    "items": [
                        {
                            "items": [
                                {
                                    "motivation": "painting",
                                    "body": {"id": "https://example.org/fictional-scan.jpg"},
                                }
                            ]
                        }
                    ],
                }
            ],
        }
    ).encode("utf-8")
    return atlas_from_manifest(raw)


def _protocol() -> dict:
    return create_protocol(_atlas(), ["f78r"])


def _filled(protocol: dict, reviewer_id: str, labels: list[str] | None = None) -> dict:
    labels = labels or ["BIND", "FLOW", "RETURN", "NO_PATTERN"]
    result = blank_review(protocol, reviewer_id)
    result["blinding_asserted"] = True
    result["status"] = "COMPLETE"
    for annotation, label in zip(result["annotations"], labels, strict=True):
        annotation["operator"] = label
        annotation["evidence"] = "Independent visual observation for the predefined grid cell"
        annotation["counter_hypothesis"] = (
            "An unrelated illustration or ordinary decorative feature"
            if label != "NO_PATTERN"
            else ""
        )
    unsigned = {key: value for key, value in result.items() if key != "receipt_sha256"}
    canonical = json.dumps(unsigned, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    result["receipt_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return result


def test_grid_protocol_uses_only_canvas_metadata() -> None:
    protocol = _protocol()
    assert protocol["grid"] == {"rows": 2, "cols": 2}
    assert len(protocol["regions"]) == 4
    assert protocol["regions"][0]["bbox_per_mille"] == [0, 0, 500, 500]
    assert protocol["regions"][-1]["bbox_per_mille"] == [500, 500, 1000, 1000]
    assert protocol["regions"][0]["canvas_id"] == "https://example.org/fictional-canvas"
    assert protocol["review_status"].startswith("PREPARED")


def test_protocol_is_deterministic_and_binds_raw_manifest() -> None:
    a, b = _protocol(), _protocol()
    assert a == b
    assert a["manifest_sha256"] == _atlas()["manifest_sha256"]
    assert len(a["receipt_sha256"]) == 64


def test_blank_sheet_never_inserts_hypothesis_labels() -> None:
    review = blank_review(_protocol(), "analyst-01")
    assert review["blinding_asserted"] is False
    assert review["status"] == "UNANNOTATED"
    assert all(item["operator"] is None for item in review["annotations"])
    assert all(item["counter_hypothesis"] == "" for item in review["annotations"])


def test_identical_diverse_reviewers_have_perfect_kappa() -> None:
    protocol = _protocol()
    result = compare_reviews(protocol, _filled(protocol, "a"), _filled(protocol, "b"))
    assert result["raw_agreement"] == 1.0
    assert result["cohen_kappa"] == 1.0
    assert result["operator_disagreements"] == []
    assert result["regions_compared"] == 4


def test_disagreement_is_reported_with_cell_and_evidence() -> None:
    protocol = _protocol()
    one = _filled(protocol, "a")
    two = _filled(protocol, "b", ["BIND", "FLOW", "EXPERIENCE", "NO_PATTERN"])
    result = compare_reviews(protocol, one, two)
    assert result["raw_agreement"] == 0.75
    assert 0 < result["cohen_kappa"] < 1
    assert len(result["operator_disagreements"]) == 1
    assert result["operator_disagreements"][0]["region_id"] == "f78r:r2c1"


def test_constant_agreement_reports_undefined_kappa() -> None:
    protocol = _protocol()
    first = _filled(protocol, "a", ["NO_PATTERN"] * 4)
    second = _filled(protocol, "b", ["NO_PATTERN"] * 4)
    result = compare_reviews(protocol, first, second)
    assert result["raw_agreement"] == 1
    assert result["cohen_kappa"] is None
    assert "Undefined" in result["kappa_note"]


def test_rejects_same_reviewer_identifier() -> None:
    protocol = _protocol()
    with pytest.raises(ReviewError, match="two different"):
        compare_reviews(protocol, _filled(protocol, "a"), _filled(protocol, "a"))


def test_rejects_incomplete_review() -> None:
    protocol = _protocol()
    with pytest.raises(ReviewError, match="independent"):
        compare_reviews(protocol, blank_review(protocol, "a"), _filled(protocol, "b"))


def test_rejects_missing_counter_hypothesis() -> None:
    protocol = _protocol()
    first = _filled(protocol, "a")
    first["annotations"][0]["counter_hypothesis"] = ""
    with pytest.raises(ReviewError, match="invalid SHA-256"):
        compare_reviews(protocol, first, _filled(protocol, "b"))
    first = _filled(protocol, "a")
    first["annotations"][0]["counter_hypothesis"] = ""
    unsigned = {key: value for key, value in first.items() if key != "receipt_sha256"}
    first["receipt_sha256"] = hashlib.sha256(
        json.dumps(unsigned, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    with pytest.raises(ReviewError, match="Counter-hypothesis"):
        compare_reviews(protocol, first, _filled(protocol, "b"))


def test_rejects_tampered_protocol_or_atlas() -> None:
    protocol = _protocol()
    tampered = copy.deepcopy(protocol)
    tampered["regions"][0]["bbox_per_mille"] = [0, 0, 100, 100]
    with pytest.raises(ReviewError, match="invalid SHA-256"):
        blank_review(tampered, "a")
    atlas = _atlas()
    atlas["canvases"][0]["label"] = "f90v"
    with pytest.raises(ReviewError, match="integrity"):
        create_protocol(atlas, ["f78r"])


def test_rejects_wrong_protocol_binding_and_coverage() -> None:
    protocol = _protocol()
    first = _filled(protocol, "a")
    second = _filled(protocol, "b")
    other = create_protocol(_atlas(), ["f78r"], rows=1, cols=1)
    with pytest.raises(ReviewError, match="not bound"):
        compare_reviews(other, first, second)
    first = _filled(protocol, "a")
    first["annotations"].pop()
    unsigned = {key: value for key, value in first.items() if key != "receipt_sha256"}
    first["receipt_sha256"] = hashlib.sha256(
        json.dumps(unsigned, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    with pytest.raises(ReviewError, match="coverage"):
        compare_reviews(protocol, first, second)


@pytest.mark.parametrize("rows,cols", [(0, 2), (9, 1), (8, 9), (1, 0)])
def test_rejects_invalid_grid(rows: int, cols: int) -> None:
    with pytest.raises(ReviewError, match="Grid"):
        create_protocol(_atlas(), ["f78r"], rows=rows, cols=cols)


def test_rejects_nonexistent_folio() -> None:
    with pytest.raises(ReviewError, match="verifiable"):
        create_protocol(_atlas(), ["f79r"])


def test_seal_review_accepts_complete_edits_and_rejects_blank() -> None:
    protocol = _protocol()
    blank = blank_review(protocol, "a")
    with pytest.raises(ReviewError, match="independent"):
        seal_review(protocol, blank)
    complete = _filled(protocol, "a")
    complete["receipt_sha256"] = "stale"
    sealed = seal_review(protocol, complete)
    assert len(sealed["receipt_sha256"]) == 64
    assert sealed == _filled(protocol, "a")


def test_non_string_operator_fails_without_type_error() -> None:
    protocol = _protocol()
    complete = _filled(protocol, "a")
    complete["annotations"][0]["operator"] = ["BIND"]
    with pytest.raises(ReviewError, match="invalid operator"):
        seal_review(protocol, complete)
