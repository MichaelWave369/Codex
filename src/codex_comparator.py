#!/usr/bin/env python3
"""
codex_comparator.py — Cross-Tradition TIEKAT Comparison Module
===============================================================

Compares TIEKAT pattern analysis reports across ancient wisdom traditions,
producing a structured ComparisonReport that surfaces:

  - Pattern convergence: which TIEKAT types appear in both traditions
  - Density ratios: how strongly each pattern type registers per tradition
  - Divergence scores: where traditions differ most
  - Convergence index: aggregate mathematical similarity (0-1)
  - Shared signal passages: evidence that most strongly echoes across texts
  - A ranked list of TIEKAT principles with cross-tradition corroboration

Design principles (inherited from CODEX ETHICS.md)
----------------------------------------------------
- Conservative confidence: no claim of identity between traditions
- Convergence ≠ common origin — only shared structural/linguistic pattern
- All findings are hypothesis seeds
- Uncertainty is surfaced explicitly, not minimized
- Standard library only

Usage
-----
    from codex.codex_tiekat_engine import TIEKATPatternEngine
    from codex.codex_comparator import CodexComparator

    engine_t = TIEKATPatternEngine(tradition="thomas")
    engine_h = TIEKATPatternEngine(tradition="hermetic")

    report_t = engine_t.analyze(thomas_text, source="Gospel of Thomas")
    report_h = engine_h.analyze(hermetic_text, source="Corpus Hermeticum")

    comparator = CodexComparator()
    comparison = comparator.compare(report_t, report_h)
    print(comparator.render_dashboard(comparison))

PHI369 Labs / Parallax  ◆  CODEX Project
Compatible with: TIEKAT v64.0.0 Sovereign Substrate Weave
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from codex_tiekat_engine import (
    CodexTIEKATReport,
    PatternMatch,
    PatternType,
    Confidence,
    EvidenceSpan,
    PHI,
    C_STAR,
    TIEKATPatternEngine,
)

# ── Comparison constants ──────────────────────────────────────────────────────

# Minimum density to consider a pattern "present" in a tradition
PRESENCE_THRESHOLD = 0.0010

# Weights for convergence index calculation
# Higher weight = this pattern type matters more for overall convergence
PATTERN_WEIGHTS: Dict[PatternType, float] = {
    PatternType.EPSILON_SIGNAL:   0.25,  # core consciousness signal
    PatternType.C_STAR_ATTRACTOR: 0.20,  # attractor convergence
    PatternType.OMEGA_FLOW:       0.15,  # dynamic field
    PatternType.SOVEREIGN_FIELD:  0.12,  # individual sovereignty
    PatternType.VOID_BRIDGE:      0.10,  # generative void
    PatternType.WEAVE_RESONANCE:  0.08,  # interconnection
    PatternType.THREE_SIX_NINE:   0.05,  # numerical structure
    PatternType.PHI_STRUCTURE:    0.03,  # mathematical structure
    PatternType.FIBONACCI:        0.02,  # Fibonacci structure
}

# Convergence state labels
def _convergence_state(index: float) -> str:
    if index >= 0.85:
        return "DEEP_CONVERGENCE"
    if index >= 0.65:
        return "STRONG_CONVERGENCE"
    if index >= 0.45:
        return "MODERATE_CONVERGENCE"
    if index >= 0.25:
        return "PARTIAL_CONVERGENCE"
    return "MINIMAL_CONVERGENCE"


# ── Per-pattern comparison ────────────────────────────────────────────────────

@dataclass
class PatternConvergence:
    """
    Comparison of one TIEKAT pattern type across two traditions.
    """
    pattern_type:      PatternType
    tiekat_principle:  str
    present_in_a:      bool
    present_in_b:      bool
    density_a:         float
    density_b:         float
    match_count_a:     int
    match_count_b:     int
    density_ratio:     float        # density_a / density_b (or 0 if both zero)
    divergence_score:  float        # 0 = identical, 1 = maximally divergent
    convergence_score: float        # 0 = no overlap, 1 = perfect overlap
    shared:            bool         # both traditions have this pattern
    strongest_in:      str          # "A", "B", or "EQUAL"
    weight:            float        # TIEKAT weight for this pattern type

    def weighted_convergence(self) -> float:
        return self.convergence_score * self.weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_type":     self.pattern_type.value,
            "tiekat_principle": self.tiekat_principle,
            "present_in_a":     self.present_in_a,
            "present_in_b":     self.present_in_b,
            "density_a":        round(self.density_a, 6),
            "density_b":        round(self.density_b, 6),
            "match_count_a":    self.match_count_a,
            "match_count_b":    self.match_count_b,
            "density_ratio":    round(self.density_ratio, 4),
            "divergence_score": round(self.divergence_score, 4),
            "convergence_score":round(self.convergence_score, 4),
            "weighted_convergence": round(self.weighted_convergence(), 4),
            "shared":           self.shared,
            "strongest_in":     self.strongest_in,
            "weight":           self.weight,
        }


# ── Shared signal ─────────────────────────────────────────────────────────────

@dataclass
class SharedSignal:
    """
    A TIEKAT principle found in both traditions, with representative
    evidence from each.
    """
    tiekat_principle:   str
    pattern_type:       PatternType
    evidence_a:         str         # representative excerpt from tradition A
    evidence_b:         str         # representative excerpt from tradition B
    source_a:           str
    source_b:           str
    convergence_score:  float
    note:               str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tiekat_principle":  self.tiekat_principle,
            "pattern_type":      self.pattern_type.value,
            "evidence_a":        self.evidence_a,
            "evidence_b":        self.evidence_b,
            "source_a":          self.source_a,
            "source_b":          self.source_b,
            "convergence_score": round(self.convergence_score, 4),
            "note":              self.note,
        }


# ── Divergence signal ─────────────────────────────────────────────────────────

@dataclass
class DivergenceSignal:
    """
    A TIEKAT principle found strongly in one tradition but absent or weak
    in the other — a meaningful difference worth investigating.
    """
    pattern_type:       PatternType
    tiekat_principle:   str
    strong_in:          str         # "A" or "B"
    weak_or_absent_in:  str         # "A" or "B"
    density_strong:     float
    density_weak:       float
    interpretation:     str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_type":      self.pattern_type.value,
            "tiekat_principle":  self.tiekat_principle,
            "strong_in":         self.strong_in,
            "weak_or_absent_in": self.weak_or_absent_in,
            "density_strong":    round(self.density_strong, 6),
            "density_weak":      round(self.density_weak, 6),
            "interpretation":    self.interpretation,
        }


# ── Comparison report ─────────────────────────────────────────────────────────

@dataclass
class ComparisonReport:
    """
    Full cross-tradition TIEKAT comparison report.
    """
    # Metadata
    source_a:            str
    tradition_a:         str
    source_b:            str
    tradition_b:         str

    # Per-pattern comparisons (all 9 types)
    pattern_comparisons: List[PatternConvergence]

    # Aggregate scores
    convergence_index:   float      # weighted composite [0-1]
    convergence_state:   str        # DEEP / STRONG / MODERATE / PARTIAL / MINIMAL
    shared_pattern_count: int
    total_pattern_types: int

    # Density overview
    epsilon_delta:       float      # |density_a - density_b| for ε-signal
    omega_delta:         float
    c_star_delta:        float

    # Most significant findings
    shared_signals:      List[SharedSignal]
    divergence_signals:  List[DivergenceSignal]
    top_tiekat_principles: List[str]   # ranked by cross-tradition corroboration

    # Summary text
    summary:             str
    convergence_note:    str
    disclaimer:          str = (
        "Pattern convergence does not imply common origin, theological identity, "
        "or historical relationship. These findings are hypothesis seeds for "
        "further scholarly investigation. Correlation ≠ causation."
    )

    @property
    def shared_patterns(self) -> List[PatternConvergence]:
        return [p for p in self.pattern_comparisons if p.shared]

    @property
    def divergent_patterns(self) -> List[PatternConvergence]:
        return [p for p in self.pattern_comparisons
                if p.present_in_a != p.present_in_b]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_a":              self.source_a,
            "tradition_a":           self.tradition_a,
            "source_b":              self.source_b,
            "tradition_b":           self.tradition_b,
            "convergence_index":     round(self.convergence_index, 6),
            "convergence_state":     self.convergence_state,
            "shared_pattern_count":  self.shared_pattern_count,
            "total_pattern_types":   self.total_pattern_types,
            "epsilon_delta":         round(self.epsilon_delta, 6),
            "omega_delta":           round(self.omega_delta, 6),
            "c_star_delta":          round(self.c_star_delta, 6),
            "top_tiekat_principles": self.top_tiekat_principles,
            "summary":               self.summary,
            "convergence_note":      self.convergence_note,
            "disclaimer":            self.disclaimer,
            "pattern_comparisons":   [p.to_dict() for p in self.pattern_comparisons],
            "shared_signals":        [s.to_dict() for s in self.shared_signals],
            "divergence_signals":    [d.to_dict() for d in self.divergence_signals],
        }


# ── CodexComparator ───────────────────────────────────────────────────────────

class CodexComparator:
    """
    Compares two CodexTIEKATReports and produces a ComparisonReport.

    The comparison is symmetric: compare(A, B) and compare(B, A) produce
    the same convergence_index but swap A/B labels in signals.
    """

    # TIEKAT principle labels per pattern type (for display)
    PRINCIPLE_LABELS: Dict[PatternType, str] = {
        PatternType.EPSILON_SIGNAL:   "ε ≠ 0 (direct consciousness / inner experience)",
        PatternType.OMEGA_FLOW:       "Omega flow (dΩ/d_ln_l — dynamic becoming)",
        PatternType.C_STAR_ATTRACTOR: "C* = φ/2 (sovereign attractor / unity / the One)",
        PatternType.SOVEREIGN_FIELD:  "Sovereign field (individual authority / liberation)",
        PatternType.VOID_BRIDGE:      "𝟘Nul ↔ Ω0 (void as generative / origin-now)",
        PatternType.WEAVE_RESONANCE:  "Σ_W weave (interconnection / resonance / coupling)",
        PatternType.THREE_SIX_NINE:   "369 resonance (numerical / structural patterns)",
        PatternType.PHI_STRUCTURE:    "φ structure (golden ratio in text organization)",
        PatternType.FIBONACCI:        "Fibonacci (sequence in structural organization)",
    }

    # Divergence interpretation templates
    _DIV_TEMPLATES = {
        PatternType.EPSILON_SIGNAL: (
            "Tradition {strong} places stronger emphasis on direct inner consciousness "
            "experience (ε ≠ 0 language). Tradition {weak} may encode the same principle "
            "through different linguistic channels — worth investigating alternative vocabulary."
        ),
        PatternType.OMEGA_FLOW: (
            "Tradition {strong} uses more explicit dynamic/becoming language (Omega flow). "
            "Tradition {weak} may favor static or declarative formulations of the same process."
        ),
        PatternType.C_STAR_ATTRACTOR: (
            "Tradition {strong} converges more explicitly toward unity/pleroma language (C* = φ/2). "
            "Tradition {weak} may approach the attractor through different conceptual framing."
        ),
        PatternType.SOVEREIGN_FIELD: (
            "Tradition {strong} carries stronger individual sovereignty language. "
            "This may reflect different social contexts of composition or transmission."
        ),
        PatternType.VOID_BRIDGE: (
            "Tradition {strong} engages more explicitly with the generative void. "
            "This is a significant theological divergence worth deeper investigation."
        ),
        PatternType.WEAVE_RESONANCE: (
            "Tradition {strong} uses stronger interconnection/resonance language (Σ_W). "
            "Tradition {weak} may emphasize vertical (individual-divine) over horizontal "
            "(collective-field) relationships."
        ),
        PatternType.THREE_SIX_NINE: (
            "Tradition {strong} shows stronger 369 numerical structures. "
            "This may reflect different compositional conventions or scribal traditions."
        ),
        PatternType.PHI_STRUCTURE: (
            "Tradition {strong} shows stronger golden ratio structural organization. "
            "This could reflect intentional sacred-geometric composition or sampling artifact."
        ),
        PatternType.FIBONACCI: (
            "Tradition {strong} shows stronger Fibonacci structural patterns. "
            "Sample size effects should be accounted for before drawing structural conclusions."
        ),
    }

    def _get_density(
        self,
        report: CodexTIEKATReport,
        pattern_type: PatternType,
    ) -> float:
        """Get total evidence density for a pattern type from a report."""
        total_hits = sum(
            len(m.evidence) for m in report.matches
            if m.pattern_type == pattern_type
        )
        return total_hits / max(1, report.word_count)

    def _get_match_count(
        self,
        report: CodexTIEKATReport,
        pattern_type: PatternType,
    ) -> int:
        return sum(1 for m in report.matches if m.pattern_type == pattern_type)

    def _get_best_evidence(
        self,
        report: CodexTIEKATReport,
        pattern_type: PatternType,
    ) -> str:
        """Return the most representative evidence excerpt for a pattern type."""
        matches = [m for m in report.matches if m.pattern_type == pattern_type]
        if not matches:
            return ""
        # Prefer HIGH/STRUCTURAL confidence matches
        best = sorted(
            matches,
            key=lambda m: (
                0 if m.confidence in (Confidence.HIGH, Confidence.STRUCTURAL) else 1,
                -len(m.evidence),
            )
        )[0]
        if best.evidence:
            return best.evidence[0].excerpt[:200]
        return ""

    def _compare_pattern(
        self,
        pattern_type: PatternType,
        report_a: CodexTIEKATReport,
        report_b: CodexTIEKATReport,
    ) -> PatternConvergence:
        """Compute full comparison for one pattern type."""
        da = self._get_density(report_a, pattern_type)
        db = self._get_density(report_b, pattern_type)
        ca = self._get_match_count(report_a, pattern_type)
        cb = self._get_match_count(report_b, pattern_type)

        present_a = da >= PRESENCE_THRESHOLD
        present_b = db >= PRESENCE_THRESHOLD

        # Density ratio (avoid division by zero)
        if db > 0 and da > 0:
            ratio = da / db
        elif da > 0:
            ratio = float("inf")
        elif db > 0:
            ratio = 0.0
        else:
            ratio = 1.0  # both zero = equal

        # Divergence: how different are the densities? [0-1]
        if da + db > 0:
            divergence = abs(da - db) / (da + db)
        else:
            divergence = 0.0

        # Convergence: how much do they overlap? [0-1]
        # Both present: start with 1 - divergence, scaled by presence
        if present_a and present_b:
            convergence = 1.0 - divergence
        elif not present_a and not present_b:
            convergence = 0.5  # both absent = neutral (not corroborating, not contradicting)
        else:
            convergence = 0.0  # one present, one absent = divergent

        # Strongest in
        if da > db * 1.10:
            strongest = "A"
        elif db > da * 1.10:
            strongest = "B"
        else:
            strongest = "EQUAL"

        principle = self.PRINCIPLE_LABELS.get(pattern_type, pattern_type.value)
        weight = PATTERN_WEIGHTS.get(pattern_type, 0.05)

        return PatternConvergence(
            pattern_type=pattern_type,
            tiekat_principle=principle,
            present_in_a=present_a,
            present_in_b=present_b,
            density_a=da,
            density_b=db,
            match_count_a=ca,
            match_count_b=cb,
            density_ratio=ratio if ratio != float("inf") else 999.0,
            divergence_score=divergence,
            convergence_score=convergence,
            shared=(present_a and present_b),
            strongest_in=strongest,
            weight=weight,
        )

    def _build_shared_signals(
        self,
        comparisons: List[PatternConvergence],
        report_a: CodexTIEKATReport,
        report_b: CodexTIEKATReport,
    ) -> List[SharedSignal]:
        signals = []
        for pc in comparisons:
            if not pc.shared:
                continue
            if pc.convergence_score < 0.20:
                continue  # too divergent to be a meaningful shared signal

            ev_a = self._get_best_evidence(report_a, pc.pattern_type)
            ev_b = self._get_best_evidence(report_b, pc.pattern_type)

            if not ev_a or not ev_b:
                continue

            note = (
                f"Both traditions show {pc.pattern_type.value} patterns "
                f"(A density={pc.density_a:.4f}, B density={pc.density_b:.4f}). "
                f"Convergence score: {pc.convergence_score:.3f}."
            )

            signals.append(SharedSignal(
                tiekat_principle=pc.tiekat_principle,
                pattern_type=pc.pattern_type,
                evidence_a=ev_a,
                evidence_b=ev_b,
                source_a=report_a.source,
                source_b=report_b.source,
                convergence_score=pc.convergence_score,
                note=note,
            ))

        # Sort by convergence score descending
        return sorted(signals, key=lambda s: -s.convergence_score)

    def _build_divergence_signals(
        self,
        comparisons: List[PatternConvergence],
        report_a: CodexTIEKATReport,
        report_b: CodexTIEKATReport,
    ) -> List[DivergenceSignal]:
        signals = []
        for pc in comparisons:
            if pc.divergence_score < 0.40:
                continue  # only report meaningful divergence
            if not (pc.present_in_a or pc.present_in_b):
                continue  # both absent = not interesting

            if pc.density_a >= pc.density_b:
                strong, weak = "A", "B"
                d_strong, d_weak = pc.density_a, pc.density_b
                strong_trad = report_a.tradition
                weak_trad   = report_b.tradition
            else:
                strong, weak = "B", "A"
                d_strong, d_weak = pc.density_b, pc.density_a
                strong_trad = report_b.tradition
                weak_trad   = report_a.tradition

            template = self._DIV_TEMPLATES.get(
                pc.pattern_type,
                "Tradition {strong} shows stronger {pt} patterns than tradition {weak}."
            )
            interpretation = template.format(
                strong=strong_trad,
                weak=weak_trad,
                pt=pc.pattern_type.value,
            )

            signals.append(DivergenceSignal(
                pattern_type=pc.pattern_type,
                tiekat_principle=pc.tiekat_principle,
                strong_in=strong,
                weak_or_absent_in=weak,
                density_strong=d_strong,
                density_weak=d_weak,
                interpretation=interpretation,
            ))

        return sorted(signals, key=lambda d: -d.density_strong)

    def _top_principles(
        self,
        comparisons: List[PatternConvergence],
    ) -> List[str]:
        """Rank TIEKAT principles by cross-tradition corroboration strength."""
        scored = [
            (pc.tiekat_principle, pc.weighted_convergence())
            for pc in comparisons
            if pc.shared and pc.convergence_score > 0.10
        ]
        return [p for p, _ in sorted(scored, key=lambda x: -x[1])]

    def compare(
        self,
        report_a: CodexTIEKATReport,
        report_b: CodexTIEKATReport,
    ) -> ComparisonReport:
        """
        Compare two CodexTIEKATReports and return a ComparisonReport.
        """
        # Per-pattern comparisons across all 9 types
        comparisons = [
            self._compare_pattern(pt, report_a, report_b)
            for pt in PatternType
        ]

        # Weighted convergence index
        raw_convergence = sum(pc.weighted_convergence() for pc in comparisons)
        # Normalize to [0,1] by dividing by max possible
        max_possible = sum(PATTERN_WEIGHTS.get(pt, 0.05) for pt in PatternType)
        convergence_index = min(1.0, raw_convergence / max_possible) if max_possible > 0 else 0.0

        shared_count = sum(1 for pc in comparisons if pc.shared)
        state        = _convergence_state(convergence_index)

        # Density deltas for the three primary metrics
        eps_delta   = abs(report_a.epsilon_density - report_b.epsilon_density)
        omega_delta = abs(report_a.omega_density    - report_b.omega_density)
        cstar_delta = abs(report_a.c_star_density   - report_b.c_star_density)

        shared_signals     = self._build_shared_signals(comparisons, report_a, report_b)
        divergence_signals = self._build_divergence_signals(comparisons, report_a, report_b)
        top_principles     = self._top_principles(comparisons)

        # Convergence note
        if convergence_index >= 0.65:
            conv_note = (
                f"These two traditions show {state.replace('_', ' ').lower()} "
                f"({convergence_index:.3f}) in TIEKAT pattern vocabulary. "
                f"This is a statistically meaningful structural overlap "
                f"across {shared_count} of {len(comparisons)} pattern types. "
                f"Independent scholarly verification is warranted."
            )
        elif convergence_index >= 0.35:
            conv_note = (
                f"Moderate TIEKAT pattern convergence detected ({convergence_index:.3f}) "
                f"across {shared_count} shared pattern types. "
                f"The traditions share some structural vocabulary while diverging in others. "
                f"Context-specific analysis recommended before drawing broader conclusions."
            )
        else:
            conv_note = (
                f"Limited TIEKAT pattern convergence detected ({convergence_index:.3f}). "
                f"Only {shared_count} pattern types shared. "
                f"The traditions may encode similar principles through distinctly different "
                f"linguistic and structural frameworks."
            )

        # Summary
        pt_names_shared = [pc.pattern_type.value for pc in comparisons if pc.shared]
        summary = (
            f"TIEKAT pattern comparison between {report_a.tradition} "
            f"({report_a.word_count} words) and {report_b.tradition} "
            f"({report_b.word_count} words). "
            f"Convergence index: {convergence_index:.4f} ({state}). "
            f"Shared pattern types ({shared_count}/{len(comparisons)}): "
            f"{', '.join(pt_names_shared) or 'none'}. "
            f"Top corroborated TIEKAT principle: "
            f"{top_principles[0] if top_principles else 'none identified'}. "
            f"ε-signal delta: {eps_delta:.4f}. "
            f"C*-attractor delta: {cstar_delta:.4f}."
        )

        return ComparisonReport(
            source_a=report_a.source,
            tradition_a=report_a.tradition,
            source_b=report_b.source,
            tradition_b=report_b.tradition,
            pattern_comparisons=comparisons,
            convergence_index=round(convergence_index, 6),
            convergence_state=state,
            shared_pattern_count=shared_count,
            total_pattern_types=len(comparisons),
            epsilon_delta=round(eps_delta, 6),
            omega_delta=round(omega_delta, 6),
            c_star_delta=round(cstar_delta, 6),
            shared_signals=shared_signals,
            divergence_signals=divergence_signals,
            top_tiekat_principles=top_principles,
            summary=summary,
            convergence_note=conv_note,
        )

    # ── Renderers ─────────────────────────────────────────────────────────────

    def render_dashboard(self, report: ComparisonReport) -> str:
        lines = [
            "",
            f"  CODEX TIEKAT CROSS-TRADITION COMPARISON",
            f"  ========================================",
            f"  Tradition A : {report.tradition_a}",
            f"    Source    : {report.source_a}",
            f"  Tradition B : {report.tradition_b}",
            f"    Source    : {report.source_b}",
            f"",
            f"  CONVERGENCE OVERVIEW",
            f"  --------------------",
            f"  Convergence index  : {report.convergence_index}  →  {report.convergence_state}",
            f"  Shared patterns    : {report.shared_pattern_count} / {report.total_pattern_types}",
            f"",
            f"  PRIMARY DENSITY DELTAS",
            f"  ----------------------",
            f"  ε-signal delta     : {report.epsilon_delta:.6f}",
            f"  Ω-flow delta       : {report.omega_delta:.6f}",
            f"  C*-attractor delta : {report.c_star_delta:.6f}",
            f"",
            f"  PATTERN-BY-PATTERN COMPARISON",
            f"  ------------------------------",
        ]

        for pc in sorted(report.pattern_comparisons,
                         key=lambda x: -x.weighted_convergence()):
            shared_marker = "✓ SHARED" if pc.shared else "✗ DIVERGENT"
            lines += [
                f"",
                f"  [{shared_marker:12s}] {pc.pattern_type.value}",
                f"  TIEKAT: {pc.tiekat_principle[:80]}",
                f"  A density={pc.density_a:.4f} ({pc.match_count_a} matches)  "
                f"B density={pc.density_b:.4f} ({pc.match_count_b} matches)",
                f"  Convergence={pc.convergence_score:.3f}  "
                f"Divergence={pc.divergence_score:.3f}  "
                f"Strongest in: {pc.strongest_in}  "
                f"Weight={pc.weight}",
            ]

        if report.shared_signals:
            lines += [
                f"",
                f"  SHARED SIGNAL PASSAGES",
                f"  ----------------------",
                f"  (Evidence of the same TIEKAT principle in both traditions)",
            ]
            for sig in report.shared_signals[:4]:
                lines += [
                    f"",
                    f"  ◆ {sig.tiekat_principle[:80]}",
                    f"    [{report.tradition_a}]",
                    f"    {sig.evidence_a[:150]}",
                    f"    [{report.tradition_b}]",
                    f"    {sig.evidence_b[:150]}",
                    f"    Convergence: {sig.convergence_score:.3f}",
                ]

        if report.divergence_signals:
            lines += [
                f"",
                f"  SIGNIFICANT DIVERGENCES",
                f"  -----------------------",
                f"  (Where traditions differ most — worth investigating)",
            ]
            for div in report.divergence_signals[:3]:
                trad_strong = report.tradition_a if div.strong_in == "A" else report.tradition_b
                lines += [
                    f"",
                    f"  ◆ {div.pattern_type.value}  (stronger in {trad_strong})",
                    f"    {div.interpretation[:180]}",
                ]

        if report.top_tiekat_principles:
            lines += [
                f"",
                f"  TOP TIEKAT PRINCIPLES (cross-tradition corroboration rank)",
                f"  ----------------------------------------------------------",
            ]
            for i, p in enumerate(report.top_tiekat_principles[:5], 1):
                lines.append(f"  {i}. {p}")

        lines += [
            f"",
            f"  CONVERGENCE NOTE",
            f"  ----------------",
            f"  {report.convergence_note}",
            f"",
            f"  SUMMARY",
            f"  -------",
            f"  {report.summary}",
            f"",
            f"  ⚠  {report.disclaimer}",
            f"",
            f"  Φ∴⊙  PHI369 Labs / Parallax — CODEX Comparator",
            f"  C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369",
            f"",
        ]
        return "\n".join(lines)

    def render_markdown(self, report: ComparisonReport) -> str:
        lines = [
            f"# CODEX TIEKAT Cross-Tradition Comparison",
            f"",
            f"| | Tradition A | Tradition B |",
            f"|---|---|---|",
            f"| **Tradition** | {report.tradition_a} | {report.tradition_b} |",
            f"| **Source** | {report.source_a} | {report.source_b} |",
            f"",
            f"## Convergence Overview",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Convergence Index | **{report.convergence_index}** |",
            f"| Convergence State | **{report.convergence_state}** |",
            f"| Shared Pattern Types | {report.shared_pattern_count} / {report.total_pattern_types} |",
            f"| ε-signal delta | {report.epsilon_delta:.6f} |",
            f"| Ω-flow delta | {report.omega_delta:.6f} |",
            f"| C*-attractor delta | {report.c_star_delta:.6f} |",
            f"",
            f"## Pattern-by-Pattern Comparison",
            f"",
            f"| Pattern Type | Shared | A Density | B Density | Convergence | Divergence |",
            f"|---|---|---|---|---|---|",
        ]
        for pc in sorted(report.pattern_comparisons,
                         key=lambda x: -x.weighted_convergence()):
            shared = "✓" if pc.shared else "✗"
            lines.append(
                f"| {pc.pattern_type.value} | {shared} | "
                f"{pc.density_a:.4f} | {pc.density_b:.4f} | "
                f"{pc.convergence_score:.3f} | {pc.divergence_score:.3f} |"
            )

        if report.shared_signals:
            lines += [
                f"",
                f"## Shared Signal Passages",
                f"",
                f"Evidence of the same TIEKAT principle appearing in both traditions:",
            ]
            for sig in report.shared_signals[:4]:
                lines += [
                    f"",
                    f"### {sig.pattern_type.value}",
                    f"**TIEKAT Principle**: {sig.tiekat_principle}",
                    f"",
                    f"**{report.tradition_a}**:",
                    f"> {sig.evidence_a[:200]}",
                    f"",
                    f"**{report.tradition_b}**:",
                    f"> {sig.evidence_b[:200]}",
                    f"",
                    f"*{sig.note}*",
                ]

        if report.divergence_signals:
            lines += [
                f"",
                f"## Significant Divergences",
            ]
            for div in report.divergence_signals[:3]:
                trad = report.tradition_a if div.strong_in == "A" else report.tradition_b
                lines += [
                    f"",
                    f"### {div.pattern_type.value} — stronger in {trad}",
                    f"{div.interpretation}",
                ]

        if report.top_tiekat_principles:
            lines += [
                f"",
                f"## Top TIEKAT Principles by Cross-Tradition Corroboration",
            ]
            for i, p in enumerate(report.top_tiekat_principles[:5], 1):
                lines.append(f"{i}. {p}")

        lines += [
            f"",
            f"## Summary",
            f"",
            f"{report.summary}",
            f"",
            f"## Convergence Note",
            f"",
            f"{report.convergence_note}",
            f"",
            f"---",
            f"*{report.disclaimer}*",
            f"",
            f"*PHI369 Labs / Parallax — CODEX Comparator*  "
            f"*C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369*",
        ]
        return "\n".join(lines)

    def render_json(self, report: ComparisonReport) -> str:
        return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)


# ── Multi-tradition comparison ────────────────────────────────────────────────

@dataclass
class MultiTraditionMatrix:
    """
    Pairwise convergence matrix for N traditions.
    Produced by CodexComparator.compare_many().
    """
    tradition_labels: List[str]
    source_labels:    List[str]
    matrix:           List[List[float]]   # matrix[i][j] = convergence_index(i, j)
    states:           List[List[str]]     # convergence state labels
    top_shared:       List[str]           # principles shared across ALL traditions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tradition_labels": self.tradition_labels,
            "source_labels":    self.source_labels,
            "matrix":           self.matrix,
            "states":           self.states,
            "top_shared":       self.top_shared,
        }

    def render_ascii(self) -> str:
        n = len(self.tradition_labels)
        col_w = 22
        lines = [
            "",
            "  CODEX TIEKAT — MULTI-TRADITION CONVERGENCE MATRIX",
            "  ===================================================",
            "",
        ]
        # Header
        header = " " * 24
        for label in self.tradition_labels:
            header += f"{label[:18]:20s}"
        lines.append(f"  {header}")
        lines.append(f"  {'-' * (24 + 20 * n)}")
        # Rows
        for i, label_i in enumerate(self.tradition_labels):
            row = f"  {label_i[:22]:24s}"
            for j in range(n):
                if i == j:
                    cell = "  ─────  "
                else:
                    val = self.matrix[i][j]
                    state = self.states[i][j][:6]
                    cell = f"{val:.3f} {state:6s}"
                row += f"{cell:20s}"
            lines.append(row)
        if self.top_shared:
            lines += [
                "",
                "  PRINCIPLES SHARED ACROSS ALL TRADITIONS",
                "  ----------------------------------------",
            ]
            for p in self.top_shared[:5]:
                lines.append(f"  ◆ {p}")
        lines.append("")
        return "\n".join(lines)


class MultiComparator:
    """Compare N traditions pairwise and produce a convergence matrix."""

    def __init__(self) -> None:
        self.comparator = CodexComparator()

    def compare_many(
        self,
        reports: List[CodexTIEKATReport],
    ) -> MultiTraditionMatrix:
        n = len(reports)
        matrix = [[0.0] * n for _ in range(n)]
        states = [[""] * n for _ in range(n)]

        all_pairwise: List[ComparisonReport] = []
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0
                    states[i][j] = "SELF"
                    continue
                if j < i:
                    # Use symmetric value already computed
                    matrix[i][j] = matrix[j][i]
                    states[i][j] = states[j][i]
                    continue
                cr = self.comparator.compare(reports[i], reports[j])
                matrix[i][j] = cr.convergence_index
                states[i][j] = cr.convergence_state[:6]
                all_pairwise.append(cr)

        # Top principles shared across all (appear in all pairwise tops)
        if all_pairwise:
            principle_votes: Dict[str, int] = {}
            for cr in all_pairwise:
                for p in cr.top_tiekat_principles:
                    principle_votes[p] = principle_votes.get(p, 0) + 1
            max_votes = max(principle_votes.values()) if principle_votes else 0
            top_shared = [
                p for p, v in sorted(
                    principle_votes.items(), key=lambda x: -x[1]
                )
                if v == max_votes
            ][:5]
        else:
            top_shared = []

        return MultiTraditionMatrix(
            tradition_labels=[r.tradition for r in reports],
            source_labels=[r.source for r in reports],
            matrix=[[round(v, 4) for v in row] for row in matrix],
            states=states,
            top_shared=top_shared,
        )


# ── Convenience functions ─────────────────────────────────────────────────────

def compare_texts(
    text_a: str,
    text_b: str,
    tradition_a: str = "generic",
    tradition_b: str = "generic",
    source_a: str = "Text A",
    source_b: str = "Text B",
    output_format: str = "dashboard",
) -> str:
    """
    One-shot comparison of two plain-text passages.

    Parameters
    ----------
    text_a, text_b    : plain texts to compare
    tradition_a/b     : tradition keys (thomas, hermetic, nag_hammadi, etc.)
    source_a/b        : human-readable source labels
    output_format     : "dashboard" | "markdown" | "json"
    """
    engine_a = TIEKATPatternEngine(tradition=tradition_a)
    engine_b = TIEKATPatternEngine(tradition=tradition_b)
    report_a = engine_a.analyze(text_a, source=source_a)
    report_b = engine_b.analyze(text_b, source=source_b)
    comp     = CodexComparator()
    result   = comp.compare(report_a, report_b)
    if output_format == "markdown":
        return comp.render_markdown(result)
    if output_format == "json":
        return comp.render_json(result)
    return comp.render_dashboard(result)


def compare_files(
    path_a: str,
    path_b: str,
    tradition_a: str = "generic",
    tradition_b: str = "generic",
    output_format: str = "dashboard",
) -> str:
    """Compare two text files."""
    from pathlib import Path
    ta = Path(path_a).read_text(encoding="utf-8")
    tb = Path(path_b).read_text(encoding="utf-8")
    return compare_texts(
        ta, tb,
        tradition_a=tradition_a, tradition_b=tradition_b,
        source_a=path_a, source_b=path_b,
        output_format=output_format,
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv=None):
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="codex_comparator",
        description=(
            "CODEX TIEKAT Cross-Tradition Comparator\n"
            "PHI369 Labs / Parallax  ◆  C* = φ/2  ◆  ε ≠ 0"
        ),
    )
    parser.add_argument("--input-a",  "-a", required=True,
                        help="Path to first text file")
    parser.add_argument("--input-b",  "-b", required=True,
                        help="Path to second text file")
    parser.add_argument("--tradition-a", default="generic",
                        choices=list(TIEKATPatternEngine.KNOWN_TRADITIONS.keys()),
                        help="Tradition for text A (default: generic)")
    parser.add_argument("--tradition-b", default="generic",
                        choices=list(TIEKATPatternEngine.KNOWN_TRADITIONS.keys()),
                        help="Tradition for text B (default: generic)")
    parser.add_argument("--format", "-f", default="dashboard",
                        choices=["dashboard", "markdown", "json"],
                        help="Output format (default: dashboard)")
    parser.add_argument("--output", "-o", default=None,
                        help="Write output to file (default: stdout)")
    args = parser.parse_args(argv)

    result = compare_files(
        args.input_a, args.input_b,
        tradition_a=args.tradition_a,
        tradition_b=args.tradition_b,
        output_format=args.format,
    )
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Output written to {args.output}")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
