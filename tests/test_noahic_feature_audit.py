"""NOAHIC-02 safeguards for passage-level attestations and controls."""

from copy import deepcopy

import pytest

from codex.noahic_feature_audit import (
    comparison,
    load_audit,
    render_markdown,
    validate_audit,
)


def indexed():
    return {entry["id"]: entry for entry in load_audit()["features"]}


def test_nine_features_and_all_seven_controls_remain_unreviewed():
    audit = load_audit()
    assert len(audit["features"]) == 9
    assert len(audit["controls"]) == 7
    assert all(item["status"] == "unreviewed" for item in audit["controls"])


def test_fraction_and_mastema_have_scoped_double_attestation():
    features = indexed()
    for key in ("one_tenth_spirits_remain", "mastema_named_in_partition"):
        row = features[key]["attestations"]
        assert row["jubilees_10"]["status"] == "attested"
        assert row["asaf_prologue"]["status"] == "attested"
        assert row["jubilees_10"]["locus"]
        assert row["asaf_prologue"]["locus"]


def test_mount_lubar_same_place_different_function():
    result = comparison(load_audit())
    shifts = {entry["feature_id"] for entry in result["shared_different_role"]}
    assert "mount_lubar_named" in shifts
    roles = indexed()["mount_lubar_named"]["attestations"]
    assert roles["jubilees_10"]["role"] == "burial_site"
    assert roles["asaf_prologue"]["role"] == "revelation_site"


def test_raphael_missing_only_in_scoped_jubilees_passage():
    row = indexed()["raphael_explicitly_named"]["attestations"]
    assert row["jubilees_10"]["status"] == "not_attested_in_locus"
    assert "10:10" in row["jubilees_10"]["locus"]
    assert row["asaf_prologue"]["status"] == "attested"


def test_no_claims_of_rarity_or_literary_descent():
    result = comparison(load_audit())
    assert result["rarity_evaluable"] is False
    assert result["historical_dependence_established"] is False
    assert result["control_reviews_completed"] == 0
    assert "not evaluable" in render_markdown(result)
    assert "nine" not in result["warning"].lower()  # No magical number bias


def test_no_false_negative_for_unreviewed_control():
    audit = deepcopy(load_audit())
    audit["controls"][0]["status"] = "not_attested_in_locus"
    with pytest.raises(ValueError, match="unreviewed"):
        validate_audit(audit)


def test_missing_source_locator_and_role_are_rejected():
    audit = deepcopy(load_audit())
    audit["features"][0]["attestations"]["jubilees_10"]["locus"] = ""
    with pytest.raises(ValueError, match="locus"):
        validate_audit(audit)
    audit = deepcopy(load_audit())
    audit["features"][0]["attestations"]["asaf_prologue"]["role"] = None
    with pytest.raises(ValueError, match="role"):
        validate_audit(audit)


def test_duplicate_feature_rejected():
    audit = deepcopy(load_audit())
    audit["features"][1]["id"] = audit["features"][0]["id"]
    with pytest.raises(ValueError, match="duplicate"):
        validate_audit(audit)
