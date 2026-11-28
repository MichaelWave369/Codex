import pytest

from codex.elohim_atlas import RECORDS, compare, record


def test_registry_is_unique_and_source_anchored():
    ids = [item["id"] for item in RECORDS]
    assert len(ids) == len(set(ids))
    for item in RECORDS:
        assert item["locator"]
        assert item["url"].startswith("https://")
        assert item["limit"]
        assert item["count_scope"]


def test_plural_does_not_imply_a_known_count():
    assert record("genesis-1")["count"] is None
    assert record("apocryphon-john")["count"] == 7
    result = compare("genesis-1", "apocryphon-john")
    assert result["genesis_addressee_count"] is None
    assert result["shared_motifs"] == ["divine-likeness"]
    assert result["right"]["relation"] == "later-interpretation"


def test_cross_tradition_comparison_preserves_divergence():
    result = compare("enki-ninmah", "atrahasis")
    assert result["shared_motifs"] == ["clay", "collaborative-formation", "labor"]
    assert result["right_only"] == ["divine-substance"]
    assert result["left_only"] == []


def test_registry_returns_detached_records():
    first = record("genesis-1")
    first["motifs"].clear()
    assert record("genesis-1")["motifs"]


def test_unknown_id_fails_explicitly():
    with pytest.raises(ValueError, match="Unknown record"):
        record("not-a-source")
