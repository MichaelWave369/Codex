"""Utilities for loading and combining deterministic pattern lexicons."""

from __future__ import annotations

import json
from importlib import resources

PATTERN_TAG_MAP = {
    "epsilon_states": "epsilon_signature",
    "omega_dynamics": "omega_flow",
    "scale_invariance": "scale_invariance",
}

DERIVED_PATTERN_TERMS = {
    "transformation": ["transform", "rebirth", "renew", "metamorphosis", "transmute"],
    "interiority": ["within", "inner", "heart", "silence", "inward"],
    "unity_correspondence": ["one", "unity", "correspond", "likeness", "reflection"],
}


def load_base_patterns() -> dict[str, list[str]]:
    """Load base lexicon entries from packaged JSON files."""
    patterns: dict[str, list[str]] = {}
    package = "codex.data.patterns"
    for file_name, tag in PATTERN_TAG_MAP.items():
        text = resources.files(package).joinpath(f"{file_name}.json").read_text(encoding="utf-8")
        payload = json.loads(text)
        patterns[tag] = payload["terms"]

    for tag, terms in DERIVED_PATTERN_TERMS.items():
        patterns[tag] = terms
    return patterns


def combine_patterns(
    base: dict[str, list[str]],
    extension: dict[str, list[str]] | None = None,
) -> dict[str, list[str]]:
    """Combine base patterns with optional tradition-specific extensions."""
    combined: dict[str, list[str]] = {tag: terms[:] for tag, terms in base.items()}
    if not extension:
        return combined

    for tag, extra_terms in extension.items():
        if tag not in combined:
            combined[tag] = []
        for term in extra_terms:
            if term not in combined[tag]:
                combined[tag].append(term)
    return combined
