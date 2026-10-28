"""NOAHIC-03 tests prevent fabricated manuscript and translation equivalence."""

from copy import deepcopy

import pytest

from codex.noahic_witness import (
    TRANSCRIPTION_SCHEMA,
    _unicode_tokens,
    compare_local_excerpts,
    load_registry,
    validate_registry,
    witness_plan,
)


def sample(witness_id, text):
    """Synthetic Unicode test tokens, never manuscript transcriptions."""
    registry = load_registry()
    witness = next(item for item in registry["witnesses"] if item["id"] == witness_id)
    return {
        "schema": TRANSCRIPTION_SCHEMA,
        "witness_id": witness_id,
        "locus": witness["locus"],
        "source_url": witness["source_url"],
        "editor": "SYNTHETIC TEST FIXTURE",
        "transcription_note": "Artificial tokens. Not historical manuscript text.",
        "text": text,
    }


def test_registry_exposes_original_language_gap():
    registry = load_registry()
    report = witness_plan(registry)
    assert len(registry["witnesses"]) == 4
    assert report["direct_original_language_pair_available"] is False
    gap = next(x for x in registry["witnesses"] if x["id"] == "jubilees_10_qumran_hebrew_gap")
    assert gap["coverage"] == "not_attested_in_identified_extant_fragments"
    assert gap["ingestion"] == "unavailable"


def test_geez_to_hebrew_is_blocked_not_auto_translated():
    registry = load_registry()
    a = sample("jubilees_10_geez_eotc", "ሀለመ ሰረቀ")
    b = sample("asaf_prologue_hebrew_muntner", "אבג דהו")
    report = compare_local_excerpts(a, b, registry)
    assert report["status"] == "blocked"
    assert not report["identical_bigrams"]
    assert any("Different source languages" in reason for reason in report["reasons"])
    assert report["original_language_dependence_proven"] is False


def test_modern_hebrew_translation_is_not_original_language_evidence():
    registry = load_registry()
    a = sample("jubilees_10_modern_hebrew_translation", "אבג דהו")
    b = sample("asaf_prologue_hebrew_muntner", "אבג דהו")
    report = compare_local_excerpts(a, b, registry)
    assert report["status"] == "blocked"
    assert report["identical_bigrams"] == []
    assert any("translation" in reason.lower() for reason in report["reasons"])


def test_missing_hebrew_locus_cannot_be_transcribed():
    registry = load_registry()
    a = sample("jubilees_10_qumran_hebrew_gap", "אבג דהו")
    b = sample("asaf_prologue_hebrew_muntner", "אבג דהו")
    with pytest.raises(ValueError, match="missing source-locus"):
        compare_local_excerpts(a, b, registry)


def test_rejects_wrong_script_and_unregistered_source_url():
    registry = load_registry()
    a = sample("asaf_prologue_hebrew_muntner", "latin words")
    with pytest.raises(ValueError, match="script"):
        compare_local_excerpts(a, a, registry)
    a = sample("asaf_prologue_hebrew_muntner", "אבג דהו")
    a["source_url"] = "https://wrong.example"
    with pytest.raises(ValueError, match="Source URL"):
        compare_local_excerpts(a, a, registry)


def test_unicode_nfc_and_combining_marks_preserved():
    assert _unicode_tokens("אָב שֵׁם") == ["אָב", "שֵׁם"]
    assert _unicode_tokens("ሀለ፡ ሐመ።") == ["ሀለ", "ሐመ"]


def test_duplicate_or_false_covered_witness_is_invalid():
    registry = deepcopy(load_registry())
    registry["witnesses"][1]["id"] = registry["witnesses"][0]["id"]
    with pytest.raises(ValueError, match="duplicate"):
        validate_registry(registry)
    registry = deepcopy(load_registry())
    registry["witnesses"][2]["ingestion"] = "not_ingested"
    with pytest.raises(ValueError, match="Unattested locus"):
        validate_registry(registry)
