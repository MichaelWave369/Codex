"""Regression checks for VGVE guarded comparisons."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from codex.voynich_engine import PacketError, compare

DEMO = Path(__file__).resolve().parents[1] / "examples" / "voynich_symbolic_demo.json"


def sample_packet() -> dict:
    return json.loads(DEMO.read_text(encoding="utf-8"))


def test_same_packet_has_identical_hash_and_scores() -> None:
    first = compare(sample_packet())
    second = compare(sample_packet())
    assert first == second
    assert len(first["comparisons"]) == 3
    assert len(first["receipt_sha256"]) == 64
    unsigned = {key: value for key, value in first.items() if key != "receipt_sha256"}
    canonical = json.dumps(unsigned, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == first["receipt_sha256"]


def test_similar_synthetic_sequences_score_higher_than_negative_control() -> None:
    result = compare(sample_packet())
    scores = {
        frozenset((pair["left_id"], pair["right_id"])): pair["transition_jaccard"]
        for pair in result["comparisons"]
    }
    assert scores[frozenset(("illustration-demo", "parable-demo"))] == 1.0
    assert scores[frozenset(("illustration-demo", "negative-control"))] == 0.0


def test_changing_annotation_changes_receipt() -> None:
    packet = sample_packet()
    baseline = compare(packet)["receipt_sha256"]
    changed = copy.deepcopy(packet)
    changed["records"][0]["anchors"][1]["operator"] = "FLOW"
    assert compare(changed)["receipt_sha256"] != baseline


def test_rejects_missing_counter_hypothesis() -> None:
    packet = sample_packet()
    packet["records"][0].pop("counter_hypothesis")
    with pytest.raises(PacketError, match="counter_hypothesis"):
        compare(packet)


def test_rejects_text_evidence_not_in_source() -> None:
    packet = sample_packet()
    packet["records"][1]["anchors"][0]["evidence"] = "The manuscript says this."
    with pytest.raises(PacketError, match="exact source.text substring"):
        compare(packet)


def test_rejects_decipherment_claim() -> None:
    packet = sample_packet()
    packet["claimed_decipherment"] = True
    with pytest.raises(PacketError, match="claimed_decipherment"):
        compare(packet)


def test_rejects_missing_historical_url() -> None:
    packet = sample_packet()
    packet["records"][0]["source"]["kind"] = "historical"
    with pytest.raises(PacketError, match="source.url"):
        compare(packet)


def test_requires_distinct_traditions() -> None:
    packet = sample_packet()
    for record in packet["records"]:
        record["tradition"] = "same"
    with pytest.raises(PacketError, match="distinct traditions"):
        compare(packet)
