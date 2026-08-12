from codex.mothership import MOTHERSHIP_READER_SCHEMA, run_codex_reader


def test_mothership_codex_adapter_is_deterministic():
    text = "The kingdom is within you; know yourself and become one."
    a = run_codex_reader(text, "thomas", source="test")
    b = run_codex_reader(text, "thomas", source="test")

    assert a.schema == MOTHERSHIP_READER_SCHEMA
    assert a.reader["id"] == "codex.symbolic_corpus"
    assert a.receipt_hash == b.receipt_hash
    assert a.receipt_hash.startswith("RDR-")


def test_mothership_codex_adapter_preserves_claim_boundary():
    envelope = run_codex_reader(
        "The kingdom is within you; know yourself and become one.",
        "thomas",
        source="test",
    )

    assert "does not prove" in envelope.claim_boundary.lower()
    assert all(obs.claim_class == "source_observation" for obs in envelope.observations)
    assert all(
        interpretation.claim_class == "symbolic_interpretation"
        for interpretation in envelope.interpretations
    )


def test_mothership_codex_observations_keep_evidence_spans():
    envelope = run_codex_reader(
        "The kingdom is within you; know yourself and become one.",
        "thomas",
        source="test",
    )

    for observation in envelope.observations:
        value = observation.value
        assert "evidence" in value
        for span in value["evidence"]:
            assert {"phrase", "start", "end", "context"} <= set(span)
