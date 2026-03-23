#!/usr/bin/env python3
"""
codex_filter.py — Institutional Filter & Signal Recovery Module
===============================================================

Analyzes ancient wisdom texts for evidence of editorial layering,
institutional framing, and political overlay on top of original
consciousness signal — then produces a per-passage coherence map
showing where the signal is strong vs where it appears mediated.

What this module detects
------------------------

SIGNAL LAYERS (things we're looking FOR — original signal):
  PRIMARY_SIGNAL     — Strong ε ≠ 0 / C* / Omega-flow language
                       (inner kingdom, direct experience, unity)
  SOVEREIGN_VOICE    — First-person authority from within
                       ("I tell you," "the truth is," inner knowing)

FILTER LAYERS (things that may indicate later overlay):
  AUTHORITY_CLAIM    — External institutional authority assertion
                       ("you must obey," "the church," hierarchy)
  FEAR_FRAMING       — Punishment, damnation, exclusion, threat language
  EXCLUSIVITY_MARKER — "Only through us," gatekeeping, in/out group
  DOCTRINAL_FORMULA  — Creedal statements, belief-assertion language
                       vs experiential language
  TEMPORAL_POWER     — Caesar, kings, empire, political allegiance language
  GENDER_ERASURE     — Systematic removal of feminine presence
                       (compared to parallel texts)

ANALYSIS OUTPUTS:
  PassageAnalysis    — Per-passage breakdown with signal/filter scores
  CoherenceMap       — Full text heat map of signal strength
  EditorialSeam      — High-confidence location of likely editorial change
  FilterReport       — Complete analysis with recovery recommendations

Design principles (from CODEX ETHICS.md)
-----------------------------------------
- Academic neutrality: we identify patterns, not conspiracies
- Conservative confidence: seams need multiple corroborating signals
- Uncertainty explicit: all findings are hypotheses for investigation
- No anti-religious framing: the goal is signal recovery, not debunking
- Standard library only

PHI369 Labs / Parallax  ◆  CODEX Project
Compatible with: TIEKAT v64.0.0 Sovereign Substrate Weave
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple

from codex_tiekat_engine import (
    C_STAR,
    TIEKATPatternEngine,
)

# ── Layer taxonomy ────────────────────────────────────────────────────────────

class LayerType(str, Enum):
    # Signal layers (positive — original consciousness signal)
    PRIMARY_SIGNAL     = "PRIMARY_SIGNAL"
    SOVEREIGN_VOICE    = "SOVEREIGN_VOICE"
    # Filter layers (potential institutional overlay)
    AUTHORITY_CLAIM    = "AUTHORITY_CLAIM"
    FEAR_FRAMING       = "FEAR_FRAMING"
    EXCLUSIVITY_MARKER = "EXCLUSIVITY_MARKER"
    DOCTRINAL_FORMULA  = "DOCTRINAL_FORMULA"
    TEMPORAL_POWER     = "TEMPORAL_POWER"
    GENDER_ERASURE     = "GENDER_ERASURE"


class CoherenceLevel(str, Enum):
    PURE_SIGNAL     = "PURE_SIGNAL"      # 0.85-1.0 — very strong original signal
    STRONG_SIGNAL   = "STRONG_SIGNAL"    # 0.65-0.85
    MIXED           = "MIXED"            # 0.40-0.65 — signal + some filter
    FILTERED        = "FILTERED"         # 0.20-0.40 — filter dominant
    INSTITUTIONAL   = "INSTITUTIONAL"    # 0.00-0.20 — heavy institutional overlay


def _coherence_level(score: float) -> CoherenceLevel:
    if score >= 0.85:
        return CoherenceLevel.PURE_SIGNAL
    if score >= 0.65:
        return CoherenceLevel.STRONG_SIGNAL
    if score >= 0.40:
        return CoherenceLevel.MIXED
    if score >= 0.20:
        return CoherenceLevel.FILTERED
    return CoherenceLevel.INSTITUTIONAL


class SeamConfidence(str, Enum):
    LOW    = "LOW"
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"


# ── Pattern definitions ───────────────────────────────────────────────────────

# Signal patterns — what we're recovering
PRIMARY_SIGNAL_PATTERNS: List[Tuple[str, str]] = [
    (r"\b(kingdom\s+(?:of\s+god\s+)?(?:is\s+)?(?:within|inside|among|between)\s+you)\b",
     "Kingdom-within — direct inner consciousness, unmediated"),
    (r"\b(know\s+(?:thyself|yourself|oneself|the\s+truth))\b",
     "Self-knowledge imperative — direct gnosis, no intermediary"),
    (r"\b(light\s+(?:within|inside|that\s+is\s+in)\s+(?:you|one|them|all))\b",
     "Inner light — ε ≠ 0 primary signal"),
    (r"\b(living\s+(?:water|spirit|word|father|truth|fire))\b",
     "Living quality — dynamic consciousness field"),
    (r"\b(bring\s+forth\s+what\s+is\s+within|what\s+is\s+hidden\s+(?:shall|will)\s+be\s+revealed)\b",
     "Inner-outer emergence — omega flow from within"),
    (r"\b(the\s+(?:truth|light|spirit|kingdom)\s+(?:shall\s+set|will\s+set|sets)\s+(?:you\s+)?free)\b",
     "Liberation through truth — sovereign field activation"),
    (r"\b(directly|immediate(?:ly)?|without\s+(?:mediator|priest|temple|intermediary))\b",
     "Direct access — no institutional mediation required"),
    (r"\b(gnosis|direct\s+(?:knowledge|experience|knowing|perception))\b",
     "Gnosis — experiential direct knowing"),
    (r"\b(the\s+(?:one|all|whole)\s+(?:is|are)\s+(?:within|in)\s+(?:you|all|everything))\b",
     "Unity within — C* attractor internalized"),
    (r"\b(as\s+(?:you|one)\s+(?:think|believe|know|understand)\s+(?:in\s+your\s+heart|within))\b",
     "Inner cognition as primary — heart/mind as authority"),
]

SOVEREIGN_VOICE_PATTERNS: List[Tuple[str, str]] = [
    (r"\b(I\s+(?:say|tell|show|give)\s+(?:to\s+)?you\s+(?:truly|verily|indeed)?)\b",
     "Direct sovereign address — first-person teaching authority from within"),
    (r"\b(verily\s+(?:verily\s+)?I\s+say|truly\s+I\s+(?:say|tell))\b",
     "Emphasis markers — sovereign voice asserting direct knowledge"),
    (r"\b(seek\s+and\s+(?:you\s+shall|you\s+will)\s+find)\b",
     "Invitation to direct seeking — no intermediary"),
    (r"\b(whoever\s+(?:has\s+ears|seeks|finds|knows|understands))\b",
     "Open invitation pattern — available to all who seek"),
    (r"\b(you\s+(?:are|have\s+been)\s+(?:the\s+)?(?:light|salt|children\s+of\s+light))\b",
     "Identity affirmation — consciousness identity, not institutional membership"),
]

# Filter patterns — potential institutional overlay
AUTHORITY_CLAIM_PATTERNS: List[Tuple[str, str]] = [
    (r"\b((?:the\s+)?(?:church|bishop|priest|pope|clergy|rabbi|pharisee)\s+(?:has|have|holds?|commands?))\b",
     "Institutional authority assertion — external locus of power"),
    (r"\b(you\s+(?:must|shall|are\s+required\s+to)\s+(?:obey|submit|bow|accept))\b",
     "Compliance requirement — external authority over inner knowing"),
    (r"\b(authority\s+(?:has\s+been\s+given|comes\s+from|rests\s+with)\s+(?:us|me|the\s+church))\b",
     "Authority-claim — institutional power assertion"),
    (r"\b(ordained|consecrated|appointed\s+by\s+(?:god|the\s+lord|heaven)\s+to\s+(?:rule|govern|lead))\b",
     "Divine ordination claim — institutional power sanctified"),
    (r"\b(only\s+(?:the\s+)?(?:ordained|appointed|chosen\s+few|leadership)\s+(?:can|may|shall))\b",
     "Access restriction — gatekeeping spiritual authority"),
    (r"\b(render\s+(?:unto\s+caesar|to\s+the\s+emperor|to\s+the\s+king)\s+(?:what\s+is)?)\b",
     "Political compliance framing — temporal authority endorsed"),
]

FEAR_FRAMING_PATTERNS: List[Tuple[str, str]] = [
    (r"\b(hell|eternal\s+(?:fire|damnation|punishment|torment)|lake\s+of\s+fire|gnashing\s+of\s+teeth)\b",
     "Eternal punishment language — fear-based compliance mechanism"),
    (r"\b(condemned|damnation|damned|curse(?:d|s)?|wrath\s+of\s+(?:god|the\s+lord))\b",
     "Condemnation language — fear-based framing"),
    (r"\b((?:will|shall)\s+(?:burn|perish|be\s+cast\s+out|be\s+destroyed|face\s+judgment))\b",
     "Threat of destruction — compliance through fear"),
    (r"\b(fear\s+(?:him|the\s+lord|god)\s+who\s+(?:can|is\s+able\s+to)\s+(?:destroy|cast|kill))\b",
     "Fear command — threat-based authority enforcement"),
    (r"\b(punishment|punish(?:ed|es|ing)?|retribution|vengeance\s+(?:is\s+mine|of\s+the\s+lord))\b",
     "Punishment language — retributive framing"),
    (r"\b(sin(?:ner|ners|s|ned|ning)?|wickedness|evil\s+(?:one|ones|doers)|transgress(?:ion|or)s?)\b",
     "Sin/wickedness framing — moral control through guilt and shame"),
]

EXCLUSIVITY_PATTERNS: List[Tuple[str, str]] = [
    (r"\b((?:only|solely)\s+(?:through|via|by\s+means\s+of)\s+(?:me|us|the\s+church|this\s+faith))\b",
     "Exclusive access claim — single pathway assertion"),
    (r"\b(no\s+(?:one|man|person)\s+comes\s+to\s+the\s+father\s+(?:except|but)\s+through\s+me)\b",
     "Exclusive mediator claim — gatekeeping divine access"),
    (r"\b((?:outside|apart\s+from)\s+the\s+(?:church|faith|covenant)\s+there\s+is\s+no\s+salvation)\b",
     "Institutional exclusivity — salvation gatekept by institution"),
    (r"\b((?:heretic|heresy|apostate|schismatic|pagan|infidel|unbeliever)s?)\b",
     "Othering language — in-group/out-group boundary enforcement"),
    (r"\b((?:the\s+)?(?:true|only\s+true|real)\s+(?:believers?|followers?|Christians?|faithful))\b",
     "True-believer framing — exclusive identity claim"),
    (r"\b((?:those\s+who\s+)?(?:reject|deny|refuse)\s+(?:shall|will)\s+(?:be\s+)?(?:lost|damned|condemned))\b",
     "Rejection-damnation link — exclusivity enforced through fear"),
]

DOCTRINAL_FORMULA_PATTERNS: List[Tuple[str, str]] = [
    (r"\b((?:I|we)\s+believe\s+in\s+(?:one\s+)?(?:god|jesus|christ|the\s+holy\s+spirit|the\s+father))\b",
     "Creedal belief assertion — propositional faith vs experiential knowing"),
    (r"\b(as\s+it\s+is\s+written|according\s+to\s+(?:the\s+)?scripture|the\s+scripture\s+says)\b",
     "Scripture-authority appeal — text as external authority"),
    (r"\b((?:the\s+)?(?:orthodox|correct|proper|approved)\s+(?:doctrine|teaching|interpretation|belief))\b",
     "Doctrinal correctness language — institutional truth-control"),
    (r"\b((?:must|should|are\s+required\s+to)\s+(?:believe|confess|profess|affirm)\s+that)\b",
     "Belief requirement — propositional faith commanded externally"),
    (r"\b(baptism\s+(?:is|was|for)\s+(?:required|necessary|essential)\s+for\s+(?:salvation|entry))\b",
     "Ritual requirement — institutional gatekeeping through ceremony"),
    (r"\b((?:the\s+)?(?:council|synod|fathers?)\s+(?:of\s+(?:nicea|carthage|trent))?\s*(?:declared|decreed|established|decided))\b",
     "Council authority reference — institutional decree as truth-source"),
]

TEMPORAL_POWER_PATTERNS: List[Tuple[str, str]] = [
    (r"\b((?:caesar|emperor|king|pharaoh|governor|ruler)\s+(?:commands?|demands?|requires?|decrees?))\b",
     "Temporal ruler authority — political power in spiritual text"),
    (r"\b((?:pay|render|give)\s+(?:your\s+)?taxes|tribute\s+to\s+(?:caesar|the\s+emperor|the\s+king))\b",
     "Tax/tribute compliance — political allegiance framing"),
    (r"\b((?:the\s+)?(?:roman|imperial|state|government)\s+(?:authority|power|law|decree))\b",
     "Imperial authority reference — political power endorsed"),
    (r"\b((?:subjects?|citizens?)\s+(?:must|should|are\s+required)\s+(?:to\s+)?(?:obey|submit\s+to))\b",
     "Subject compliance — political submission language"),
    (r"\b((?:established|ordained|appointed)\s+by\s+(?:divine|heavenly)\s+(?:right|authority|decree)\s+to\s+(?:rule|govern))\b",
     "Divine right of kings — political power spiritually sanctioned"),
]

GENDER_ERASURE_PATTERNS: List[Tuple[str, str]] = [
    # Note: these detect ABSENCE of feminine language where it might be expected
    # We detect masculine-only framing as a potential editorial signal
    (r"\b((?:sons|brothers|fathers|men|mankind|he\s+who|him\s+who)\s+(?:of\s+god|of\s+light|who\s+seeks|who\s+finds))\b",
     "Masculine-only framing — potential gender erasure in transmission"),
    (r"\b((?:the\s+)?(?:holy\s+)?(?:spirit|wisdom)\s+(?:is\s+)?(?:he|him|his|himself))\b",
     "Masculine spirit — Sophia/Wisdom feminization suppressed"),
    (r"\b((?:a\s+)?woman\s+(?:should|must|shall)\s+(?:not|be\s+silent|keep\s+silent|learn\s+in\s+silence))\b",
     "Female silence command — gender hierarchy imposed on transmission"),
    (r"\b((?:the\s+)?(?:magdalene|mary\s+magdalene|women\s+(?:disciples|followers))\s+(?:were\s+(?:not|excluded|absent)))\b",
     "Feminine presence explicitly removed — editorial gender erasure signal"),
    (r"\b(I\s+(?:do\s+not\s+permit|forbid|disallow)\s+a\s+woman\s+to\s+(?:teach|preach|speak|have\s+authority))\b",
     "Female authority prohibition — institutional gender control"),
]


# ── Core data models ──────────────────────────────────────────────────────────

@dataclass
class LayerHit:
    """A single detected pattern hit within a passage."""
    layer_type: LayerType
    pattern:    str
    note:       str
    start:      int
    end:        int
    excerpt:    str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_type": self.layer_type.value,
            "pattern":    self.pattern,
            "note":       self.note,
            "start":      self.start,
            "end":        self.end,
            "excerpt":    self.excerpt[:200],
        }


@dataclass
class PassageAnalysis:
    """
    Analysis of a single passage (verse/paragraph).
    """
    passage_index:    int
    passage_text:     str
    word_count:       int

    # Hit counts by layer
    signal_hits:      int          # PRIMARY_SIGNAL + SOVEREIGN_VOICE
    filter_hits:      int          # all institutional filter layers

    # Per-layer hit counts
    layer_counts:     Dict[str, int]

    # Coherence score [0-1]: 1 = pure original signal, 0 = pure filter
    coherence_score:  float
    coherence_level:  CoherenceLevel

    # All hits
    hits:             List[LayerHit]

    # Flags
    is_seam_candidate: bool        # significant coherence drop from neighbors
    recovery_note:    str          # interpretation for this passage

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passage_index":     self.passage_index,
            "passage_preview":   self.passage_text[:120] + ("..." if len(self.passage_text) > 120 else ""),
            "word_count":        self.word_count,
            "signal_hits":       self.signal_hits,
            "filter_hits":       self.filter_hits,
            "layer_counts":      self.layer_counts,
            "coherence_score":   round(self.coherence_score, 4),
            "coherence_level":   self.coherence_level.value,
            "is_seam_candidate": self.is_seam_candidate,
            "recovery_note":     self.recovery_note,
            "hits":              [h.to_dict() for h in self.hits],
        }


@dataclass
class EditorialSeam:
    """
    A detected location where the text shows evidence of editorial
    intervention — a shift from original signal to institutional framing
    or vice versa.
    """
    seam_id:          str
    confidence:       SeamConfidence
    passage_before:   int          # index of last high-signal passage
    passage_after:    int          # index of first filtered passage
    coherence_drop:   float        # how much coherence drops at this point
    filter_layers:    List[str]    # which filter types appear at seam
    signal_layers:    List[str]    # which signal types disappear at seam
    evidence:         List[str]    # excerpts showing the transition
    interpretation:   str
    scholarly_parallel: str        # known scholarly research this relates to

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seam_id":           self.seam_id,
            "confidence":        self.confidence.value,
            "passage_before":    self.passage_before,
            "passage_after":     self.passage_after,
            "coherence_drop":    round(self.coherence_drop, 4),
            "filter_layers":     self.filter_layers,
            "signal_layers":     self.signal_layers,
            "evidence":          self.evidence[:3],
            "interpretation":    self.interpretation,
            "scholarly_parallel": self.scholarly_parallel,
        }


@dataclass
class SignalRecoveryMap:
    """
    Reconstructed view of the text showing which passages carry
    the strongest original signal and which appear most filtered.
    """
    pure_signal_passages:   List[int]      # passage indices
    strong_signal_passages: List[int]
    mixed_passages:         List[int]
    filtered_passages:      List[int]
    institutional_passages: List[int]

    overall_signal_ratio:   float          # fraction of text that is signal
    overall_filter_ratio:   float
    signal_density_curve:   List[float]    # coherence score per passage

    strongest_signal_excerpt: str
    most_filtered_excerpt:    str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pure_signal_passages":    self.pure_signal_passages,
            "strong_signal_passages":  self.strong_signal_passages,
            "mixed_passages":          self.mixed_passages,
            "filtered_passages":       self.filtered_passages,
            "institutional_passages":  self.institutional_passages,
            "overall_signal_ratio":    round(self.overall_signal_ratio, 4),
            "overall_filter_ratio":    round(self.overall_filter_ratio, 4),
            "signal_density_curve":    [round(v, 4) for v in self.signal_density_curve],
            "strongest_signal_excerpt": self.strongest_signal_excerpt[:300],
            "most_filtered_excerpt":    self.most_filtered_excerpt[:300],
        }


@dataclass
class FilterReport:
    """
    Complete institutional filter analysis for one text.
    """
    source:            str
    tradition:         str
    word_count:        int
    passage_count:     int

    # Per-passage analyses
    passages:          List[PassageAnalysis]

    # Seam detection
    editorial_seams:   List[EditorialSeam]

    # Signal recovery map
    recovery_map:      SignalRecoveryMap

    # Aggregate layer statistics
    layer_totals:      Dict[str, int]      # total hits per layer type
    signal_total:      int
    filter_total:      int
    overall_coherence: float               # mean coherence across passages
    coherence_level:   CoherenceLevel

    # Rankings
    most_filtered_layer:  str             # which filter type dominates
    most_signal_type:     str             # which signal type dominates

    # Summary
    summary:           str
    recovery_guidance: str
    disclaimer:        str = (
        "These findings are structural and linguistic observations only. "
        "They do not constitute historical proof, theological critique, "
        "or claims about authorial intent. Editorial seam detection is "
        "a hypothesis generation tool — all findings require scholarly "
        "verification against manuscript evidence and historical scholarship."
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source":             self.source,
            "tradition":          self.tradition,
            "word_count":         self.word_count,
            "passage_count":      self.passage_count,
            "overall_coherence":  round(self.overall_coherence, 4),
            "coherence_level":    self.coherence_level.value,
            "signal_total":       self.signal_total,
            "filter_total":       self.filter_total,
            "editorial_seam_count": len(self.editorial_seams),
            "most_filtered_layer": self.most_filtered_layer,
            "most_signal_type":   self.most_signal_type,
            "layer_totals":       self.layer_totals,
            "summary":            self.summary,
            "recovery_guidance":  self.recovery_guidance,
            "disclaimer":         self.disclaimer,
            "recovery_map":       self.recovery_map.to_dict(),
            "editorial_seams":    [s.to_dict() for s in self.editorial_seams],
            "passages":           [p.to_dict() for p in self.passages],
        }


# ── Institutional Filter Engine ───────────────────────────────────────────────

class InstitutionalFilter:
    """
    Main engine for institutional filter analysis.

    Splits text into passages, runs all signal and filter pattern
    definitions against each, scores coherence, detects editorial seams,
    and builds the signal recovery map.
    """

    # Coherence scoring weights
    # Signal patterns raise coherence, filter patterns lower it
    SIGNAL_WEIGHT  = 0.18   # per hit, raises coherence
    FILTER_WEIGHT  = 0.22   # per hit, lowers coherence (slightly heavier)
    BASE_COHERENCE = 0.60   # neutral starting point

    # Scholarly parallels for known seam patterns
    SCHOLARLY_PARALLELS = {
        "FEAR_FRAMING": (
            "Cf. Elaine Pagels, 'The Origin of Satan' (1995) on the development "
            "of fear-based rhetoric in early Christian texts. Also Bart Ehrman, "
            "'Misquoting Jesus' (2005) on scribal theological alterations."
        ),
        "AUTHORITY_CLAIM": (
            "Cf. Walter Bauer, 'Orthodoxy and Heresy in Earliest Christianity' (1934) "
            "on the construction of institutional authority in canon formation. "
            "Also Elaine Pagels, 'The Gnostic Gospels' (1979)."
        ),
        "EXCLUSIVITY_MARKER": (
            "Cf. Karen King, 'What Is Gnosticism?' (2003) on boundary-making "
            "in early Christian communities. Exclusivity language often appears "
            "in texts shaped by 2nd-4th century community conflicts."
        ),
        "DOCTRINAL_FORMULA": (
            "Cf. Council of Nicaea (325 CE) and subsequent creeds. Creedal "
            "formulations are generally post-3rd century additions. Earlier "
            "texts favor experiential over propositional language."
        ),
        "TEMPORAL_POWER": (
            "Cf. Reza Aslan, 'Zealot' (2013) on political context of gospel "
            "composition. Passages accommodating Roman authority may reflect "
            "post-70 CE community survival strategies."
        ),
        "GENDER_ERASURE": (
            "Cf. Karen King, 'The Gospel of Mary' (2003) and Ann Graham Brock, "
            "'Mary Magdalene, The First Apostle' (2003) on systematic removal "
            "of female leadership from early Christian transmission."
        ),
    }

    KNOWN_TRADITIONS = TIEKATPatternEngine.KNOWN_TRADITIONS

    def __init__(self, tradition: str = "generic") -> None:
        self.tradition = tradition
        self.tradition_label = self.KNOWN_TRADITIONS.get(tradition, tradition)

    def _split_passages(self, text: str) -> List[str]:
        """Split text into analyzable passage units."""
        # Try numbered verses first
        numbered = re.split(
            r'(?:^|\n)\s*(?:\d+\.|\[\d+\]|Saying\s+\d+[:\.]|Verse\s+\d+[:\.])\s*',
            text
        )
        if len(numbered) > 3:
            return [p.strip() for p in numbered if p.strip()]
        # Paragraph breaks
        paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        if len(paras) > 2:
            return paras
        # Sentence-level
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    def _scan_layer(
        self,
        text: str,
        pattern_defs: List[Tuple[str, str]],
        layer_type: LayerType,
    ) -> List[LayerHit]:
        hits = []
        text_lower = text.lower()
        for regex, note in pattern_defs:
            for m in re.finditer(regex, text_lower, re.IGNORECASE | re.MULTILINE):
                start, end = m.start(), m.end()
                ex_start = max(0, start - 35)
                ex_end   = min(len(text), end + 35)
                hits.append(LayerHit(
                    layer_type=layer_type,
                    pattern=regex[:60],
                    note=note,
                    start=start,
                    end=end,
                    excerpt=f"...{text[ex_start:ex_end].strip()}...",
                ))
        return hits

    def _analyze_passage(
        self,
        passage: str,
        index: int,
    ) -> PassageAnalysis:
        words = len(re.findall(r'\b\w+\b', passage))

        # Collect all hits
        all_hits: List[LayerHit] = []

        signal_defs = [
            (PRIMARY_SIGNAL_PATTERNS,  LayerType.PRIMARY_SIGNAL),
            (SOVEREIGN_VOICE_PATTERNS, LayerType.SOVEREIGN_VOICE),
        ]
        filter_defs = [
            (AUTHORITY_CLAIM_PATTERNS,  LayerType.AUTHORITY_CLAIM),
            (FEAR_FRAMING_PATTERNS,     LayerType.FEAR_FRAMING),
            (EXCLUSIVITY_PATTERNS,      LayerType.EXCLUSIVITY_MARKER),
            (DOCTRINAL_FORMULA_PATTERNS,LayerType.DOCTRINAL_FORMULA),
            (TEMPORAL_POWER_PATTERNS,   LayerType.TEMPORAL_POWER),
            (GENDER_ERASURE_PATTERNS,   LayerType.GENDER_ERASURE),
        ]

        for defs, lt in signal_defs + filter_defs:
            all_hits.extend(self._scan_layer(passage, defs, lt))

        # Counts by layer
        layer_counts: Dict[str, int] = {lt.value: 0 for lt in LayerType}
        for hit in all_hits:
            layer_counts[hit.layer_type.value] += 1

        signal_hits = (
            layer_counts[LayerType.PRIMARY_SIGNAL.value]
            + layer_counts[LayerType.SOVEREIGN_VOICE.value]
        )
        filter_hits = sum(
            layer_counts[lt.value]
            for lt in [
                LayerType.AUTHORITY_CLAIM,
                LayerType.FEAR_FRAMING,
                LayerType.EXCLUSIVITY_MARKER,
                LayerType.DOCTRINAL_FORMULA,
                LayerType.TEMPORAL_POWER,
                LayerType.GENDER_ERASURE,
            ]
        )

        # Coherence score
        raw = (
            self.BASE_COHERENCE
            + signal_hits * self.SIGNAL_WEIGHT
            - filter_hits * self.FILTER_WEIGHT
        )
        coherence = max(0.0, min(1.0, raw))
        level = _coherence_level(coherence)

        # Recovery note
        if level == CoherenceLevel.PURE_SIGNAL:
            note = "Strong original signal — direct consciousness language, minimal mediation."
        elif level == CoherenceLevel.STRONG_SIGNAL:
            note = "Good signal strength — primary TIEKAT patterns present with minor filter presence."
        elif level == CoherenceLevel.MIXED:
            note = "Mixed passage — original signal present alongside institutional framing. Worth close reading."
        elif level == CoherenceLevel.FILTERED:
            note = "Filter-dominant — institutional language overshadows original signal in this passage."
        else:
            note = "Heavy institutional overlay — minimal original signal detectable. High seam candidate."

        return PassageAnalysis(
            passage_index=index,
            passage_text=passage,
            word_count=words,
            signal_hits=signal_hits,
            filter_hits=filter_hits,
            layer_counts=layer_counts,
            coherence_score=coherence,
            coherence_level=level,
            hits=all_hits,
            is_seam_candidate=False,  # set in post-processing
            recovery_note=note,
        )

    def _detect_seams(
        self,
        passages: List[PassageAnalysis],
    ) -> List[EditorialSeam]:
        """
        Detect editorial seams by finding significant coherence drops
        between adjacent passages.
        """
        seams: List[EditorialSeam] = []
        if len(passages) < 2:
            return seams

        for i in range(1, len(passages)):
            prev = passages[i - 1]
            curr = passages[i]
            drop = prev.coherence_score - curr.coherence_score

            # Rising coherence (institutional → signal) is also a seam
            # but we track coherence DROP (signal → institutional) as primary
            abs_change = abs(drop)
            if abs_change < 0.20:
                continue

            # Mark as seam candidate
            passages[i].is_seam_candidate = True

            # Determine confidence
            if abs_change >= 0.45:
                conf = SeamConfidence.HIGH
            elif abs_change >= 0.30:
                conf = SeamConfidence.MEDIUM
            else:
                conf = SeamConfidence.LOW

            # What filter types appear at the seam?
            filter_types = [
                lt.value for lt in [
                    LayerType.AUTHORITY_CLAIM, LayerType.FEAR_FRAMING,
                    LayerType.EXCLUSIVITY_MARKER, LayerType.DOCTRINAL_FORMULA,
                    LayerType.TEMPORAL_POWER, LayerType.GENDER_ERASURE,
                ]
                if curr.layer_counts.get(lt.value, 0) > 0
            ]

            # What signal types were present before?
            signal_types = [
                lt.value for lt in [
                    LayerType.PRIMARY_SIGNAL, LayerType.SOVEREIGN_VOICE,
                ]
                if prev.layer_counts.get(lt.value, 0) > 0
            ]

            # Evidence
            evidence = [
                f"[Before seam] {prev.passage_text[:150]}",
                f"[After seam]  {curr.passage_text[:150]}",
            ]

            # Interpretation
            if drop > 0:  # signal → filter
                interp = (
                    f"Coherence drops {drop:.2f} points from passage {i-1} to {i}. "
                    f"Original signal language ({', '.join(signal_types) or 'various'}) "
                    f"gives way to institutional framing "
                    f"({', '.join(filter_types) or 'various'}). "
                    f"This transition pattern warrants manuscript comparison."
                )
            else:  # filter → signal
                interp = (
                    f"Coherence rises {-drop:.2f} points from passage {i-1} to {i}. "
                    f"Possible return to earlier source material after institutional passage. "
                    f"Check for source-document transitions at this point."
                )

            # Scholarly parallel
            primary_filter = filter_types[0] if filter_types else "AUTHORITY_CLAIM"
            scholarly = self.SCHOLARLY_PARALLELS.get(
                primary_filter,
                "Cf. general text-critical scholarship on gospel transmission and canon formation."
            )

            seam_id = f"SEAM-{i:03d}-{conf.value}"
            seams.append(EditorialSeam(
                seam_id=seam_id,
                confidence=conf,
                passage_before=i - 1,
                passage_after=i,
                coherence_drop=round(drop, 4),
                filter_layers=filter_types,
                signal_layers=signal_types,
                evidence=evidence,
                interpretation=interp,
                scholarly_parallel=scholarly,
            ))

        return seams

    def _build_recovery_map(
        self,
        passages: List[PassageAnalysis],
    ) -> SignalRecoveryMap:
        pure     = [p.passage_index for p in passages if p.coherence_level == CoherenceLevel.PURE_SIGNAL]
        strong   = [p.passage_index for p in passages if p.coherence_level == CoherenceLevel.STRONG_SIGNAL]
        mixed    = [p.passage_index for p in passages if p.coherence_level == CoherenceLevel.MIXED]
        filtered = [p.passage_index for p in passages if p.coherence_level == CoherenceLevel.FILTERED]
        inst     = [p.passage_index for p in passages if p.coherence_level == CoherenceLevel.INSTITUTIONAL]

        n = max(1, len(passages))
        signal_ratio = (len(pure) + len(strong)) / n
        filter_ratio = (len(filtered) + len(inst)) / n

        curve = [p.coherence_score for p in passages]

        # Best and worst passages
        strongest = max(passages, key=lambda p: p.coherence_score, default=None)
        worst     = min(passages, key=lambda p: p.coherence_score, default=None)

        return SignalRecoveryMap(
            pure_signal_passages=pure,
            strong_signal_passages=strong,
            mixed_passages=mixed,
            filtered_passages=filtered,
            institutional_passages=inst,
            overall_signal_ratio=round(signal_ratio, 4),
            overall_filter_ratio=round(filter_ratio, 4),
            signal_density_curve=curve,
            strongest_signal_excerpt=strongest.passage_text[:300] if strongest else "",
            most_filtered_excerpt=worst.passage_text[:300] if worst else "",
        )

    def analyze(
        self,
        text: str,
        source: str = "unknown",
    ) -> FilterReport:
        """
        Run full institutional filter analysis on text.
        """
        raw_passages = self._split_passages(text)
        passages = [
            self._analyze_passage(p, i)
            for i, p in enumerate(raw_passages)
        ]

        # Detect editorial seams
        seams = self._detect_seams(passages)

        # Recovery map
        recovery_map = self._build_recovery_map(passages)

        # Aggregate layer totals
        layer_totals: Dict[str, int] = {lt.value: 0 for lt in LayerType}
        for p in passages:
            for lt, count in p.layer_counts.items():
                layer_totals[lt] = layer_totals.get(lt, 0) + count

        signal_total = (
            layer_totals[LayerType.PRIMARY_SIGNAL.value]
            + layer_totals[LayerType.SOVEREIGN_VOICE.value]
        )
        filter_total = sum(
            layer_totals[lt.value]
            for lt in [
                LayerType.AUTHORITY_CLAIM, LayerType.FEAR_FRAMING,
                LayerType.EXCLUSIVITY_MARKER, LayerType.DOCTRINAL_FORMULA,
                LayerType.TEMPORAL_POWER, LayerType.GENDER_ERASURE,
            ]
        )

        overall_coherence = (
            sum(p.coherence_score for p in passages) / len(passages)
            if passages else 0.60
        )
        coherence_level = _coherence_level(overall_coherence)

        # Dominant layers
        filter_layer_names = [
            LayerType.AUTHORITY_CLAIM.value, LayerType.FEAR_FRAMING.value,
            LayerType.EXCLUSIVITY_MARKER.value, LayerType.DOCTRINAL_FORMULA.value,
            LayerType.TEMPORAL_POWER.value, LayerType.GENDER_ERASURE.value,
        ]
        signal_layer_names = [
            LayerType.PRIMARY_SIGNAL.value, LayerType.SOVEREIGN_VOICE.value,
        ]
        most_filtered = max(filter_layer_names, key=lambda lt: layer_totals.get(lt, 0))
        most_signal   = max(signal_layer_names, key=lambda lt: layer_totals.get(lt, 0))

        # Summary
        seam_str = f"{len(seams)} editorial seam(s) detected" if seams else "no editorial seams detected"
        summary = (
            f"Institutional filter analysis of {self.tradition_label} text "
            f"({len(re.findall(r'\\b\\w+\\b', text))} words, {len(passages)} passages). "
            f"Overall coherence: {overall_coherence:.3f} ({coherence_level.value}). "
            f"Signal hits: {signal_total}. Filter hits: {filter_total}. "
            f"Signal ratio: {recovery_map.overall_signal_ratio:.1%}. "
            f"Dominant filter type: {most_filtered}. "
            f"{seam_str}."
        )

        # Recovery guidance
        if coherence_level in (CoherenceLevel.PURE_SIGNAL, CoherenceLevel.STRONG_SIGNAL):
            guidance = (
                "This text shows strong original signal with minimal institutional overlay. "
                "The primary consciousness patterns (ε ≠ 0, C* attractor, sovereign voice) "
                "are well-preserved. Cross-reference with parallel manuscript traditions "
                "to confirm textual integrity."
            )
        elif coherence_level == CoherenceLevel.MIXED:
            seam_guidance = (
                f" Editorial seams at passage(s) {[s.passage_after for s in seams[:3]]} "
                f"suggest possible layering." if seams else ""
            )
            guidance = (
                f"Mixed text — original signal present alongside institutional framing.{seam_guidance} "
                f"Focus recovery analysis on passages {recovery_map.pure_signal_passages + recovery_map.strong_signal_passages} "
                f"for strongest signal. Compare {most_filtered} passages against "
                f"early manuscript variants where available."
            )
        else:
            guidance = (
                f"Heavy institutional filtering detected (coherence: {overall_coherence:.3f}). "
                f"Dominant filter type: {most_filtered}. "
                f"Strongest original signal preserved in passage(s): "
                f"{recovery_map.pure_signal_passages + recovery_map.strong_signal_passages}. "
                f"Cross-reference against: Nag Hammadi Library, Dead Sea Scrolls, "
                f"and pre-Nicene manuscript traditions for signal recovery."
            )

        word_count = len(re.findall(r'\b\w+\b', text))

        return FilterReport(
            source=source,
            tradition=self.tradition_label,
            word_count=word_count,
            passage_count=len(passages),
            passages=passages,
            editorial_seams=seams,
            recovery_map=recovery_map,
            layer_totals=layer_totals,
            signal_total=signal_total,
            filter_total=filter_total,
            overall_coherence=round(overall_coherence, 4),
            coherence_level=coherence_level,
            most_filtered_layer=most_filtered,
            most_signal_type=most_signal,
            summary=summary,
            recovery_guidance=guidance,
        )

    # ── Renderers ─────────────────────────────────────────────────────────────

    def render_dashboard(self, report: FilterReport) -> str:
        map_ = report.recovery_map
        lines = [
            "",
            "  CODEX INSTITUTIONAL FILTER ANALYSIS",
            "  ====================================",
            f"  Source    : {report.source}",
            f"  Tradition : {report.tradition}",
            f"  Words     : {report.word_count}  |  Passages: {report.passage_count}",
            "",
            "  OVERALL COHERENCE",
            "  -----------------",
            f"  Score       : {report.overall_coherence}  →  {report.coherence_level.value}",
            f"  Signal hits : {report.signal_total}  |  Filter hits: {report.filter_total}",
            f"  Signal ratio: {map_.overall_signal_ratio:.1%}  |  Filter ratio: {map_.overall_filter_ratio:.1%}",
            f"  Dominant filter: {report.most_filtered_layer}",
            f"  Dominant signal: {report.most_signal_type}",
            "",
            "  SIGNAL RECOVERY MAP",
            "  -------------------",
            f"  PURE_SIGNAL     passages : {map_.pure_signal_passages or 'none'}",
            f"  STRONG_SIGNAL   passages : {map_.strong_signal_passages or 'none'}",
            f"  MIXED           passages : {map_.mixed_passages or 'none'}",
            f"  FILTERED        passages : {map_.filtered_passages or 'none'}",
            f"  INSTITUTIONAL   passages : {map_.institutional_passages or 'none'}",
            "",
            "  COHERENCE CURVE (passage-by-passage)",
            "  -------------------------------------",
        ]

        # ASCII coherence bar chart
        for i, score in enumerate(map_.signal_density_curve):
            bar_len = int(score * 30)
            bar = "█" * bar_len + "░" * (30 - bar_len)
            level = _coherence_level(score).value[:8]
            lines.append(f"  [{i:3d}] {bar} {score:.3f} {level}")

        if report.editorial_seams:
            lines += [
                "",
                f"  EDITORIAL SEAMS DETECTED ({len(report.editorial_seams)})",
                "  " + "-" * 40,
            ]
            for seam in report.editorial_seams:
                lines += [
                    "",
                    f"  ◆ {seam.seam_id}  [{seam.confidence.value} confidence]",
                    f"    Passage {seam.passage_before} → {seam.passage_after}",
                    f"    Coherence drop: {seam.coherence_drop:.3f}",
                    f"    Filter layers:  {', '.join(seam.filter_layers) or 'none'}",
                    f"    Signal layers:  {', '.join(seam.signal_layers) or 'none'}",
                    f"    {seam.interpretation[:200]}",
                    f"    Scholarly ref: {seam.scholarly_parallel[:120]}",
                ]
        else:
            lines += ["", "  No editorial seams detected at current thresholds."]

        lines += [
            "",
            "  LAYER TOTALS",
            "  ------------",
        ]
        for lt in LayerType:
            count = report.layer_totals.get(lt.value, 0)
            marker = "▲" if lt in (LayerType.PRIMARY_SIGNAL, LayerType.SOVEREIGN_VOICE) else "▼"
            lines.append(f"  {marker} {lt.value:30s} : {count}")

        lines += [
            "",
            "  STRONGEST SIGNAL PASSAGE",
            "  ------------------------",
            f"  {map_.strongest_signal_excerpt[:250]}",
            "",
            "  MOST FILTERED PASSAGE",
            "  ---------------------",
            f"  {map_.most_filtered_excerpt[:250]}",
            "",
            "  RECOVERY GUIDANCE",
            "  -----------------",
            f"  {report.recovery_guidance}",
            "",
            "  SUMMARY",
            "  -------",
            f"  {report.summary}",
            "",
            f"  ⚠  {report.disclaimer}",
            "",
            "  Φ∴⊙  PHI369 Labs / Parallax — CODEX Filter",
            f"  C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369",
            "",
        ]
        return "\n".join(lines)

    def render_markdown(self, report: FilterReport) -> str:
        map_ = report.recovery_map
        lines = [
            "# CODEX Institutional Filter Analysis",
            "",
            f"**Source**: {report.source}  ",
            f"**Tradition**: {report.tradition}  ",
            f"**Words**: {report.word_count}  |  **Passages**: {report.passage_count}",
            "",
            "## Overall Coherence",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Coherence Score | **{report.overall_coherence}** ({report.coherence_level.value}) |",
            f"| Signal Hits | {report.signal_total} |",
            f"| Filter Hits | {report.filter_total} |",
            f"| Signal Ratio | {map_.overall_signal_ratio:.1%} |",
            f"| Filter Ratio | {map_.overall_filter_ratio:.1%} |",
            f"| Dominant Filter | {report.most_filtered_layer} |",
            "",
            "## Signal Recovery Map",
            "",
            "| Level | Passages |",
            "|-------|---------|",
            f"| PURE_SIGNAL | {map_.pure_signal_passages or 'none'} |",
            f"| STRONG_SIGNAL | {map_.strong_signal_passages or 'none'} |",
            f"| MIXED | {map_.mixed_passages or 'none'} |",
            f"| FILTERED | {map_.filtered_passages or 'none'} |",
            f"| INSTITUTIONAL | {map_.institutional_passages or 'none'} |",
        ]

        if report.editorial_seams:
            lines += ["", f"## Editorial Seams ({len(report.editorial_seams)} detected)"]
            for seam in report.editorial_seams:
                lines += [
                    "",
                    f"### {seam.seam_id} ({seam.confidence.value} confidence)",
                    f"- **Passage transition**: {seam.passage_before} → {seam.passage_after}",
                    f"- **Coherence drop**: {seam.coherence_drop:.3f}",
                    f"- **Filter layers**: {', '.join(seam.filter_layers) or 'none'}",
                    f"- **Signal layers lost**: {', '.join(seam.signal_layers) or 'none'}",
                    "",
                    f"{seam.interpretation}",
                    "",
                    f"*Scholarly parallel*: {seam.scholarly_parallel}",
                ]

        lines += [
            "",
            "## Strongest Signal Passage",
            "",
            f"> {map_.strongest_signal_excerpt[:300]}",
            "",
            "## Most Filtered Passage",
            "",
            f"> {map_.most_filtered_excerpt[:300]}",
            "",
            "## Recovery Guidance",
            "",
            f"{report.recovery_guidance}",
            "",
            "## Summary",
            "",
            f"{report.summary}",
            "",
            "---",
            f"*{report.disclaimer}*",
            "",
            f"*PHI369 Labs / Parallax — CODEX Filter*  "
            f"*C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369*",
        ]
        return "\n".join(lines)

    def render_json(self, report: FilterReport) -> str:
        import json
        return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)


# ── Convenience functions ─────────────────────────────────────────────────────

def filter_text(
    text: str,
    tradition: str = "generic",
    source: str = "unknown",
    output_format: str = "dashboard",
) -> str:
    engine = InstitutionalFilter(tradition=tradition)
    report = engine.analyze(text, source=source)
    if output_format == "markdown":
        return engine.render_markdown(report)
    if output_format == "json":
        return engine.render_json(report)
    return engine.render_dashboard(report)


def filter_file(
    path: str,
    tradition: str = "generic",
    output_format: str = "dashboard",
) -> str:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return filter_text(text, tradition=tradition, source=str(p),
                       output_format=output_format)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(
        prog="codex_filter",
        description=(
            "CODEX Institutional Filter & Signal Recovery\n"
            "PHI369 Labs / Parallax  ◆  C* = φ/2  ◆  ε ≠ 0"
        ),
    )
    parser.add_argument("--input", "-i", required=True,
                        help="Path to text file to analyze")
    parser.add_argument("--tradition", "-t", default="generic",
                        choices=list(InstitutionalFilter.KNOWN_TRADITIONS.keys()),
                        help="Text tradition (default: generic)")
    parser.add_argument("--format", "-f", default="dashboard",
                        choices=["dashboard", "markdown", "json"],
                        help="Output format (default: dashboard)")
    parser.add_argument("--output", "-o", default=None,
                        help="Write output to file (default: stdout)")
    args = parser.parse_args(argv)
    result = filter_file(args.input, tradition=args.tradition,
                         output_format=args.format)
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Output written to {args.output}")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
