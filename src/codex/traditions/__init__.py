"""Tradition registry and sample loaders."""

from __future__ import annotations

from importlib import resources

from codex.models import Tradition
from codex.traditions.gospel_of_thomas import TRADITION as THOMAS
from codex.traditions.hermetic import TRADITION as HERMETIC

REGISTRY: dict[str, Tradition] = {
    THOMAS.key: THOMAS,
    HERMETIC.key: HERMETIC,
}


def get_tradition(key: str) -> Tradition:
    """Return a registered tradition by key."""
    try:
        return REGISTRY[key]
    except KeyError as exc:
        options = ", ".join(sorted(REGISTRY))
        raise ValueError(f"Unknown tradition '{key}'. Available: {options}") from exc


def list_traditions() -> list[Tradition]:
    """Return all registered traditions in sorted key order."""
    return [REGISTRY[k] for k in sorted(REGISTRY)]


def load_sample_text(tradition: Tradition) -> str:
    """Load bundled sample text for a tradition."""
    return (
        resources.files("codex.data.samples")
        .joinpath(tradition.sample_resource)
        .read_text(encoding="utf-8")
    )
