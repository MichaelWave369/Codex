"""Deterministic symbolic decoding engine for MVP."""

from __future__ import annotations

import re

from codex.ethics import CAUTIONARY_NOTE
from codex.lexicon import combine_patterns, load_base_patterns
from codex.models import ConfidenceNote, DecodeResult, EvidenceSpan, PatternMatch
from codex.traditions import get_tradition


def _normalize_text(text: str, normalization_rules: dict[str, str]) -> str:
    normalized = text.lower()
    for source, target in normalization_rules.items():
        normalized = normalized.replace(source.lower(), target.lower())
    return normalized


def _confidence_from_count(count: int) -> ConfidenceNote:
    if count >= 3:
        return ConfidenceNote(
            level="high",
            rationale="Three or more explicit lexical matches were found for this tag.",
        )
    if count == 2:
        return ConfidenceNote(
            level="medium",
            rationale="Two explicit lexical matches were found for this tag.",
        )
    return ConfidenceNote(
        level="low",
        rationale="A single explicit lexical match was found; treat as tentative.",
    )


def _collect_evidence(text: str, term: str) -> list[EvidenceSpan]:
    evidence: list[EvidenceSpan] = []
    pattern = re.compile(re.escape(term.lower()))
    for match in pattern.finditer(text):
        start, end = match.start(), match.end()
        context_start = max(0, start - 32)
        context_end = min(len(text), end + 32)
        context = text[context_start:context_end].strip()
        evidence.append(EvidenceSpan(phrase=term, start=start, end=end, context=context))
    return evidence


def decode_text(text: str, tradition_key: str, source: str = "input") -> DecodeResult:
    """Decode text deterministically for a specific tradition key."""
    tradition = get_tradition(tradition_key)
    normalized_text = _normalize_text(text, tradition.normalization_rules)
    base_patterns = load_base_patterns()
    patterns = combine_patterns(base_patterns, tradition.lexicon_extensions)

    matches: list[PatternMatch] = []
    for tag, terms in patterns.items():
        matched_terms: list[str] = []
        evidence: list[EvidenceSpan] = []
        for term in terms:
            found = _collect_evidence(normalized_text, term.lower())
            if found:
                matched_terms.append(term)
                evidence.extend(found)

        if evidence:
            confidence = _confidence_from_count(len(matched_terms))
            matches.append(
                PatternMatch(
                    tag=tag,
                    matched_terms=matched_terms,
                    evidence=evidence,
                    interpretive_note=(
                        "Pattern is inferred from direct lexical overlap only; "
                        "semantic nuance remains open for scholarly interpretation."
                    ),
                    confidence=confidence,
                )
            )

    return DecodeResult(
        tradition_key=tradition.key,
        tradition_name=tradition.display_name,
        source=source,
        matches=matches,
        cautionary_note=CAUTIONARY_NOTE,
    )
