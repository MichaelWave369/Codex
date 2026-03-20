"""Tradition adapter for Gospel of Thomas snippets."""

from codex.models import Tradition

TRADITION = Tradition(
    key="thomas",
    display_name="Gospel of Thomas (sample excerpts)",
    description=(
        "A compact adapter with sayings-oriented metaphors emphasizing interiority, "
        "self-knowing, and inner light motifs."
    ),
    lexicon_extensions={
        "epsilon_signature": ["living light", "single one"],
        "interiority": ["know yourself", "inside"],
        "unity_correspondence": ["make the two one"],
    },
    normalization_rules={"thyself": "yourself", "ye": "you"},
    sample_resource="gospel_of_thomas_sample.txt",
)
