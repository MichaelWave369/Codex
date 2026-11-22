"""Synthetic IVTFF tests: no real Voynich transliteration is embedded here."""

import copy
import hashlib
import json

import pytest

from codex.voynich_ivtff import (
    TranscriptionError,
    bridge_atlas,
    index_ivtff,
)
from codex.voynich_sources import MANIFEST_URL, atlas_from_manifest

RAW = b"""#=IVTFF Eva- 2.0 M 5
# Synthetic test lines, NOT ZL transcription
<f1r>  <! $Q=A $P=A>
<f1r.1,@P0>  foo.bar?baz
<f1r.2,+P0>  [a:o].qux
<f1v>  <! $Q=A $P=B>
<f1v.1,@L0>  foo.bar
<f85v1> <! $Q=A>
<f85v1.1,@P0> foo
"""


def _atlas() -> dict:
    manifest = {
        "id": MANIFEST_URL,
        "type": "Manifest",
        "items": [
            {
                "id": "https://example.org/canvas/f1r",
                "label": {"en": ["f1r"]},
                "items": [
                    {
                        "items": [
                            {
                                "motivation": "painting",
                                "body": {"id": "https://example.org/image1.jpg"},
                            }
                        ]
                    }
                ],
            },
            {
                "id": "https://example.org/canvas/f1r-partial",
                "label": {"en": ["f1r partial"]},
                "items": [],
            },
            {
                "id": "https://example.org/canvas/f1v",
                "label": {"en": ["f1v"]},
                "items": [],
            },
        ],
    }
    return atlas_from_manifest(json.dumps(manifest).encode("utf-8"))


def test_parses_edition_and_preserves_locus_ids_without_translations() -> None:
    result = index_ivtff(RAW)
    assert result["format"] == "IVTFF 2.0"
    assert result["alphabet"] == "Eva-"
    assert result["source_sha256"] == hashlib.sha256(RAW).hexdigest()
    assert result["page_count"] == 3
    assert result["locus_count"] == 4
    assert result["pages"][0]["loci"][0]["locus_id"] == "f1r.1"
    assert result["pages"][0]["loci"][0]["question_mark_count"] == 1
    assert result["pages"][0]["loci"][1]["square_bracket_count"] == 1
    assert "foo.bar" not in json.dumps(result)


def test_raw_bytes_produce_deterministic_receipts() -> None:
    assert index_ivtff(RAW) == index_ivtff(RAW)
    assert len(index_ivtff(RAW)["receipt_sha256"]) == 64


def test_accepted_expected_hash_and_rejected_mismatch() -> None:
    digest = hashlib.sha256(RAW).hexdigest()
    assert index_ivtff(RAW, expected_sha256=digest)["source_sha256"] == digest
    with pytest.raises(TranscriptionError, match="does not match"):
        index_ivtff(RAW, expected_sha256="0" * 64)


def test_rejects_invalid_format_and_empty_source() -> None:
    with pytest.raises(TranscriptionError, match="Empty"):
        index_ivtff(b"")
    with pytest.raises(TranscriptionError, match="Expected IVTFF Eva-"):
        index_ivtff(RAW.replace(b"Eva-", b"Unknown"))


def test_rejects_duplicate_locus_ids_and_orphans() -> None:
    duplicate = RAW.replace(b"<f1r.2,+P0>  [a:o].qux", b"<f1r.1,+P0>  [a:o].qux")
    with pytest.raises(TranscriptionError, match="Duplicate locus"):
        index_ivtff(duplicate)
    orphan = b"#=IVTFF Eva- 2.0 M 5\n<f1r.1,@P0> words\n"
    with pytest.raises(TranscriptionError, match="before page"):
        index_ivtff(orphan)


def test_rejects_wrong_page_and_unrecognized_records() -> None:
    mismatch = RAW.replace(b"<f1v.1,@L0>", b"<f2r.1,@L0>")
    with pytest.raises(TranscriptionError, match="another folio"):
        index_ivtff(mismatch)
    invalid = RAW + b"this line is not a locus\n"
    with pytest.raises(TranscriptionError, match="Unrecognized"):
        index_ivtff(invalid)


def test_bridges_literal_labels_and_marks_partial_ambiguity() -> None:
    joined = bridge_atlas(index_ivtff(RAW), _atlas())
    assert joined["mapping_counts"] == {
        "EXACT_LABEL_MATCH": 1,
        "MULTIPLE_EXPLICIT_CANVASES": 1,
        "UNMAPPED": 1,
    }
    rows = {entry["folio_id"]: entry for entry in joined["mappings"]}
    assert rows["f1r"]["status"] == "MULTIPLE_EXPLICIT_CANVASES"
    assert rows["f1v"]["status"] == "EXACT_LABEL_MATCH"
    assert rows["f85v1"]["status"] == "UNMAPPED"


def test_rejects_tampered_index_and_atlas_receipts() -> None:
    index = index_ivtff(RAW)
    edited = copy.deepcopy(index)
    edited["pages"][0]["loci"][0]["locus_id"] = "changed"
    with pytest.raises(TranscriptionError, match="checksum"):
        bridge_atlas(edited, _atlas())
    atlas = _atlas()
    atlas["canvases"][0]["folio_key"] = "f300r"
    with pytest.raises(TranscriptionError, match="checksum"):
        bridge_atlas(index, atlas)
