import pytest

from codex.traditions import get_tradition, list_traditions


def test_tradition_registry_lists_expected() -> None:
    keys = [trad.key for trad in list_traditions()]
    assert keys == ["hermetic", "thomas"]


def test_unknown_tradition_raises() -> None:
    with pytest.raises(ValueError):
        get_tradition("unknown")
