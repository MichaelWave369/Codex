"""Offline regression tests for Yale IIIF source-only atlas ingestion."""

import copy
import hashlib
import json

import pytest

from codex.voynich_sources import (
    MANIFEST_URL,
    AtlasError,
    atlas_from_manifest,
    blank_assignments,
)


def _painting(image_id: str) -> list[dict]:
    return [
        {
            "items": [
                {
                    "motivation": "painting",
                    "body": {"id": image_id, "type": "Image"},
                }
            ]
        }
    ]


def _v3() -> bytes:
    return json.dumps(
        {
            "id": MANIFEST_URL,
            "type": "Manifest",
            "items": [
                {
                    "id": "https://collections.library.yale.edu/canvas/78r",
                    "type": "Canvas",
                    "label": {"en": ["f78r"]},
                    "items": _painting(
                        "https://collections.library.yale.edu/iiif/2/img78/full/full/0/default.jpg"
                    ),
                },
                {
                    "id": "https://collections.library.yale.edu/canvas/foldout",
                    "type": "Canvas",
                    "label": {"none": ["foldout f85v–f86r"]},
                    "items": _painting(
                        "https://collections.library.yale.edu/iiif/2/fold/full/full/0/default.jpg"
                    ),
                },
                {
                    "id": "https://collections.library.yale.edu/canvas/page3",
                    "type": "Canvas",
                    "label": {"none": ["Page 3"]},
                    "items": _painting(
                        "https://collections.library.yale.edu/iiif/2/3/full/full/0/default.jpg"
                    ),
                },
            ],
        }
    ).encode("utf-8")


def _v2() -> bytes:
    return json.dumps(
        {
            "@id": MANIFEST_URL,
            "@type": "sc:Manifest",
            "sequences": [
                {
                    "canvases": [
                        {
                            "@id": "https://collections.library.yale.edu/canvas/1",
                            "label": "folio 78r",
                            "images": [
                                {
                                    "resource": {
                                        "@id": "https://collections.library.yale.edu/iiif/2/a/full/full/0/default.jpg"
                                    }
                                }
                            ],
                        },
                        {
                            "@id": "https://collections.library.yale.edu/canvas/2",
                            "label": "f84v",
                            "images": [],
                        },
                    ]
                }
            ],
        }
    ).encode("utf-8")


def test_v3_canvas_index_and_unambiguous_folio() -> None:
    atlas = atlas_from_manifest(_v3())
    assert atlas["iiif_presentation_version"] == 3
    assert atlas["canvas_count"] == 3
    assert atlas["canvases"][0]["folio_key"] == "f78r"
    assert atlas["canvases"][0]["label_status"] == "unambiguous"
    assert atlas["canvases"][0]["image_url"].endswith("default.jpg")


def test_ambiguous_and_unresolved_labels_are_not_guessed() -> None:
    atlas = atlas_from_manifest(_v3())
    assert atlas["canvases"][1]["folio_key"] is None
    assert atlas["canvases"][1]["label_status"] == "ambiguous"
    assert atlas["canvases"][2]["label_status"] == "unresolved"
    with pytest.raises(AtlasError, match="verifiable"):
        blank_assignments(atlas, ["f85v"])


def test_v2_canvas_parser_preserves_missing_images() -> None:
    atlas = atlas_from_manifest(_v2())
    assert atlas["iiif_presentation_version"] == 2
    assert atlas["canvases"][0]["folio_key"] == "f78r"
    assert atlas["canvases"][1]["image_url"] is None
    with pytest.raises(AtlasError, match="no image"):
        blank_assignments(atlas, ["f84v"])


def test_blank_assignments_do_not_imply_ancient_meanings() -> None:
    atlas = atlas_from_manifest(_v3())
    review = blank_assignments(atlas, ["78r"])
    assert review["assignments"][0]["status"] == "UNANNOTATED"
    assert review["assignments"][0]["operator_sequence"] == []
    assert review["assignments"][0]["observations"] == []
    assert "target Source-to-embodiment" in review["blinding"]


def test_atlas_receipt_is_reproducible_and_source_hash_is_raw_bytes() -> None:
    raw = _v3()
    atlas = atlas_from_manifest(raw)
    assert atlas == atlas_from_manifest(raw)
    assert atlas["manifest_sha256"] == hashlib.sha256(raw).hexdigest()
    receipt = atlas.pop("receipt_sha256")
    canonical = json.dumps(atlas, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    assert receipt == hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_rejects_wrong_manuscript_and_empty_manifest() -> None:
    wrong = json.loads(_v3())
    wrong["id"] = "https://collections.library.yale.edu/manifests/123"
    with pytest.raises(AtlasError, match="MS 408"):
        atlas_from_manifest(json.dumps(wrong).encode("utf-8"))
    empty = {"id": MANIFEST_URL, "items": []}
    with pytest.raises(AtlasError, match="no canvases"):
        atlas_from_manifest(json.dumps(empty).encode("utf-8"))


def test_rejects_duplicate_canvas_ids() -> None:
    obj = json.loads(_v3())
    obj["items"][1]["id"] = obj["items"][0]["id"]
    with pytest.raises(AtlasError, match="Duplicate IIIF"):
        atlas_from_manifest(json.dumps(obj).encode("utf-8"))


def test_rejects_unresolved_or_unlisted_folios() -> None:
    atlas = atlas_from_manifest(_v3())
    with pytest.raises(AtlasError, match="verifiable"):
        blank_assignments(atlas, ["f79v"])
    with pytest.raises(AtlasError, match="Specify"):
        blank_assignments(atlas, [])


def test_assignments_are_repeatable_and_independent() -> None:
    atlas = atlas_from_manifest(_v3())
    a = blank_assignments(atlas, ["f78r"])
    b = blank_assignments(atlas, ["78r"])
    assert a == b
    assert not a["assignments"][0]["observer_id"]
    assert a["receipt_sha256"] == b["receipt_sha256"]


def test_source_fields_do_not_accept_malformed_input() -> None:
    with pytest.raises(AtlasError, match="JSON"):
        atlas_from_manifest(b"not json")
    corrupted = copy.deepcopy(json.loads(_v3()))
    corrupted["items"][0]["id"] = "not-a-canvas"
    with pytest.raises(AtlasError, match="HTTPS"):
        atlas_from_manifest(json.dumps(corrupted).encode("utf-8"))


def test_tampered_atlas_is_rejected_before_review() -> None:
    atlas = atlas_from_manifest(_v3())
    atlas["canvases"][0]["image_url"] = "https://example.com/unverified.jpg"
    with pytest.raises(AtlasError, match="integrity"):
        blank_assignments(atlas, ["f78r"])


def test_duplicate_aliases_are_rejected() -> None:
    atlas = atlas_from_manifest(_v3())
    with pytest.raises(AtlasError, match="Duplicate requested folio"):
        blank_assignments(atlas, ["f78r", "78r"])
