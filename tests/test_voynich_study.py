"""Synthetic preregistration tests. No historical glyph readings are invented."""

import copy
import hashlib
import json

import pytest

from codex.voynich_ivtff import bridge_atlas, index_ivtff
from codex.voynich_review import blank_review, seal_review
from codex.voynich_sources import MANIFEST_URL, atlas_from_manifest
from codex.voynich_study import StudyError, evaluate, make_plan

FOLIOS = 12


def _study_sources(count: int = FOLIOS) -> tuple[dict, dict, dict, dict]:
    lines = ["#=IVTFF Eva- 2.0 M 5", "# SYNTHETIC fixture, not historical data"]
    canvases = []
    for number in range(1, count + 1):
        folio = f"f{number}r"
        lines.append(f"<{folio}> <! $Q=A>")
        for locus in range(1, number + 1):
            lines.append(f"<{folio}.{locus},@P0> nonsense")
        canvases.append(
            {
                "id": f"https://example.org/canvas/{folio}",
                "label": {"en": [folio]},
                "items": [
                    {
                        "items": [
                            {
                                "motivation": "painting",
                                "body": {"id": f"https://example.org/image/{folio}.jpg"},
                            }
                        ]
                    }
                ],
            }
        )
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    index = index_ivtff(raw)
    atlas = atlas_from_manifest(
        json.dumps({"id": MANIFEST_URL, "items": canvases}).encode("utf-8")
    )
    bridge = bridge_atlas(index, atlas)
    lock = {
        "schema_version": "vgve-source-lock/0.1",
        "yale": {
            "manifest_sha256": atlas["manifest_sha256"],
            "iiif_canvas_count": atlas["canvas_count"],
        },
        "zl3b": {
            "source_sha256": index["source_sha256"],
            "page_section_count": index["page_count"],
            "locus_record_count": index["locus_count"],
        },
        "literal_crosswalk": {
            "exact_label_matches": count,
            "multiple_explicit_canvas_matches": 0,
            "unmapped_transcription_sections": 0,
        },
    }
    return index, atlas, bridge, lock


def _reviews(protocol: dict, *, uniform: bool = False) -> tuple[dict, dict]:
    result = []
    for reviewer in ("reviewer-a", "reviewer-b"):
        sheet = blank_review(protocol, reviewer)
        for cell in sheet["annotations"]:
            cell["operator"] = "NO_PATTERN" if uniform else (
                "FLOW" if cell["region_id"].endswith("c1") else "NO_PATTERN"
            )
            cell["evidence"] = "Made-up example grid cell, no source observation"
            cell["counter_hypothesis"] = (
                "Simple decoration" if cell["operator"] == "FLOW" else ""
            )
        sheet["blinding_asserted"] = True
        sheet["status"] = "COMPLETE"
        result.append(seal_review(protocol, sheet))
    return result[0], result[1]


def test_preregistration_is_deterministic_and_locks_all_sources() -> None:
    source = _study_sources()
    first, protocol_a = make_plan(*source, sample_size=12)
    second, protocol_b = make_plan(*source, sample_size=12)
    assert first == second
    assert protocol_a == protocol_b
    assert first["sample_size"] == 12
    assert first["holdout_size"] == 3
    assert len(protocol_a["regions"]) == 48
    assert len({row["folio_id"] for row in first["records"]}) == 12
    assert sum(row["partition"] == "HOLDOUT" for row in first["records"]) == 3


def test_source_drift_blocks_plan() -> None:
    index, atlas, bridge, lock = _study_sources()
    wrong_lock = copy.deepcopy(lock)
    wrong_lock["zl3b"]["source_sha256"] = "0" * 64
    with pytest.raises(StudyError, match="Pinned source"):
        make_plan(index, atlas, bridge, wrong_lock, sample_size=12)


def test_invalid_sample_size_blocks_plan() -> None:
    source = _study_sources()
    with pytest.raises(StudyError, match="Sample size"):
        make_plan(*source, sample_size=11)
    with pytest.raises(StudyError, match="Sample size"):
        make_plan(*source, sample_size=16 if len(source[0]["pages"]) == 16 else 52)


def test_incomplete_review_blocks_score_instead_of_inventing_results() -> None:
    plan, protocol = make_plan(*_study_sources(), sample_size=12)
    first = blank_review(protocol, "a")
    second = blank_review(protocol, "b")
    with pytest.raises(StudyError, match="Invalid independent review"):
        evaluate(plan, protocol, first, second)


def test_frozen_holdout_scoring_is_deterministic() -> None:
    plan, protocol = make_plan(*_study_sources(), sample_size=12)
    first, second = _reviews(protocol)
    result_a = evaluate(plan, protocol, first, second)
    result_b = evaluate(plan, protocol, first, second)
    assert result_a == result_b
    assert result_a["holdout_n"] == 3
    assert result_a["verdict"] in {
        "INDETERMINATE",
        "NO_PREREGISTERED_POSITIVE_SIGNAL",
        "PILOT_POSITIVE_ASSOCIATION",
    }
    assert result_a["review_agreement_receipt_sha256"]
    assert len(result_a["receipt_sha256"]) == 64


def test_all_negative_labels_produce_indeterminate_not_significant() -> None:
    plan, protocol = make_plan(*_study_sources(), sample_size=12)
    first, second = _reviews(protocol, uniform=True)
    result = evaluate(plan, protocol, first, second)
    assert result["verdict"] == "INDETERMINATE"
    assert result["spearman_rho"] is None
    assert result["permutation_p_one_sided"] is None


def test_changed_study_plan_receipt_blocks_evaluation() -> None:
    plan, protocol = make_plan(*_study_sources(), sample_size=12)
    first, second = _reviews(protocol)
    plan["records"][0]["partition"] = "DEVELOPMENT"
    with pytest.raises(StudyError, match="Invalid checksum"):
        evaluate(plan, protocol, first, second)


def test_foreign_review_protocol_blocks_evaluation() -> None:
    source = _study_sources()
    plan, protocol = make_plan(*source, sample_size=12)
    first, second = _reviews(protocol)
    different = copy.deepcopy(protocol)
    different["region_policy"] = "post-hoc chosen cells"
    unsigned = {key: value for key, value in different.items() if key != "receipt_sha256"}
    different["receipt_sha256"] = hashlib.sha256(
        json.dumps(unsigned, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    with pytest.raises(StudyError, match="Review protocol differs"):
        evaluate(plan, different, first, second)


def test_equal_source_locus_counts_are_valid_but_undefined_correlation() -> None:
    source = _study_sources()
    plan, protocol = make_plan(*source, sample_size=12)
    # A newly sealed fixed plan can still produce no statistical information.
    # All outcomes are constant, so an inference must never be fabricated.
    first, second = _reviews(protocol, uniform=True)
    verdict = evaluate(plan, protocol, first, second)
    assert verdict["verdict"] == "INDETERMINATE"
