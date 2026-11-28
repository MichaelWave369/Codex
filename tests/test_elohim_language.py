from codex.elohim_language import grammar_report, lexicon, unpoint, witness_report


def test_pointed_and_unpointed_lookup():
    assert lexicon("אֱלֹהִים") == lexicon("אלהים")
    assert lexicon("צלם")[0]["id"] == "image"
    assert len(lexicon("צלם")) == 2
    assert lexicon("missing") == []


def test_lexicon_is_source_anchored():
    terms = lexicon()
    assert len(terms) == 9
    assert len({term["id"] for term in terms}) == 9
    assert all(term["source"].startswith("https://") for term in terms)


def test_grammar_does_not_count_addressees():
    report = grammar_report()
    assert report["genesis_addressee_count"] is None
    assert "them" not in report["plural_speech"]
    assert "elohim" not in report["plural_speech"]
    assert "created" in report["singular_narration"]


def test_witnesses_keep_separate_readings():
    report = witness_report()
    assert len({item["reading"] for item in report["readings"]}) == 3
    assert report["reconstructed_original"] is None
    assert report["genesis_addressee_count"] is None
    assert report["image_transcription_verified"] is False
    assert report["readings"][1]["manuscript_id"] == "4Q37 (4QDeutj)"


def test_unpoint_preserves_greek_and_hebrew_punctuation():
    assert unpoint("אֱלֹהִים־") == "אלהים־"
    assert unpoint("θεοῦ") == "θεοῦ"
