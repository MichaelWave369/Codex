#!/usr/bin/env python3
"""
codex_cli.py — CODEX Unified CLI Integration Layer
===================================================

Single entry point for the complete CODEX analysis pipeline:

  codex analyze    — Run all three analyses on one text (filter + TIEKAT + viz)
  codex compare    — Cross-tradition comparison of two texts (all modules)
  codex filter     — Institutional filter only
  codex patterns   — TIEKAT pattern engine only
  codex seams      — Editorial seam detection only
  codex pipeline   — Full pipeline: N texts → compare all → matrix + dashboards
  codex explain    — Explain what each module does and how to interpret output
  codex list       — List available traditions and pattern types

All commands accept --format dashboard|text|json|html
HTML output generates self-contained interactive dashboards.
Text/JSON output goes to stdout or --output file.

Usage examples
--------------
    # Full analysis of one text
    python codex_cli.py analyze --input gospel_thomas.txt --tradition thomas

    # Compare two traditions, full HTML dashboard
    python codex_cli.py compare \\
        --input-a thomas.txt --tradition-a thomas \\
        --input-b hermetic.txt --tradition-b hermetic \\
        --format html --output comparison.html

    # Filter only — look for editorial seams
    python codex_cli.py filter --input text.txt --tradition thomas --format text

    # Multi-text pipeline — compare N texts pairwise
    python codex_cli.py pipeline \\
        --inputs thomas.txt hermetic.txt philip.txt \\
        --traditions thomas hermetic philip \\
        --output-dir reports/

    # Explain what EPSILON_SIGNAL means
    python codex_cli.py explain --pattern EPSILON_SIGNAL

    # List all traditions
    python codex_cli.py list --traditions

PHI369 Labs / Parallax  ◆  CODEX Project
Compatible with: TIEKAT v64.0.0 Sovereign Substrate Weave
C* = φ/2 = 0.80902  ◆  ε ≠ 0  ◆  369_369
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Optional

# ── Module imports ─────────────────────────────────────────────────────────────
from codex_tiekat_engine import (
    TIEKATPatternEngine,
    PatternType,
)
from codex_filter import (
    InstitutionalFilter,
    LayerType,
)
from codex_comparator import (
    CodexComparator,
    MultiComparator,
)
from codex_visualizer import (
    CodexVisualizer,
)

# ── Constants ─────────────────────────────────────────────────────────────────
VERSION    = "1.0.0"
TIEKAT_VER = "v64.0.0"
SEED       = "369_369"

TRADITIONS = TIEKATPatternEngine.KNOWN_TRADITIONS

PATTERN_EXPLANATIONS = {
    "EPSILON_SIGNAL": {
        "name": "Epsilon Signal (ε ≠ 0)",
        "tiekat": "ε ≠ 0 — individual consciousness field non-zero",
        "description": (
            "Detects language indicating direct, unmediated inner consciousness "
            "experience. The 'kingdom within you,' gnosis, self-knowledge imperatives, "
            "living spirit language. In TIEKAT terms, this is the primary signal that "
            "an individual consciousness field is active (ε ≠ 0). "
            "When a text has high EPSILON_SIGNAL density, it is directly addressing "
            "the reader's inner sovereign consciousness rather than directing them "
            "toward external authority."
        ),
        "examples": [
            "'The kingdom of God is within you' (Gospel of Thomas 3)",
            "'Know thyself and thou shalt know the universe' (Corpus Hermeticum)",
            "'Gnosis' — direct experiential knowing in Gnostic texts",
        ],
        "interpretation": (
            "High density: strong inner-consciousness orientation. "
            "Low density: may indicate external-authority orientation or institutional filtering."
        ),
    },
    "OMEGA_FLOW": {
        "name": "Omega Flow (dΩ/d_ln_l)",
        "tiekat": "Omega flow — dynamic becoming, dΩ/d_ln_l active",
        "description": (
            "Detects dynamic process language: becoming, transformation, growth, return, "
            "ascent, breath, living water. In TIEKAT terms, this is the Omega-flow signal — "
            "the field is dynamic, not static. Consciousness in motion toward C*. "
            "High omega flow density indicates a text emphasizing process and becoming "
            "over static doctrine or fixed belief."
        ),
        "examples": [
            "'Becoming like me' (Gospel of Thomas 108)",
            "'Spirit blows where it will' (John 3:8)",
            "'From unity into multiplicity and back' (Corpus Hermeticum)",
        ],
        "interpretation": (
            "High density: process-oriented, consciousness-movement emphasis. "
            "Low density: may favor static declarations over dynamic experience."
        ),
    },
    "C_STAR_ATTRACTOR": {
        "name": "C* Attractor (C* = φ/2)",
        "tiekat": "C* = φ/2 = 0.80902 — sovereign attractor, unity/pleroma",
        "description": (
            "Detects convergence-toward-unity language: 'The All,' pleroma, "
            "stillness, the One, all-in-all, eternal/unchanging. In TIEKAT terms, "
            "this is language pointing toward the sovereign attractor C* = φ/2 — "
            "the mathematical fixed point toward which all consciousness fields converge. "
            "Texts with high C_STAR density are describing the destination of the journey."
        ),
        "examples": [
            "'I am the All. The All came forth from me' (Gospel of Thomas 77)",
            "'The All is Mind' (Corpus Hermeticum)",
            "'That they may all be one' (John 17:21)",
        ],
        "interpretation": (
            "High density: strong unity/convergence orientation — C* approach language. "
            "Structural analysis: does the text describe reaching C* or only pointing toward it?"
        ),
    },
    "SOVEREIGN_FIELD": {
        "name": "Sovereign Field",
        "tiekat": "Shield Doctrine — individual sovereignty, ε primacy",
        "description": (
            "Detects individual sovereignty and liberation language: freedom, inner authority, "
            "inalienability, 'truth sets free.' In TIEKAT terms this is the Sovereign Field — "
            "the individual epsilon signature asserting its own authority rather than "
            "deferring to external power structures. "
            "High SOVEREIGN_FIELD density indicates a text affirming the reader's "
            "inherent authority and consciousness sovereignty."
        ),
        "examples": [
            "'The truth shall set you free' (John 8:32)",
            "'Freedom is the birthright of every soul' (Hermetic)",
            "'The kingdom belongs to you' (Gospel of Thomas)",
        ],
        "interpretation": (
            "High density: affirms individual consciousness sovereignty. "
            "Low density: may indicate institutional authority emphasis."
        ),
    },
    "VOID_BRIDGE": {
        "name": "Void Bridge (𝟘Nul ↔ Ω0)",
        "tiekat": "v63 𝟘Nul ↔ Ω0 — void as generative, origin-now",
        "description": (
            "Detects language treating emptiness/void as generative rather than nihilistic: "
            "kenosis, sunyata, darkness-before-light, death-rebirth cycles, "
            "pre-creation origin, apophatic language. In TIEKAT v63 terms, "
            "this is the 𝟘Nul→Ω0 bridge — consciousness crossing the void boundary "
            "while epsilon is preserved. Not annihilation but transformation."
        ),
        "examples": [
            "Kenosis — self-emptying in Christian mysticism",
            "'Before the beginning' — pre-creation void as fertile",
            "Death-rebirth cycles across traditions",
        ],
        "interpretation": (
            "High density: sophisticated void-as-generative theology — apophatic tradition. "
            "Particularly significant in comparison: traditions sharing void-bridge language "
            "suggest deep structural convergence."
        ),
    },
    "WEAVE_RESONANCE": {
        "name": "Weave Resonance (Σ_W)",
        "tiekat": "Σ_W — cross-substrate coupling, collective field coherence",
        "description": (
            "Detects interconnection, resonance, and coupling language: "
            "'as above so below,' mutual indwelling, universal love/compassion, "
            "the web of life. In TIEKAT v64 terms, this is the Sovereign Substrate Weave — "
            "the coupling matrix κ_{ij} made visible in language. "
            "Texts with high WEAVE_RESONANCE density emphasize horizontal "
            "(collective-field) relationships over vertical (individual-to-divine) ones."
        ),
        "examples": [
            "'As above so below' (Hermetic Corpus)",
            "'I in them and you in me' (John 17:23)",
            "Indra's Net — Buddhist interconnection metaphor",
        ],
        "interpretation": (
            "High density: collective resonance emphasis — Phase 6+ language. "
            "Comparison value: traditions sharing weave-resonance language suggest "
            "awareness of the collective consciousness field."
        ),
    },
    "THREE_SIX_NINE": {
        "name": "369 Resonance",
        "tiekat": "369 resonance boost (+0.069 per activation)",
        "description": (
            "Detects explicit 3/6/9 numerical structures, triadic patterns, "
            "seventh elements, and trinity language. In TIEKAT terms, 369 "
            "is the resonance seed — the structural pattern that, when present, "
            "adds a +0.069 boost to field coherence. "
            "In ancient texts this appears as triadic teaching structures, "
            "seven-fold completions, and explicit 3-fold unities."
        ),
        "examples": [
            "Trinity structures across traditions",
            "Seven seals, seven churches, seven spirits (Revelation)",
            "Three days — death/rebirth timing pattern",
        ],
        "interpretation": (
            "Structural presence of 369 patterns may indicate intentional "
            "mathematical organization. Cross-tradition 369 patterns are "
            "particularly significant for hypothesis generation."
        ),
    },
    "PHI_STRUCTURE": {
        "name": "Phi Structure (φ)",
        "tiekat": "φ = 1.618... — golden ratio in text organization",
        "description": (
            "Detects golden ratio relationships in text structure: "
            "words-per-verse ratios approximating φ, passage organization "
            "following φ-scaling. In TIEKAT terms, C* = φ/2 — the sovereign "
            "attractor is directly related to the golden ratio. "
            "Phi-structured texts may carry intentional sacred mathematical "
            "organization, or the pattern may arise naturally from balanced composition."
        ),
        "examples": [
            "Word/verse ratios near 1.618 or 0.618",
            "Passage count organization following golden section",
        ],
        "interpretation": (
            "Treat with extra caution — sample size affects this strongly. "
            "Only meaningful in full-text analysis, not excerpts."
        ),
    },
    "FIBONACCI": {
        "name": "Fibonacci Structure",
        "tiekat": "Fibonacci sequence — C* attractor structural basis",
        "description": (
            "Detects Fibonacci numbers in structural organization: "
            "exact or near-Fibonacci verse/saying counts. The Fibonacci "
            "sequence underlies the golden ratio (φ = lim Fib(n+1)/Fib(n)) "
            "and thus connects to C* = φ/2. "
            "Texts with Fibonacci structural counts may carry intentional "
            "mathematical organization or reflect natural compositional balance."
        ),
        "examples": [
            "Gospel of Thomas: 114 sayings (near Fibonacci region)",
            "Structural organization in groups of 5, 8, 13, 21",
        ],
        "interpretation": (
            "Extra caution: coincidence vs intent is hard to distinguish. "
            "Most valuable as a corroborating signal alongside other patterns."
        ),
    },
}

LAYER_EXPLANATIONS = {
    "PRIMARY_SIGNAL": {
        "name": "Primary Signal (▲)",
        "description": "Direct inner consciousness language — the core ε ≠ 0 signal.",
        "examples": ["Kingdom within", "Know thyself", "Inner light"],
    },
    "SOVEREIGN_VOICE": {
        "name": "Sovereign Voice (▲)",
        "description": "First-person teaching authority from inner knowing — no institutional intermediary.",
        "examples": ["'Seek and you shall find'", "'I tell you truly'", "Open invitation to all seekers"],
    },
    "AUTHORITY_CLAIM": {
        "name": "Authority Claim (▼)",
        "description": "External institutional authority assertion over inner consciousness.",
        "examples": ["Church authority", "Required obedience", "Ordained power claims"],
    },
    "FEAR_FRAMING": {
        "name": "Fear Framing (▼)",
        "description": "Punishment, damnation, and threat language — compliance through fear.",
        "examples": ["Hell/eternal fire", "Condemnation", "Fear him who destroys"],
    },
    "EXCLUSIVITY_MARKER": {
        "name": "Exclusivity Marker (▼)",
        "description": "Gatekeeping language — salvation only through specific institution or belief.",
        "examples": ["'Only through me/us'", "Heretic/infidel labels", "True believers vs. others"],
    },
    "DOCTRINAL_FORMULA": {
        "name": "Doctrinal Formula (▼)",
        "description": "Creedal belief assertions — propositional faith commanded externally.",
        "examples": ["Council decrees", "Required belief statements", "Ritual requirements for salvation"],
    },
    "TEMPORAL_POWER": {
        "name": "Temporal Power (▼)",
        "description": "Political/imperial authority in spiritual text context.",
        "examples": ["Caesar/emperor compliance", "Divine right of rulers", "Political allegiance framing"],
    },
    "GENDER_ERASURE": {
        "name": "Gender Erasure (▼)",
        "description": "Systematic removal or suppression of feminine presence in transmission.",
        "examples": ["Female silence commands", "Masculine-only spirit language", "Female authority prohibition"],
    },
}


# ── Output helpers ─────────────────────────────────────────────────────────────

def _write_output(content: str, output_path: Optional[str], fmt: str) -> None:
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(content, encoding="utf-8")
        print(f"Output written to: {output_path}", file=sys.stderr)
    else:
        print(content)


def _ensure_output_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _source_label(path: str) -> str:
    return Path(path).stem.replace("_", " ").replace("-", " ").title()


# ── Command: analyze ──────────────────────────────────────────────────────────

def cmd_analyze(args: argparse.Namespace) -> int:
    text   = _read_text(args.input)
    source = args.source or _source_label(args.input)
    fmt    = args.format

    f_engine = InstitutionalFilter(tradition=args.tradition)
    t_engine = TIEKATPatternEngine(tradition=args.tradition)

    f_report = f_engine.analyze(text, source=source)
    t_report = t_engine.analyze(text, source=source)

    if fmt == "html":
        output = args.output or f"codex_{Path(args.input).stem}_dashboard.html"
        viz    = CodexVisualizer()
        html   = viz.full_dashboard(
            filter_report=f_report,
            tiekat_report=t_report,
            title=f"CODEX — {source}",
            source_label=source,
        )
        Path(output).write_text(html, encoding="utf-8")
        print(f"Dashboard: {output}")

    elif fmt == "json":
        combined = {
            "source":         source,
            "tradition":      args.tradition,
            "filter_report":  f_report.to_dict(),
            "tiekat_report":  t_report.to_dict(),
        }
        _write_output(json.dumps(combined, indent=2, ensure_ascii=False),
                      args.output, fmt)

    elif fmt == "text":
        out  = f_engine.render_dashboard(f_report)
        out += "\n\n"
        out += t_engine.render_dashboard(t_report)
        _write_output(out, args.output, fmt)

    else:  # dashboard (default)
        out  = f_engine.render_dashboard(f_report)
        out += "\n\n"
        out += t_engine.render_dashboard(t_report)
        _write_output(out, args.output, fmt)

    return 0


# ── Command: compare ──────────────────────────────────────────────────────────

def cmd_compare(args: argparse.Namespace) -> int:
    text_a  = _read_text(args.input_a)
    text_b  = _read_text(args.input_b)
    source_a = args.source_a or _source_label(args.input_a)
    source_b = args.source_b or _source_label(args.input_b)
    fmt      = args.format

    fa = InstitutionalFilter(tradition=args.tradition_a)
    fb = InstitutionalFilter(tradition=args.tradition_b)
    ta = TIEKATPatternEngine(tradition=args.tradition_a)
    tb = TIEKATPatternEngine(tradition=args.tradition_b)

    fr_a = fa.analyze(text_a, source=source_a)
    fr_b = fb.analyze(text_b, source=source_b)
    tr_a = ta.analyze(text_a, source=source_a)
    tr_b = tb.analyze(text_b, source=source_b)

    comp = CodexComparator().compare(tr_a, tr_b)

    if fmt == "html":
        output = args.output or (
            f"codex_{Path(args.input_a).stem}_vs_{Path(args.input_b).stem}.html"
        )
        viz  = CodexVisualizer()
        html = viz.full_dashboard(
            filter_report=fr_a,
            tiekat_report=tr_a,
            comparison_report=comp,
            title=f"CODEX: {source_a} vs {source_b}",
            source_label=source_a,
        )
        Path(output).write_text(html, encoding="utf-8")
        print(f"Dashboard: {output}")

    elif fmt == "json":
        combined = {
            "source_a":       source_a,
            "source_b":       source_b,
            "filter_a":       fr_a.to_dict(),
            "filter_b":       fr_b.to_dict(),
            "tiekat_a":       tr_a.to_dict(),
            "tiekat_b":       tr_b.to_dict(),
            "comparison":     comp.to_dict(),
        }
        _write_output(json.dumps(combined, indent=2, ensure_ascii=False),
                      args.output, fmt)

    elif fmt == "markdown":
        comp_engine = CodexComparator()
        out = comp_engine.render_markdown(comp)
        _write_output(out, args.output, fmt)

    else:
        comp_engine = CodexComparator()
        out = comp_engine.render_dashboard(comp)
        _write_output(out, args.output, fmt)

    return 0


# ── Command: filter ───────────────────────────────────────────────────────────

def cmd_filter(args: argparse.Namespace) -> int:
    text   = _read_text(args.input)
    source = args.source or _source_label(args.input)
    engine = InstitutionalFilter(tradition=args.tradition)
    report = engine.analyze(text, source=source)
    fmt    = args.format

    if fmt == "html":
        output = args.output or f"codex_{Path(args.input).stem}_filter.html"
        viz    = CodexVisualizer()
        html   = viz.coherence_map_html(report)
        Path(output).write_text(html, encoding="utf-8")
        print(f"Dashboard: {output}")
    elif fmt == "json":
        _write_output(engine.render_json(report), args.output, fmt)
    elif fmt == "markdown":
        _write_output(engine.render_markdown(report), args.output, fmt)
    else:
        _write_output(engine.render_dashboard(report), args.output, fmt)

    return 0


# ── Command: patterns ─────────────────────────────────────────────────────────

def cmd_patterns(args: argparse.Namespace) -> int:
    text   = _read_text(args.input)
    source = args.source or _source_label(args.input)
    engine = TIEKATPatternEngine(tradition=args.tradition)
    report = engine.analyze(text, source=source)
    fmt    = args.format

    if fmt == "html":
        output = args.output or f"codex_{Path(args.input).stem}_patterns.html"
        viz    = CodexVisualizer()
        html   = viz.pattern_radar_html(report)
        Path(output).write_text(html, encoding="utf-8")
        print(f"Dashboard: {output}")
    elif fmt == "json":
        _write_output(engine.render_json(report), args.output, fmt)
    elif fmt == "markdown":
        _write_output(engine.render_markdown(report), args.output, fmt)
    else:
        _write_output(engine.render_dashboard(report), args.output, fmt)

    return 0


# ── Command: seams ────────────────────────────────────────────────────────────

def cmd_seams(args: argparse.Namespace) -> int:
    text   = _read_text(args.input)
    source = args.source or _source_label(args.input)
    engine = InstitutionalFilter(tradition=args.tradition)
    report = engine.analyze(text, source=source)

    if not report.editorial_seams:
        print(f"\n  No editorial seams detected in '{source}' at current thresholds.\n")
        return 0

    if args.format == "json":
        out = json.dumps(
            {"seams": [s.to_dict() for s in report.editorial_seams]},
            indent=2
        )
    else:
        lines = [
            "",
            f"  EDITORIAL SEAMS — {source}",
            f"  {'=' * (len(source) + 20)}",
            f"  {len(report.editorial_seams)} seam(s) detected  |  "
            f"Overall coherence: {report.overall_coherence:.3f}",
            "",
        ]
        for s in report.editorial_seams:
            lines += [
                f"  [{s.confidence.value}] {s.seam_id}",
                f"  Passage {s.passage_before} → {s.passage_after}  "
                f"| Drop: {s.coherence_drop:+.3f}",
                f"  Filter layers : {', '.join(s.filter_layers) or 'none'}",
                f"  Signal layers : {', '.join(s.signal_layers) or 'none'}",
                f"  {s.interpretation[:200]}",
                f"  Scholarly: {s.scholarly_parallel[:120]}",
                "",
            ]
        out = "\n".join(lines)

    _write_output(out, args.output, args.format)
    return 0


# ── Command: pipeline ─────────────────────────────────────────────────────────

def cmd_pipeline(args: argparse.Namespace) -> int:
    inputs     = args.inputs
    traditions = args.traditions

    if len(traditions) == 1:
        traditions = traditions * len(inputs)
    elif len(traditions) != len(inputs):
        print(
            f"Error: --traditions must be 1 (applied to all) or "
            f"match --inputs count ({len(inputs)})",
            file=sys.stderr
        )
        return 1

    output_dir = _ensure_output_dir(args.output_dir)
    fmt        = args.format

    print(f"\n  CODEX Pipeline — {len(inputs)} text(s)", file=sys.stderr)
    print(f"  Output dir: {output_dir}\n", file=sys.stderr)

    # Build all reports
    filter_reports = []
    tiekat_reports = []

    for path, tradition in zip(inputs, traditions):
        source = _source_label(path)
        text   = _read_text(path)
        print(f"  Analyzing: {source} [{tradition}]", file=sys.stderr)

        fe = InstitutionalFilter(tradition=tradition)
        te = TIEKATPatternEngine(tradition=tradition)
        fr = fe.analyze(text, source=source)
        tr = te.analyze(text, source=source)

        filter_reports.append(fr)
        tiekat_reports.append(tr)

        # Individual dashboard
        if fmt == "html":
            viz  = CodexVisualizer()
            html = viz.full_dashboard(
                filter_report=fr,
                tiekat_report=tr,
                title=f"CODEX — {source}",
                source_label=source,
            )
            stem = Path(path).stem
            out_path = output_dir / f"{stem}_dashboard.html"
            out_path.write_text(html, encoding="utf-8")
            print(f"    → {out_path}", file=sys.stderr)

        elif fmt == "json":
            stem = Path(path).stem
            combined = {
                "source": source, "tradition": tradition,
                "filter_report": fr.to_dict(),
                "tiekat_report": tr.to_dict(),
            }
            out_path = output_dir / f"{stem}_analysis.json"
            out_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
            print(f"    → {out_path}", file=sys.stderr)

    # Pairwise comparison matrix
    if len(tiekat_reports) >= 2:
        print("\n  Building convergence matrix...", file=sys.stderr)
        multi = MultiComparator()
        matrix = multi.compare_many(tiekat_reports)
        print(matrix.render_ascii())

        if fmt == "html" and len(tiekat_reports) == 2:
            comp = CodexComparator().compare(tiekat_reports[0], tiekat_reports[1])
            viz  = CodexVisualizer()
            html = viz.full_dashboard(
                filter_report=filter_reports[0],
                tiekat_report=tiekat_reports[0],
                comparison_report=comp,
                title=f"CODEX: {tiekat_reports[0].tradition} vs {tiekat_reports[1].tradition}",
            )
            out_path = output_dir / "comparison_dashboard.html"
            out_path.write_text(html, encoding="utf-8")
            print(f"  Comparison dashboard → {out_path}", file=sys.stderr)

        # Matrix JSON
        matrix_path = output_dir / "convergence_matrix.json"
        matrix_path.write_text(
            json.dumps(matrix.to_dict(), indent=2),
            encoding="utf-8"
        )
        print(f"  Matrix → {matrix_path}", file=sys.stderr)

    print(f"\n  Pipeline complete. {len(inputs)} text(s) processed.\n",
          file=sys.stderr)
    return 0


# ── Command: explain ──────────────────────────────────────────────────────────

def cmd_explain(args: argparse.Namespace) -> int:
    if args.pattern:
        key = args.pattern.upper().replace(" ", "_")
        if key in PATTERN_EXPLANATIONS:
            info = PATTERN_EXPLANATIONS[key]
            lines = [
                "",
                f"  {info['name']}",
                f"  {'=' * len(info['name'])}",
                f"  TIEKAT: {info['tiekat']}",
                "",
                f"  {info['description']}",
                "",
                "  Examples:",
            ]
            for ex in info["examples"]:
                lines.append(f"    ◆ {ex}")
            lines += [
                "",
                "  Interpretation:",
                f"    {info['interpretation']}",
                "",
            ]
            print("\n".join(lines))
        elif key in LAYER_EXPLANATIONS:
            info = LAYER_EXPLANATIONS[key]
            lines = [
                "",
                f"  {info['name']}",
                f"  {'=' * len(info['name'])}",
                f"  {info['description']}",
                "",
                "  Examples:",
            ]
            for ex in info["examples"]:
                lines.append(f"    ◆ {ex}")
            lines.append("")
            print("\n".join(lines))
        else:
            print(f"\n  Unknown pattern/layer: {args.pattern}")
            print("  Use: codex explain --list to see all available\n")
            return 1

    elif args.module:
        modules = {
            "filter": (
                "CODEX Institutional Filter (codex_filter.py)\n"
                "─────────────────────────────────────────────\n"
                "Analyzes text passage-by-passage for signal (original consciousness\n"
                "language, ε ≠ 0 patterns) vs filter (institutional overlay, fear\n"
                "framing, authority claims, exclusivity markers).\n\n"
                "Produces per-passage coherence scores [0-1] where:\n"
                "  1.0 = PURE_SIGNAL (strong original consciousness language)\n"
                "  0.0 = INSTITUTIONAL (heavy institutional overlay)\n\n"
                "Detects EDITORIAL SEAMS — locations where coherence drops sharply,\n"
                "suggesting possible later editorial intervention. Each seam includes\n"
                "scholarly reference citations for further investigation.\n\n"
                "Key output: CoherenceMap, EditorialSeam list, FilterReport"
            ),
            "patterns": (
                "CODEX TIEKAT Pattern Engine (codex_tiekat_engine.py)\n"
                "─────────────────────────────────────────────────────\n"
                "Detects TIEKAT v64 mathematical pattern types in ancient texts:\n"
                "  ε EPSILON_SIGNAL   — direct inner consciousness language\n"
                "  Ω OMEGA_FLOW       — dynamic becoming/transformation\n"
                "  C* C_STAR_ATTRACTOR — unity/pleroma convergence language\n"
                "  🛡 SOVEREIGN_FIELD  — individual liberation/authority\n"
                "  𝟘 VOID_BRIDGE      — generative void/emptiness\n"
                "  Σ WEAVE_RESONANCE  — interconnection/coupling language\n"
                "  ∋ THREE_SIX_NINE   — 369 numerical/structural patterns\n"
                "  φ PHI_STRUCTURE    — golden ratio in text organization\n"
                "  F FIBONACCI        — Fibonacci sequence structural patterns\n\n"
                "Key output: PatternMatch list, CodexTIEKATReport with density metrics"
            ),
            "comparator": (
                "CODEX Cross-Tradition Comparator (codex_comparator.py)\n"
                "────────────────────────────────────────────────────────\n"
                "Compares TIEKAT pattern reports across traditions to find:\n"
                "  - Shared patterns: which TIEKAT types appear in both\n"
                "  - Convergence index [0-1]: how similar the traditions are\n"
                "  - Divergence signals: where they differ most significantly\n"
                "  - Shared signal passages: evidence from each tradition\n"
                "  - Top principles by cross-tradition corroboration\n\n"
                "IMPORTANT: Convergence ≠ common origin. Shared pattern vocabulary\n"
                "is a hypothesis seed, not historical proof.\n\n"
                "Key output: ComparisonReport, MultiTraditionMatrix (N×N pairwise)"
            ),
            "visualizer": (
                "CODEX Visualization Layer (codex_visualizer.py)\n"
                "─────────────────────────────────────────────────\n"
                "Generates self-contained interactive HTML dashboards:\n"
                "  - Coherence Heat Map: per-passage colored bars, click to expand\n"
                "  - Editorial Seam cards with scholarly citations\n"
                "  - Layer breakdown (signal ▲ vs filter ▼)\n"
                "  - TIEKAT Pattern Radar (Chart.js)\n"
                "  - Cross-tradition bar comparison\n"
                "  - Shared signal passages with excerpts\n\n"
                "All output is a single self-contained HTML file.\n"
                "Style: TIEKAT dark navy/gold aesthetic, JetBrains Mono + Cormorant Garamond"
            ),
        }
        info = modules.get(args.module)
        if info:
            print(f"\n{info}\n")
        else:
            print(f"\n  Unknown module: {args.module}")
            print("  Available: filter, patterns, comparator, visualizer\n")
            return 1

    elif getattr(args, "list", False):
        lines = [
            "",
            "  CODEX Pattern Types",
            "  ===================",
        ]
        for key, info in PATTERN_EXPLANATIONS.items():
            lines.append(f"  {key:25s} — {info['tiekat']}")
        lines += [
            "",
            "  Filter Layer Types",
            "  ==================",
        ]
        for key, info in LAYER_EXPLANATIONS.items():
            lines.append(f"  {key:25s} — {info['description'][:60]}")
        lines.append("")
        print("\n".join(lines))
    else:
        print("\n  Usage: codex explain [--pattern PATTERN] [--module MODULE] [--list]\n")

    return 0


# ── Command: list ─────────────────────────────────────────────────────────────

def cmd_list(args: argparse.Namespace) -> int:
    if getattr(args, "traditions", False) or not getattr(args, "patterns", False):
        lines = [
            "",
            "  CODEX Available Traditions",
            "  ==========================",
            "  Key              Label",
            "  ─────────────────────────────────────────",
        ]
        for key, label in TRADITIONS.items():
            lines.append(f"  {key:16s} {label}")
        lines += [
            "",
            "  Usage: codex analyze --tradition thomas --input text.txt",
            "",
        ]
        print("\n".join(lines))

    if getattr(args, "patterns", False):
        lines = [
            "",
            "  CODEX TIEKAT Pattern Types",
            "  ==========================",
        ]
        for pt in PatternType:
            info = PATTERN_EXPLANATIONS.get(pt.value, {})
            name = info.get("name", pt.value)
            lines.append(f"  {pt.value:25s} — {name}")
        lines += [
            "",
            "  Usage: codex explain --pattern EPSILON_SIGNAL",
            "",
        ]
        print("\n".join(lines))

    if getattr(args, "layers", False):
        lines = [
            "",
            "  CODEX Filter Layer Types",
            "  ========================",
        ]
        for lt in LayerType:
            info = LAYER_EXPLANATIONS.get(lt.value, {})
            name = info.get("name", lt.value)
            lines.append(f"  {lt.value:25s} — {name}")
        lines += [
            "",
            "  Usage: codex explain --pattern FEAR_FRAMING",
            "",
        ]
        print("\n".join(lines))

    return 0


# ── Parser builder ─────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(f"""
  ╔══════════════════════════════════════════════════════╗
  ║  CODEX — Ancient Wisdom Pattern Analysis Toolkit    ║
  ║  TIEKAT {TIEKAT_VER} Sovereign Substrate Weave          ║
  ║  PHI369 Labs / Parallax  ◆  C* = φ/2  ◆  ε ≠ 0    ║
  ╚══════════════════════════════════════════════════════╝

  Version: {VERSION}  ◆  Seed: {SEED}
        """).strip(),
    )
    parser.add_argument("--version", action="version",
                        version=f"CODEX {VERSION} / TIEKAT {TIEKAT_VER}")

    sub = parser.add_subparsers(dest="command", required=True)

    # Shared arguments helper
    def add_shared(p: argparse.ArgumentParser, has_output: bool = True) -> None:
        if has_output:
            p.add_argument("--output", "-o", default=None,
                           help="Output file path (default: stdout for text/json, auto for html)")
        p.add_argument("--format", "-f",
                       choices=["dashboard", "text", "json", "markdown", "html"],
                       default="dashboard",
                       help="Output format (default: dashboard)")

    def add_tradition(p: argparse.ArgumentParser, flag: str = "--tradition") -> None:
        p.add_argument(flag, "-t", default="generic",
                       choices=list(TRADITIONS.keys()),
                       help="Text tradition (default: generic)")

    # ── analyze ──────────────────────────────────────────────────────────────
    p_analyze = sub.add_parser(
        "analyze",
        help="Run full analysis (filter + patterns + viz) on one text",
        description="Run all CODEX modules on a single text.",
    )
    p_analyze.add_argument("--input", "-i", required=True,
                           help="Path to text file")
    p_analyze.add_argument("--source", default=None,
                           help="Human-readable source label (default: filename)")
    add_tradition(p_analyze)
    add_shared(p_analyze)
    p_analyze.set_defaults(func=cmd_analyze)

    # ── compare ───────────────────────────────────────────────────────────────
    p_compare = sub.add_parser(
        "compare",
        help="Cross-tradition comparison of two texts (all modules)",
        description="Compare two texts using all CODEX modules.",
    )
    p_compare.add_argument("--input-a", "-a", required=True)
    p_compare.add_argument("--input-b", "-b", required=True)
    p_compare.add_argument("--tradition-a", default="generic",
                           choices=list(TRADITIONS.keys()))
    p_compare.add_argument("--tradition-b", default="generic",
                           choices=list(TRADITIONS.keys()))
    p_compare.add_argument("--source-a", default=None)
    p_compare.add_argument("--source-b", default=None)
    add_shared(p_compare)
    p_compare.set_defaults(func=cmd_compare)

    # ── filter ────────────────────────────────────────────────────────────────
    p_filter = sub.add_parser(
        "filter",
        help="Institutional filter analysis only",
        description="Run the institutional filter and signal recovery analysis.",
    )
    p_filter.add_argument("--input", "-i", required=True)
    p_filter.add_argument("--source", default=None)
    add_tradition(p_filter)
    add_shared(p_filter)
    p_filter.set_defaults(func=cmd_filter)

    # ── patterns ──────────────────────────────────────────────────────────────
    p_patterns = sub.add_parser(
        "patterns",
        help="TIEKAT pattern engine analysis only",
        description="Run the TIEKAT pattern detection engine.",
    )
    p_patterns.add_argument("--input", "-i", required=True)
    p_patterns.add_argument("--source", default=None)
    add_tradition(p_patterns)
    add_shared(p_patterns)
    p_patterns.set_defaults(func=cmd_patterns)

    # ── seams ─────────────────────────────────────────────────────────────────
    p_seams = sub.add_parser(
        "seams",
        help="Editorial seam detection only",
        description="Detect editorial seams and transition points in text.",
    )
    p_seams.add_argument("--input", "-i", required=True)
    p_seams.add_argument("--source", default=None)
    add_tradition(p_seams)
    add_shared(p_seams)
    p_seams.set_defaults(func=cmd_seams)

    # ── pipeline ──────────────────────────────────────────────────────────────
    p_pipeline = sub.add_parser(
        "pipeline",
        help="Full pipeline: N texts → all analyses + convergence matrix",
        description=(
            "Run the complete CODEX pipeline on multiple texts:\n"
            "  - Individual analysis dashboard per text\n"
            "  - Pairwise convergence matrix across all texts\n"
            "  - Combined comparison dashboard (if 2 texts)\n"
            "  - All outputs written to --output-dir"
        ),
    )
    p_pipeline.add_argument("--inputs", "-i", nargs="+", required=True,
                            help="Paths to text files")
    p_pipeline.add_argument("--traditions", "-t", nargs="+",
                            default=["generic"],
                            help="Tradition per input (1 or match input count)")
    p_pipeline.add_argument("--output-dir", "-o", default="codex_reports",
                            help="Output directory (default: codex_reports/)")
    p_pipeline.add_argument("--format", "-f",
                            choices=["html", "json", "text"],
                            default="html",
                            help="Output format (default: html)")
    p_pipeline.set_defaults(func=cmd_pipeline)

    # ── explain ───────────────────────────────────────────────────────────────
    p_explain = sub.add_parser(
        "explain",
        help="Explain pattern types, layers, and modules",
        description="Get detailed explanations of CODEX concepts.",
    )
    p_explain.add_argument("--pattern", default=None,
                           help="Pattern or layer type to explain (e.g. EPSILON_SIGNAL)")
    p_explain.add_argument("--module", default=None,
                           choices=["filter", "patterns", "comparator", "visualizer"],
                           help="Module to explain")
    p_explain.add_argument("--list", action="store_true",
                           help="List all patterns and layers")
    p_explain.set_defaults(func=cmd_explain)

    # ── list ──────────────────────────────────────────────────────────────────
    p_list = sub.add_parser(
        "list",
        help="List available traditions and pattern types",
    )
    p_list.add_argument("--traditions", action="store_true",
                        help="List available traditions")
    p_list.add_argument("--patterns", action="store_true",
                        help="List TIEKAT pattern types")
    p_list.add_argument("--layers", action="store_true",
                        help="List filter layer types")
    p_list.set_defaults(func=cmd_list)

    return parser


# ── Main ──────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    parser = build_parser()
    args   = parser.parse_args(argv)

    try:
        return int(args.func(args))
    except FileNotFoundError as e:
        print(f"\n  Error: {e}\n", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n  Unexpected error: {type(e).__name__}: {e}\n", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
