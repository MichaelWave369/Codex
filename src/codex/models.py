"""Typed models for CODEX decoding outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

ConfidenceLevel = Literal["low", "medium", "high"]


@dataclass(slots=True)
class EvidenceSpan:
    """Represents a source span where a pattern keyword appeared."""

    phrase: str
    start: int
    end: int
    context: str


@dataclass(slots=True)
class ConfidenceNote:
    """Conservative confidence description tied to explicit rule matching."""

    level: ConfidenceLevel
    rationale: str


@dataclass(slots=True)
class PatternMatch:
    """Detected pattern result with evidence and interpretive caution."""

    tag: str
    matched_terms: list[str]
    evidence: list[EvidenceSpan]
    interpretive_note: str
    confidence: ConfidenceNote


@dataclass(slots=True)
class Tradition:
    """Tradition adapter metadata and deterministic matching extensions."""

    key: str
    display_name: str
    description: str
    lexicon_extensions: dict[str, list[str]] = field(default_factory=dict)
    normalization_rules: dict[str, str] = field(default_factory=dict)
    sample_resource: str = ""


@dataclass(slots=True)
class DecodeResult:
    """Top-level decode output in both human and machine oriented forms."""

    tradition_key: str
    tradition_name: str
    source: str
    matches: list[PatternMatch]
    cautionary_note: str

    def to_dict(self) -> dict:
        """Serialize the decode result to a JSON-friendly dictionary."""
        return asdict(self)
