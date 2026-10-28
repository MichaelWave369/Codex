"""Regression tests for source provenance and anti-overclaim gates."""

from copy import deepcopy

import pytest

from codex.noahic import _ordered_shared, compare, load_corpus, matrix, validate_corpus


def records():
    return {entry["id"]: entry for entry in load_corpus()["items"]}


def test_seed_records_include_provenance_and_controls():
    entries = load_corpus()["items"]
    assert len(entries) == 9
    assert {item["role"] for item in entries} == {"noah_medicine", "direct_noah_book", "control"}
    assert all(item["sources"] and item["caution"] for item in entries)
    assert "raphael" not in records()["jubilees_10"]["agents"]
    assert records()["aramaic_levi_10_10"]["role"] != "noah_medicine"


def test_noahic_medicine_parallel_is_not_textual_descent():
    entries = records()
    result = compare(entries["jubilees_10"], entries["asaf_prologue"])
    assert result["category"] == "noahic_medicine_parallel"
    assert len(result["ordered_shared_motifs"]) == 6
    assert result["establishes_common_source"] is False
    assert "curator-assigned" in result["method_warning"]


def test_tobit_is_an_explicit_negative_control():
    entries = records()
    result = compare(entries["jubilees_10"], entries["tobit_6"])
    assert result["category"] == "contextual_parallel_with_control"
    assert "noah" not in result["shared_agents"]
    assert "fish_remedy" not in result["shared_motifs"]


def test_raziel_tradition_remains_distinct_from_raphael():
    entries = records()
    assert "raziel" in entries["razim_prologue"]["agents"]
    assert "raphael" in entries["asaf_prologue"]["agents"]
    assert "pre_flood" in entries["razim_prologue"]["motifs"]
    assert "pre_flood" not in entries["asaf_prologue"]["motifs"]


def test_schema_rejects_duplicate_ids_and_missing_provenance():
    bad = deepcopy(load_corpus())
    bad["items"][1]["id"] = bad["items"][0]["id"]
    with pytest.raises(ValueError, match="duplicate"):
        validate_corpus(bad)
    bad = deepcopy(load_corpus())
    bad["items"][0]["sources"] = []
    with pytest.raises(ValueError, match="source"):
        validate_corpus(bad)


def test_matrix_includes_all_pairs_and_ordered_algorithm():
    entries = load_corpus()["items"]
    assert len(matrix(entries)) == 36
    assert _ordered_shared(["a", "b", "c"], ["a", "x", "b", "c"]) == ["a", "b", "c"]
