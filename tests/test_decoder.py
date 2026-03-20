from codex.decoder import decode_text


def test_decode_flow_finds_expected_thomas_pattern() -> None:
    text = "The kingdom within reveals inner light and calls for self-knowing."
    result = decode_text(text, tradition_key="thomas", source="unit")
    tags = {m.tag for m in result.matches}
    assert "epsilon_signature" in tags
    epsilon = next(m for m in result.matches if m.tag == "epsilon_signature")
    assert "kingdom within" in epsilon.matched_terms


def test_decode_flow_finds_hermetic_scale_invariance() -> None:
    text = "As above, so below: the microcosm mirrors macrocosm."
    result = decode_text(text, tradition_key="hermetic", source="unit")
    tags = {m.tag for m in result.matches}
    assert "scale_invariance" in tags
