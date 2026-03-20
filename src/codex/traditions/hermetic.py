"""Tradition adapter for Hermetic-style symbolic language."""

from codex.models import Tradition

TRADITION = Tradition(
    key="hermetic",
    display_name="Hermetic Corpus (sample excerpts)",
    description=(
        "A compact adapter focused on correspondence language, macrocosm/microcosm framing, "
        "and transformational imagery."
    ),
    lexicon_extensions={
        "scale_invariance": ["as above, so below", "as within, so without"],
        "transformation": ["alchemical", "transmutation", "refinement"],
        "omega_flow": ["pneuma"],
    },
    normalization_rules={"macro-cosm": "macrocosm", "micro-cosm": "microcosm"},
    sample_resource="hermetic_sample.txt",
)
