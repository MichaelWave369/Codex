import pytest

from codex.elohim_chronology import compare, interval_relation, lookup, records, timeline


def test_registry_is_scoped_and_source_linked():
    data = records()
    assert len(data) == len({item["id"] for item in data}) == 9
    for item in data:
        assert item["source"].startswith("https://")
        assert item["basis"] and item["region"]
        interval_relation((item["start"], item["end"]), (1, 1))


def test_intervals_are_inclusive_and_handle_eras():
    assert interval_relation((-2, -1), (1, 2)) == "before"
    assert interval_relation((1, 2), (-2, -1)) == "after"
    assert interval_relation((-5, -2), (-2, 2)) == "overlap"
    assert interval_relation((None, None), (1, 2)) == "unknown"


@pytest.mark.parametrize("bad", [(0, 1), (2, 1), (None, 2), (True, 2), (1.5, 2)])
def test_invalid_intervals_rejected(bad):
    with pytest.raises(ValueError):
        interval_relation(bad, (1, 2))


def test_manuscript_does_not_date_composition():
    result = compare("atrahasis-morgan", "genesis-priestly")
    assert result["interval_relation"] == "before"
    assert result["same_date_kind"] is False
    assert result["transmission_established"] is False
    assert result["idea_origin_established"] is False


def test_competing_models_and_unknown_preserved():
    result = timeline()
    assert [item["id"] for item in result["undated"]] == ["deut-4q37"]
    assert lookup("genesis2-monarchy")["work"] == lookup("genesis2-exile")["work"]
    assert compare("deut-4q37", "john-nhc2")["interval_relation"] == "unknown"
    assert compare("genesis2-monarchy", "genesis2-exile")["genesis_addressee_count"] is None


def test_detached_and_unknown_record():
    lookup("deut-4q37")["start"] = 1
    assert lookup("deut-4q37")["start"] is None
    with pytest.raises(ValueError, match="Unknown chronology record"):
        lookup("missing")
