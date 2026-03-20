from codex.lexicon import combine_patterns, load_base_patterns


def test_load_base_patterns_contains_core_tags() -> None:
    patterns = load_base_patterns()
    assert "epsilon_signature" in patterns
    assert "omega_flow" in patterns
    assert "scale_invariance" in patterns


def test_combine_patterns_appends_unique_terms() -> None:
    combined = combine_patterns({"x": ["a"]}, {"x": ["a", "b"], "y": ["c"]})
    assert combined["x"] == ["a", "b"]
    assert combined["y"] == ["c"]
