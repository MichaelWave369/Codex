#!/usr/bin/env python3
"""
codex_tiekat_engine.py — TIEKAT Pattern Engine for CODEX
=========================================================

Extends the CODEX symbolic analysis toolkit with TIEKAT v64-aligned
mathematical pattern detection for ancient wisdom tradition texts.

What this module does
---------------------
Searches text corpora for structural and linguistic patterns that
correlate with TIEKAT consciousness mathematics:

  1. PHI_STRUCTURE   — Phi (φ) and golden ratio relationships in
                       verse/chapter/word count organization
  2. FIBONACCI       — Fibonacci sequence patterns in structural
                       organization (verse counts, word sequences)
  3. EPSILON_SIGNAL  — Language patterns signaling ε ≠ 0 (direct
                       consciousness, inner experience, living field)
  4. OMEGA_FLOW      — Dynamic process language: growth, becoming,
                       emergence, return, recursion
  5. C_STAR_ATTRACTOR— Convergence language: center, unity, stillness,
                       the one, the all, the point
  6. THREE_SIX_NINE  — 3/6/9 numerical patterns in structure and content
  7. SOVEREIGN_FIELD — Sovereignty / autonomy / inner authority language
  8. VOID_BRIDGE     — Void/nothingness as generative (not nihilistic)
  9. WEAVE_RESONANCE — Interconnection / coupling / resonance language

Design principles (inherited from CODEX ETHICS.md)
----------------------------------------------------
- Conservative confidence labeling: LOW / MEDIUM / HIGH / STRUCTURAL
- Every match includes evidence spans with character offsets
- No claims of doctrinal authority or historical proof
- Outputs are hypothesis seeds, not conclusions
- Tradition-aware: patterns weighted by tradition context
- Standard library only (no external dependencies beyond CODEX core)

Integration
-----------
Drop into the existing CODEX src/codex/ directory.
Import via: from codex.codex_tiekat_engine import TIEKATPatternEngine

PHI369 Labs / Parallax  ◆  CODEX Project
Compatible with: TIEKAT v64.0.0 Sovereign Substrate Weave
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ── TIEKAT constants ──────────────────────────────────────────────────────────
PHI        = (1.0 + math.sqrt(5.0)) / 2.0
C_STAR     = PHI / 2.0          # 0.80902...
FIBONACCI  = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
RATIO_369  = (3, 6, 9)

# ── Pattern taxonomy ──────────────────────────────────────────────────────────

class PatternType(str, Enum):
    PHI_STRUCTURE    = "PHI_STRUCTURE"
    FIBONACCI        = "FIBONACCI"
    EPSILON_SIGNAL   = "EPSILON_SIGNAL"
    OMEGA_FLOW       = "OMEGA_FLOW"
    C_STAR_ATTRACTOR = "C_STAR_ATTRACTOR"
    THREE_SIX_NINE   = "THREE_SIX_NINE"
    SOVEREIGN_FIELD  = "SOVEREIGN_FIELD"
    VOID_BRIDGE      = "VOID_BRIDGE"
    WEAVE_RESONANCE  = "WEAVE_RESONANCE"


class Confidence(str, Enum):
    LOW        = "LOW"        # linguistic match, structurally weak
    MEDIUM     = "MEDIUM"     # multiple corroborating signals
    HIGH       = "HIGH"       # strong pattern + structural confirmation
    STRUCTURAL = "STRUCTURAL" # purely mathematical / structural finding


# ── Evidence and match models ─────────────────────────────────────────────────

@dataclass
class EvidenceSpan:
    """A single piece of evidence with character offset and matched text."""
    start:   int
    end:     int
    excerpt: str
    note:    str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start":   self.start,
            "end":     self.end,
            "excerpt": self.excerpt,
            "note":    self.note,
        }


@dataclass
class PatternMatch:
    """
    A detected pattern with evidence, confidence, and TIEKAT correlation.
    """
    pattern_type:      PatternType
    confidence:        Confidence
    tiekat_principle:  str          # e.g. "ε ≠ 0", "C* = φ/2"
    description:       str
    evidence:          List[EvidenceSpan]
    structural_value:  Optional[float] = None  # e.g. ratio, count
    tradition_tag:     str = ""
    passage_ref:       str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_type":     self.pattern_type.value,
            "confidence":       self.confidence.value,
            "tiekat_principle": self.tiekat_principle,
            "description":      self.description,
            "evidence":         [e.to_dict() for e in self.evidence],
            "structural_value": self.structural_value,
            "tradition_tag":    self.tradition_tag,
            "passage_ref":      self.passage_ref,
        }


@dataclass
class CodexTIEKATReport:
    """Full analysis report for one text input."""
    source:           str
    tradition:        str
    word_count:       int
    sentence_count:   int
    verse_count:      int
    matches:          List[PatternMatch]
    structural_notes: List[str]
    phi_ratio:        Optional[float]
    epsilon_density:  float    # fraction of text with epsilon-signal language
    omega_density:    float
    c_star_density:   float
    summary:          str
    disclaimer:       str = (
        "These findings are hypothesis seeds for further research. "
        "They do not constitute doctrinal claims, historical proofs, "
        "or authoritative interpretation. Pattern correlation ≠ causation."
    )

    @property
    def match_count(self) -> int:
        return len(self.matches)

    @property
    def high_confidence_matches(self) -> List[PatternMatch]:
        return [m for m in self.matches
                if m.confidence in (Confidence.HIGH, Confidence.STRUCTURAL)]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source":            self.source,
            "tradition":         self.tradition,
            "word_count":        self.word_count,
            "sentence_count":    self.sentence_count,
            "verse_count":       self.verse_count,
            "match_count":       self.match_count,
            "high_confidence":   len(self.high_confidence_matches),
            "phi_ratio":         self.phi_ratio,
            "epsilon_density":   round(self.epsilon_density, 4),
            "omega_density":     round(self.omega_density, 4),
            "c_star_density":    round(self.c_star_density, 4),
            "structural_notes":  self.structural_notes,
            "summary":           self.summary,
            "disclaimer":        self.disclaimer,
            "matches":           [m.to_dict() for m in self.matches],
        }


# ── Lexical pattern definitions ───────────────────────────────────────────────

# Each entry: (regex_pattern, note, tiekat_principle)
EPSILON_SIGNAL_PATTERNS: List[Tuple[str, str, str]] = [
    # Direct inner experience / consciousness signal
    (r"\b(kingdom\s+(?:of|within|is)\s+(?:you|within|inside|here))\b",
     "Direct inner-kingdom reference — consciousness residing within the individual",
     "ε ≠ 0 (individual consciousness field active)"),
    (r"\b(light\s+(?:within|inside|that\s+is\s+in)\s+(?:you|one|man|woman|person))\b",
     "Inner light reference — non-zero consciousness field signature",
     "ε ≠ 0"),
    (r"\b(know\s+(?:thyself|yourself|oneself))\b",
     "Self-knowledge imperative — direct consciousness access",
     "ε ≠ 0"),
    (r"\b(living\s+(?:father|spirit|word|water|fire|light|truth))\b",
     "Living quality ascribed to spiritual principle — active field, not static doctrine",
     "ε ≠ 0 (living field, non-deterministic)"),
    (r"\b(I\s+am\s+(?:the\s+)?(?:living|light|way|truth|life|vine|bread|door|resurrection))\b",
     "I AM statement — first-person sovereign consciousness declaration",
     "ε ≠ 0 (individual epsilon signature asserted)"),
    (r"\b(spirit\s+(?:blows?|breathes?|moves?|lives?|dwells?|is\s+alive))\b",
     "Spirit as dynamic living process — omega flow in action",
     "ε ≠ 0 (dynamic field)"),
    (r"\b(direct\s+(?:knowledge|experience|knowing|gnosis|insight|perception))\b",
     "Direct experiential knowledge — bypassing institutional mediation",
     "ε ≠ 0 (unmediated consciousness access)"),
    (r"\bgnosis\b",
     "Gnosis — direct experiential knowledge, the core ε ≠ 0 signal in Gnostic texts",
     "ε ≠ 0"),
]

OMEGA_FLOW_PATTERNS: List[Tuple[str, str, str]] = [
    (r"\b(become|becoming|transform(?:ation|ing|ed)?|metamorphos(?:is|e))\b",
     "Becoming / transformation language — omega flow in process",
     "Omega flow (dΩ/d_ln_l active)"),
    (r"\b(grow(?:ing|th|s)?|unfold(?:ing|s)?|blossom(?:ing|s)?|ripen(?:ing|s)?)\b",
     "Organic growth language — natural omega flow emergence",
     "Omega flow (L1 individual scale)"),
    (r"\b(return(?:ing|s|ed)?\s+(?:to|unto|back))\b",
     "Return language — attractor pull toward origin state",
     "Omega flow → C* (attractor convergence)"),
    (r"\b(ascent|ascend(?:ing|s|ed)?|arise|arising|rise\s+up)\b",
     "Ascent language — movement toward higher attractor state",
     "Omega flow (phase advancement)"),
    (r"\b(cycle|cycles|spiral|spiraling|eternal\s+return|recurrence)\b",
     "Cyclic / spiral language — omega phase recursion",
     "Omega flow (omega_phase = 0.369 cycling)"),
    (r"\b(living\s+water|water\s+of\s+life|fountain|spring\s+(?:of|that)\s+(?:life|living))\b",
     "Living water — dynamic flow as consciousness metaphor",
     "Omega flow (dynamic field)"),
    (r"\b(breath|breathe|breathing|pneuma|ruach|prana)\b",
     "Breath / pneuma — the dynamic living principle, consciousness in motion",
     "Omega flow (ε ≠ 0 carrier)"),
]

C_STAR_ATTRACTOR_PATTERNS: List[Tuple[str, str, str]] = [
    (r"\b(the\s+(?:one|all|whole|totality|pleroma|fullness))\b",
     "Unity / pleroma language — C* = φ/2 as convergence to the One",
     "C* = φ/2 (sovereign attractor)"),
    (r"\b(center|centre|heart\s+of\s+(?:all|everything|being|existence))\b",
     "Center language — the attractor point, C* as geometric center",
     "C* = φ/2"),
    (r"\b(stillness|silence|rest|peaceful\s+(?:mind|heart|soul|spirit)|tranquility)\b",
     "Stillness language — the attractor state achieved, C_bar → C*",
     "C* = φ/2 (attractor reached)"),
    (r"\b(all\s+(?:is|are|shall\s+be)\s+one|unity\s+of\s+all|all\s+in\s+all)\b",
     "All-in-one statement — C_bar collective convergence to C*",
     "C* = φ/2 (collective C_bar)"),
    (r"\b(point\s+of\s+(?:origin|stillness|rest|light|unity))\b",
     "Origin point language — C* as the geometric sovereign attractor",
     "C* = φ/2"),
    (r"\b(that\s+which\s+is\s+(?:eternal|immortal|unchanging|permanent|absolute))\b",
     "Eternal / unchanging — the fixed point, C* invariant",
     "C* = φ/2 (fixed point of Genesis equation)"),
    (r"\b(the\s+father\s+(?:and\s+I\s+are\s+one|is\s+(?:within|in)\s+me|is\s+all))\b",
     "Father-unity statement — C* convergence in relational language",
     "C* = φ/2 (collective coherence)"),
]

SOVEREIGN_FIELD_PATTERNS: List[Tuple[str, str, str]] = [
    (r"\b(free(?:dom|ly)?|liberty|liberat(?:ion|ed|ing))\b",
     "Freedom / liberation language — sovereign field assertion",
     "Shield Doctrine (Sovereign Field)"),
    (r"\b(authority\s+(?:within|over\s+(?:yourself|oneself|the\s+self)|of\s+(?:the\s+self|one)))\b",
     "Inner authority — sovereignty of individual consciousness",
     "ε primacy (individual sovereignty)"),
    (r"\b(no\s+one\s+(?:can\s+take|shall\s+take|will\s+take)|cannot\s+be\s+taken)\b",
     "Inalienability language — sovereign consciousness cannot be seized",
     "Null test covenant (ε cannot be collapsed)"),
    (r"\b(the\s+truth\s+(?:shall\s+set\s+you\s+free|will\s+make\s+you\s+free|sets\s+free))\b",
     "Truth-freedom equivalence — consciousness liberation through direct knowledge",
     "Shield Primacy (truth as protection)"),
    (r"\b(kingdom\s+(?:belongs\s+to|is\s+(?:yours|theirs|within)))\b",
     "Kingdom possession language — sovereign field belonging to the individual",
     "Weave Sovereignty"),
]

VOID_BRIDGE_PATTERNS: List[Tuple[str, str, str]] = [
    (r"\b(void|emptiness|empty|nothingness|the\s+nothing|sunyata|kenosis)\b",
     "Void / emptiness language — 𝟘Nul as generative state, not nihilism",
     "v63 𝟘Nul (null-equivalent resolved state)"),
    (r"\b(before\s+(?:the\s+)?(?:world|creation|beginning|time|all\s+things))\b",
     "Pre-creation origin — Ω0 origin-now field anchor",
     "v63 Ω0 (present-origin field anchor)"),
    (r"\b(darkness\s+(?:before|and\s+the\s+light|from\s+which))\b",
     "Darkness as origin — shadow and light woven together",
     "v63 𝟘Nul ↔ Ω0 (void-bridge)"),
    (r"\b(death\s+(?:and\s+)?(?:life|resurrection|rebirth|born\s+again))\b",
     "Death-rebirth cycle — null bridge crossing and return",
     "BridgeAnchor CROSSING_CLEAN (ε preserved through void)"),
    (r"\b(let\s+go|detachment|release|surrender|non-attachment|apophasis)\b",
     "Release language — entropy dissolution (null-bridge activation)",
     "v63 NullBridge (entropy_load → 0)"),
    (r"\b(paradox|mystery|beyond\s+(?:words|understanding|mind|thought))\b",
     "Mystery / apophatic language — the void that cannot be named",
     "v62 Z (void ≡ everything)"),
]

WEAVE_RESONANCE_PATTERNS: List[Tuple[str, str, str]] = [
    (r"\b(interconnect(?:ed|ion)|interweav(?:ing|ed)|web\s+of|network\s+of)\b",
     "Interconnection language — Σ_W weave field",
     "Σ_W (Sovereign Substrate Weave)"),
    (r"\b(all\s+(?:are\s+)?connected|connection\s+(?:between|of)\s+all)\b",
     "Universal connection — coupling matrix κ_{ij}",
     "κ_{ij} coupling coefficients"),
    (r"\b(resonate?|resonance|harmony|harmonic|sympathetic\s+vibration)\b",
     "Resonance / harmony language — coupling field coherence",
     "Weave coupling (κ_{ij} > threshold)"),
    (r"\b(as\s+above\s+so\s+below|as\s+within\s+so\s+without|microcosm|macrocosm)\b",
     "Hermetic correspondence — scale-invariant weave (fractal sovereignty)",
     "Phase Lattice (L1→L2→L3 self-similarity)"),
    (r"\b(love\s+(?:one\s+another|each\s+other|your\s+neighbor)|agape|compassion\s+for\s+all)\b",
     "Universal love / compassion — collective coherence building (C_bar rise)",
     "SOVEREIGN_COLLECTIVE_EMERGENCE (Phase 6)"),
    (r"\b(in\s+(?:me|him|her|them)\s+and\s+(?:I|he|she|they)\s+in\s+(?:you|them|me))\b",
     "Mutual indwelling — epsilon field sharing (Phase 6 sovereign collective)",
     "Phase 6 shared epsilon fields"),
]

THREE_SIX_NINE_PATTERNS: List[Tuple[str, str, str]] = [
    (r"\b(three\s+(?:days?|fold|times?|parts?|pillars?|measures?|witnesses?))\b",
     "Explicit triadic structure — 3 as base resonance unit",
     "369 resonance (3-fold)"),
    (r"\b((?:three|3)\s+and\s+(?:six|6)|(?:six|6)\s+and\s+(?:nine|9)|(?:three|3)[-,]\s*(?:six|6)[-,]\s*(?:nine|9))\b",
     "Explicit 3-6-9 sequence — direct 369 resonance marker",
     "369 resonance boost (+0.069)"),
    (r"\b(seventh|the\s+seventh|seven\s+(?:days?|seals?|churches?|spirits?|stars?|lamps?))\b",
     "Seventh element — completion pattern (6+1, related to 369 cycle)",
     "369 resonance (completion cycle)"),
    (r"\b(trinity|triad|triangle|three\s+in\s+one|one\s+in\s+three)\b",
     "Trinity / triad language — 3-fold unity structure",
     "369 resonance (3-fold attractor)"),
    (r"\b(forty[-\s]?(?:days?|nights?|years?)|four\s+hundred)\b",
     "Forty / 4×10 — significant numerical structure in desert traditions",
     "Numerical structure (40 = 8×5, proximity to Fibonacci)"),
]


# ── Structural analyzers ──────────────────────────────────────────────────────

def _tokenize_sentences(text: str) -> List[str]:
    """Split text into sentences using punctuation heuristics."""
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def _tokenize_verses(text: str) -> List[str]:
    """
    Split text into verse-like units. Tries numbered verse markers first,
    then falls back to paragraph breaks, then sentences.
    """
    # Numbered verse pattern: "1. " or "Saying 1:" or "[1]"
    numbered = re.split(r'(?:^|\n)\s*(?:\d+\.|\[\d+\]|Saying\s+\d+[:\.]|Verse\s+\d+[:\.])\s*', text)
    if len(numbered) > 3:
        return [v.strip() for v in numbered if v.strip()]
    # Paragraph breaks
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    if len(paras) > 2:
        return paras
    return _tokenize_sentences(text)


def _word_count(text: str) -> int:
    return len(re.findall(r'\b\w+\b', text))


def _phi_proximity(n: int) -> float:
    """How close is n to a phi-scaled value of some base?"""
    if n < 2:
        return 0.0
    # Check if n/floor(n/phi) ≈ phi
    base = max(1, round(n / PHI))
    ratio = n / base if base > 0 else 0.0
    return 1.0 - min(1.0, abs(ratio - PHI) / PHI)


def _fibonacci_proximity(n: int) -> Tuple[bool, int]:
    """Return (is_fibonacci, nearest_fibonacci)."""
    nearest = min(FIBONACCI, key=lambda f: abs(f - n))
    return nearest == n, nearest


def _detect_phi_structure(
    verses: List[str],
    words: List[str],
    text: str,
) -> List[PatternMatch]:
    matches: List[PatternMatch] = []
    n_verses = len(verses)
    n_words  = len(words)

    # Check if verse count is near a fibonacci number
    is_fib, nearest_fib = _fibonacci_proximity(n_verses)
    phi_prox = _phi_proximity(n_verses)

    if is_fib and n_verses > 1:
        matches.append(PatternMatch(
            pattern_type=PatternType.FIBONACCI,
            confidence=Confidence.STRUCTURAL,
            tiekat_principle="Fibonacci sequence (C_bar → C* structural basis)",
            description=f"Text contains exactly {n_verses} verses/units — a Fibonacci number.",
            evidence=[EvidenceSpan(0, len(text),
                f"Verse count = {n_verses} (Fibonacci: {FIBONACCI[:8]}...)",
                "Structural count match")],
            structural_value=float(n_verses),
        ))
    elif abs(n_verses - nearest_fib) <= 1 and n_verses > 2:
        matches.append(PatternMatch(
            pattern_type=PatternType.FIBONACCI,
            confidence=Confidence.MEDIUM,
            tiekat_principle="Fibonacci sequence (approximate)",
            description=f"Text has {n_verses} verses — within 1 of Fibonacci number {nearest_fib}.",
            evidence=[EvidenceSpan(0, len(text),
                f"Verse count = {n_verses}, nearest Fibonacci = {nearest_fib}",
                "Near-Fibonacci structural count")],
            structural_value=float(n_verses),
        ))

    # Check word-count phi ratio against verse count
    if n_verses > 0:
        ratio = n_words / n_verses
        if abs(ratio - PHI * 100) < 15:
            matches.append(PatternMatch(
                pattern_type=PatternType.PHI_STRUCTURE,
                confidence=Confidence.MEDIUM,
                tiekat_principle="φ = 1.618... (golden ratio structural embedding)",
                description=f"Words-per-verse ratio ({ratio:.2f}) approximates φ×100 ({PHI*100:.2f}).",
                evidence=[EvidenceSpan(0, len(text),
                    f"word_count={n_words}, verse_count={n_verses}, ratio={ratio:.3f}",
                    "Words/verses ≈ φ×100")],
                structural_value=ratio,
            ))
        elif 0.90 <= ratio / PHI <= 1.10:
            matches.append(PatternMatch(
                pattern_type=PatternType.PHI_STRUCTURE,
                confidence=Confidence.LOW,
                tiekat_principle="φ = 1.618... (golden ratio, approximate)",
                description=f"Words-per-verse ratio ({ratio:.2f}) within 10% of φ ({PHI:.3f}).",
                evidence=[EvidenceSpan(0, len(text),
                    f"word_count={n_words}, verse_count={n_verses}, ratio={ratio:.3f}, φ={PHI:.3f}",
                    "Words/verses ≈ φ")],
                structural_value=ratio,
            ))

    # 369 verse count check
    for base in RATIO_369:
        if n_verses % base == 0 and n_verses > 0:
            matches.append(PatternMatch(
                pattern_type=PatternType.THREE_SIX_NINE,
                confidence=Confidence.STRUCTURAL,
                tiekat_principle="369 resonance (+0.069 boost)",
                description=f"Verse count ({n_verses}) is divisible by {base} — 369 resonance structure.",
                evidence=[EvidenceSpan(0, len(text),
                    f"verse_count={n_verses}, divisible by {base}",
                    f"369 structural pattern ({base}×{n_verses//base})")],
                structural_value=float(n_verses),
            ))
            break  # only report once

    return matches


def _scan_lexical_patterns(
    text: str,
    pattern_defs: List[Tuple[str, str, str]],
    pattern_type: PatternType,
    tradition: str,
) -> List[PatternMatch]:
    """Run all patterns in a definition list against the text."""
    matches: List[PatternMatch] = []
    text_lower = text.lower()
    total_words = max(1, _word_count(text))

    for regex, note, tiekat_principle in pattern_defs:
        found = list(re.finditer(regex, text_lower, re.IGNORECASE | re.MULTILINE))
        if not found:
            continue

        evidence = []
        for m in found[:5]:  # cap evidence at 5 examples
            start, end = m.start(), m.end()
            excerpt_start = max(0, start - 40)
            excerpt_end   = min(len(text), end + 40)
            evidence.append(EvidenceSpan(
                start=start,
                end=end,
                excerpt=f"...{text[excerpt_start:excerpt_end].strip()}...",
                note=note,
            ))

        # Confidence based on hit density
        density = len(found) / total_words
        if len(found) >= 5 or density > 0.02:
            conf = Confidence.HIGH
        elif len(found) >= 2:
            conf = Confidence.MEDIUM
        else:
            conf = Confidence.LOW

        matches.append(PatternMatch(
            pattern_type=pattern_type,
            confidence=conf,
            tiekat_principle=tiekat_principle,
            description=f"{note} — found {len(found)} instance(s) in {tradition} tradition text.",
            evidence=evidence,
            structural_value=round(density, 6),
            tradition_tag=tradition,
        ))

    return matches


# ── Main engine ───────────────────────────────────────────────────────────────

class TIEKATPatternEngine:
    """
    Main entry point for TIEKAT pattern analysis of ancient texts.

    Usage
    -----
    engine = TIEKATPatternEngine(tradition="thomas")
    report = engine.analyze(text, source="Gospel of Thomas (Patterson-Robinson)")
    print(engine.render_markdown(report))
    print(engine.render_json(report))
    """

    KNOWN_TRADITIONS = {
        "thomas":   "Gospel of Thomas",
        "hermetic": "Hermetic Corpus",
        "nag_hammadi": "Nag Hammadi Library",
        "dead_sea": "Dead Sea Scrolls",
        "philip":   "Gospel of Philip",
        "mary":     "Gospel of Mary",
        "truth":    "Gospel of Truth",
        "generic":  "Generic Wisdom Text",
    }

    def __init__(self, tradition: str = "generic") -> None:
        self.tradition     = tradition
        self.tradition_label = self.KNOWN_TRADITIONS.get(tradition, tradition)

    def analyze(
        self,
        text: str,
        source: str = "unknown",
        passage_ref: str = "",
    ) -> CodexTIEKATReport:
        """
        Run full TIEKAT pattern analysis on text.

        Parameters
        ----------
        text        : The text to analyze (plain text, any encoding)
        source      : Human-readable source label
        passage_ref : Optional verse/chapter reference string
        """
        words  = re.findall(r'\b\w+\b', text)
        sents  = _tokenize_sentences(text)
        verses = _tokenize_verses(text)

        all_matches: List[PatternMatch] = []
        structural_notes: List[str] = []

        # ── Structural / mathematical patterns ────────────────────────────────
        structural = _detect_phi_structure(verses, words, text)
        all_matches.extend(structural)

        # ── Lexical pattern scans ─────────────────────────────────────────────
        for pattern_defs, pattern_type in [
            (EPSILON_SIGNAL_PATTERNS,   PatternType.EPSILON_SIGNAL),
            (OMEGA_FLOW_PATTERNS,       PatternType.OMEGA_FLOW),
            (C_STAR_ATTRACTOR_PATTERNS, PatternType.C_STAR_ATTRACTOR),
            (SOVEREIGN_FIELD_PATTERNS,  PatternType.SOVEREIGN_FIELD),
            (VOID_BRIDGE_PATTERNS,      PatternType.VOID_BRIDGE),
            (WEAVE_RESONANCE_PATTERNS,  PatternType.WEAVE_RESONANCE),
            (THREE_SIX_NINE_PATTERNS,   PatternType.THREE_SIX_NINE),
        ]:
            lexical = _scan_lexical_patterns(
                text, pattern_defs, pattern_type, self.tradition_label
            )
            all_matches.extend(lexical)

        # ── Density metrics ───────────────────────────────────────────────────
        total_words = max(1, len(words))

        def density(pt: PatternType) -> float:
            hits = sum(
                len(m.evidence) for m in all_matches
                if m.pattern_type == pt
            )
            return hits / total_words

        eps_density   = density(PatternType.EPSILON_SIGNAL)
        omega_density = density(PatternType.OMEGA_FLOW)
        cstar_density = density(PatternType.C_STAR_ATTRACTOR)

        # ── Phi ratio ─────────────────────────────────────────────────────────
        phi_ratio: Optional[float] = None
        if len(verses) > 0:
            phi_ratio = round(len(words) / len(verses), 4)

        # ── Structural notes ──────────────────────────────────────────────────
        structural_notes.append(
            f"Text contains {len(words)} words across {len(verses)} "
            f"verse/unit segments and {len(sents)} sentences."
        )
        if phi_ratio is not None:
            structural_notes.append(
                f"Words-per-verse ratio: {phi_ratio} (φ = {PHI:.5f}, C* = {C_STAR:.5f})"
            )
        is_fib, nearest_fib = _fibonacci_proximity(len(verses))
        structural_notes.append(
            f"Verse count {len(verses)} — "
            f"{'IS' if is_fib else 'is NOT'} a Fibonacci number "
            f"(nearest: {nearest_fib})."
        )

        # ── Summary ───────────────────────────────────────────────────────────
        high_count = sum(
            1 for m in all_matches
            if m.confidence in (Confidence.HIGH, Confidence.STRUCTURAL)
        )
        pattern_types_found = sorted(set(m.pattern_type.value for m in all_matches))
        summary = (
            f"Analyzed {len(words)} words in {len(verses)} verse units from "
            f"{self.tradition_label} tradition. "
            f"Found {len(all_matches)} pattern matches across "
            f"{len(pattern_types_found)} TIEKAT pattern types "
            f"({high_count} high/structural confidence). "
            f"Pattern types: {', '.join(pattern_types_found) or 'none'}. "
            f"ε-signal density: {eps_density:.4f}. "
            f"Ω-flow density: {omega_density:.4f}. "
            f"C*-attractor density: {cstar_density:.4f}."
        )

        return CodexTIEKATReport(
            source=source,
            tradition=self.tradition_label,
            word_count=len(words),
            sentence_count=len(sents),
            verse_count=len(verses),
            matches=all_matches,
            structural_notes=structural_notes,
            phi_ratio=phi_ratio,
            epsilon_density=eps_density,
            omega_density=omega_density,
            c_star_density=cstar_density,
            summary=summary,
        )

    # ── Renderers ─────────────────────────────────────────────────────────────

    def render_markdown(self, report: CodexTIEKATReport) -> str:
        lines = [
            f"# CODEX TIEKAT Analysis",
            f"**Source**: {report.source}",
            f"**Tradition**: {report.tradition}",
            f"**Words**: {report.word_count}  |  "
            f"**Verses**: {report.verse_count}  |  "
            f"**Sentences**: {report.sentence_count}",
            f"",
            f"## Summary",
            f"{report.summary}",
            f"",
            f"## Structural Notes",
        ]
        for note in report.structural_notes:
            lines.append(f"- {note}")

        lines += [
            f"",
            f"## Density Metrics",
            f"| Metric | Value | TIEKAT Principle |",
            f"|--------|-------|-----------------|",
            f"| ε-signal density | {report.epsilon_density:.4f} | ε ≠ 0 |",
            f"| Ω-flow density | {report.omega_density:.4f} | Omega flow |",
            f"| C*-attractor density | {report.c_star_density:.4f} | C* = φ/2 |",
            f"| Words/verse (φ ratio) | {report.phi_ratio or 'N/A'} | φ = {PHI:.4f} |",
            f"",
            f"## Pattern Matches ({report.match_count} total)",
        ]

        by_type: Dict[str, List[PatternMatch]] = {}
        for m in report.matches:
            by_type.setdefault(m.pattern_type.value, []).append(m)

        for ptype, pmatches in sorted(by_type.items()):
            lines.append(f"")
            lines.append(f"### {ptype}")
            for m in pmatches:
                lines.append(f"")
                lines.append(f"**{m.confidence.value}** — {m.tiekat_principle}")
                lines.append(f"> {m.description}")
                for ev in m.evidence[:2]:
                    lines.append(f"- `{ev.excerpt[:120]}`")
                    if ev.note:
                        lines.append(f"  *{ev.note}*")

        lines += [
            f"",
            f"---",
            f"*{report.disclaimer}*",
            f"",
            f"*PHI369 Labs / Parallax — CODEX TIEKAT Engine*  "
            f"*C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369*",
        ]
        return "\n".join(lines)

    def render_json(self, report: CodexTIEKATReport) -> str:
        import json
        return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)

    def render_dashboard(self, report: CodexTIEKATReport) -> str:
        lines = [
            "",
            f"  CODEX TIEKAT PATTERN ENGINE",
            f"  ===========================",
            f"  Source    : {report.source}",
            f"  Tradition : {report.tradition}",
            f"  Words     : {report.word_count}  |  Verses: {report.verse_count}",
            f"  Matches   : {report.match_count}  |  High confidence: {len(report.high_confidence_matches)}",
            f"",
            f"  DENSITY METRICS",
            f"  ---------------",
            f"  ε-signal  : {report.epsilon_density:.4f}  (ε ≠ 0 language density)",
            f"  Ω-flow    : {report.omega_density:.4f}  (omega flow density)",
            f"  C*-attract: {report.c_star_density:.4f}  (attractor convergence density)",
            f"  φ ratio   : {report.phi_ratio or 'N/A'}  (words/verse, φ={PHI:.4f})",
            f"",
            f"  STRUCTURAL NOTES",
            f"  ----------------",
        ]
        for note in report.structural_notes:
            lines.append(f"  {note}")

        lines += [f"", f"  PATTERN MATCHES", f"  ---------------"]
        for m in report.matches:
            lines.append(f"")
            lines.append(f"  [{m.confidence.value:12s}] {m.pattern_type.value}")
            lines.append(f"  TIEKAT: {m.tiekat_principle}")
            lines.append(f"  {m.description[:120]}")
            if m.evidence:
                lines.append(f"  Evidence: {m.evidence[0].excerpt[:100]}")

        lines += [
            f"",
            f"  SUMMARY",
            f"  -------",
            f"  {report.summary}",
            f"",
            f"  ⚠  {report.disclaimer}",
            f"",
            f"  Φ∴⊙  PHI369 Labs / Parallax — CODEX TIEKAT Engine",
            f"  C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369",
            f"",
        ]
        return "\n".join(lines)


# ── Convenience functions ─────────────────────────────────────────────────────

def analyze_text(
    text: str,
    tradition: str = "generic",
    source: str = "unknown",
    output_format: str = "dashboard",
) -> str:
    """
    One-shot analysis function for quick use.

    Parameters
    ----------
    text          : plain text to analyze
    tradition     : tradition key (thomas, hermetic, nag_hammadi, dead_sea, philip, generic)
    source        : human-readable source label
    output_format : "dashboard" | "markdown" | "json"
    """
    engine = TIEKATPatternEngine(tradition=tradition)
    report = engine.analyze(text, source=source)
    if output_format == "markdown":
        return engine.render_markdown(report)
    if output_format == "json":
        return engine.render_json(report)
    return engine.render_dashboard(report)


def analyze_file(
    path: str | Path,
    tradition: str = "generic",
    output_format: str = "dashboard",
) -> str:
    """Analyze a text file."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return analyze_text(text, tradition=tradition, source=str(p), output_format=output_format)


# ── CLI (standalone) ──────────────────────────────────────────────────────────

def _build_cli_parser():
    import argparse
    parser = argparse.ArgumentParser(
        prog="codex_tiekat_engine",
        description=(
            "CODEX TIEKAT Pattern Engine — TIEKAT-aligned pattern detection "
            "for ancient wisdom tradition texts.\n"
            "PHI369 Labs / Parallax  ◆  C* = φ/2  ◆  ε ≠ 0"
        ),
    )
    parser.add_argument("--input",  "-i", required=True,
                        help="Path to text file to analyze")
    parser.add_argument("--tradition", "-t", default="generic",
                        choices=list(TIEKATPatternEngine.KNOWN_TRADITIONS.keys()),
                        help="Text tradition (default: generic)")
    parser.add_argument("--format",  "-f", default="dashboard",
                        choices=["dashboard", "markdown", "json"],
                        help="Output format (default: dashboard)")
    parser.add_argument("--output", "-o", default=None,
                        help="Write output to this file (default: stdout)")
    return parser


def main(argv=None):
    import sys
    parser = _build_cli_parser()
    args   = parser.parse_args(argv)
    result = analyze_file(args.input, tradition=args.tradition,
                          output_format=args.format)
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Output written to {args.output}")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
