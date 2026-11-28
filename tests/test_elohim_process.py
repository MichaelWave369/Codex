import pytest

from codex.elohim_process import ACCOUNTS, account, compare


def test_registry_has_unique_ids_and_anchors():
    assert len(ACCOUNTS) == len({item["id"] for item in ACCOUNTS}) == 5
    for item in ACCOUNTS:
        assert item["url"].startswith("https://")
        assert item["edition"] and item["boundary"]
        for step in item["steps"]:
            assert step["actor"] and step["locator"]
            assert step["mode"] in {"narrated", "proposed"}


def test_genesis_passages_not_combined():
    result = compare("genesis-1", "genesis-2")
    assert "animation" in result["right_only"]
    assert "material" in result["right_only"]
    assert result["genesis_addressee_count"] is None


def test_proposed_formation_not_treated_as_completed():
    result = compare("enki-ninmah", "genesis-2", narrated_only=True)
    assert result["left_sequence"] == ["intention", "design"]
    assert "formation" in result["right_only"]


def test_repeated_stages_and_order_preserved():
    result = compare("genesis-1", "enki-ninmah")
    assert result["left_sequence"] == ["intention", "purpose", "formation", "purpose"]
    assert result["right_sequence"].count("purpose") == 2
    assert result["shared_order_equal"] is True


def test_distinct_animation_and_inactivity():
    result = compare("genesis-2", "apocryphon-john")
    assert result["shared_categories"] == ["animation", "formation"]
    assert result["right_only"] == ["inactivity", "intention"]
    assert result["shared_order_equal"] is True


def test_detached_and_unknown_account():
    account("genesis-1")["steps"].clear()
    assert account("genesis-1")["steps"]
    with pytest.raises(ValueError, match="Unknown creation account"):
        account("missing")
