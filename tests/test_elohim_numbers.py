import pytest

from codex.elohim_numbers import contrast, lookup, match, records


def test_registry_has_unique_ids_and_provenance():
    data = records()
    assert len(data) == len({item["id"] for item in data}) == 9
    for item in data:
        assert item["edition"] and item["scope"] and item["locator"]
        assert item["url"].startswith("https://")


def test_unknown_is_not_zero_or_a_known_count():
    assert lookup("genesis-addressees")["value"] is None
    assert match(0) == []
    report = contrast("genesis-addressees", "athirat-sons")
    assert report["numeric_equal"] is None
    assert report["arithmetic_difference"] is None
    assert report["genesis_addressee_count"] is None


def test_equal_numbers_different_units_are_negative_control():
    assert len(match(7)) == 2
    report = contrast("genesis-rest", "john-long-powers")
    assert report["numeric_equal"] is True
    assert report["same_unit"] is False
    assert report["arithmetic_difference"] is None
    assert report["equivalent_referents_established"] is False


def test_recension_counts_preserve_difference():
    report = contrast("john-short-angels", "john-long-angels")
    assert report["numeric_equal"] is False
    assert report["arithmetic_difference"] == 5
    assert report["equivalent_referents_established"] is False


def test_doctrinal_count_is_not_a_god_count():
    assert lookup("trinity-persons")["basis"] == "doctrinal"
    assert lookup("trinity-persons")["unit"] == "divine-persons"


def test_detached_records_and_unknown_id():
    lookup("athirat-sons")["value"] = 0
    assert lookup("athirat-sons")["value"] == 70
    with pytest.raises(ValueError, match="Unknown numerical record"):
        lookup("missing")
