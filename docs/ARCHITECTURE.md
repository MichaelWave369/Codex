# CODEX Architecture (MVP)

## Why deterministic first
The first release uses deterministic lexicon matching to provide:
- transparent behavior,
- reproducible outputs,
- inspectable evidence spans,
- low operational complexity.

This foundation helps contributors validate assumptions before introducing probabilistic methods.

## Current flow
1. Select tradition adapter (metadata, normalization rules, lexicon extensions).
2. Normalize text with simple substitution rules.
3. Load shared pattern lexicon from JSON.
4. Merge tradition-specific terms into shared tags.
5. Match terms directly in normalized text.
6. Emit structured `DecodeResult` with conservative confidence and cautionary notes.

## Why this is extensible
- Pattern files are editable JSON resources.
- Tradition adapters are isolated modules with small, explicit contracts.
- Rendering is separated from decoding (Markdown and JSON outputs).
- Tests assert behavior at lexicon, registry, decoder, and renderer levels.

## Phase 2 options
- Broaden multilingual lexicons with editorial review workflows.
- Add corpus packaging and citation-aware evidence indexing.
- Implement cross-tradition comparative reports with explicit uncertainty controls.
- Add optional ML-assisted ranking as a secondary layer, never replacing deterministic evidence.

## TIEKAT Pattern Analysis Stack (v64.0.0)

Four new modules extending CODEX with TIEKAT-aligned mathematical pattern detection:

### codex_tiekat_engine.py
Detects nine TIEKAT pattern types in ancient texts:
- `EPSILON_SIGNAL` — direct inner consciousness language (ε ≠ 0)
- `OMEGA_FLOW` — dynamic becoming/transformation language
- `C_STAR_ATTRACTOR` — unity/convergence/pleroma language (C* = φ/2)
- `SOVEREIGN_FIELD` — individual liberation and inner authority
- `VOID_BRIDGE` — generative void/emptiness (𝟘Nul ↔ Ω0)
- `WEAVE_RESONANCE` — interconnection/coupling/resonance (Σ_W)
- `THREE_SIX_NINE` — 369 numerical/structural patterns
- `PHI_STRUCTURE` — golden ratio organization
- `FIBONACCI` — Fibonacci sequence structure

### codex_filter.py
Institutional filter and signal recovery. Analyzes texts passage-by-passage for signal (ε ≠ 0 language) vs filter (institutional overlay). Detects editorial seams with scholarly reference citations.

### codex_comparator.py
Cross-tradition comparison. Produces convergence index [0-1] across all nine pattern types. Surfaces shared signals and divergences. Includes MultiComparator for N-text pairwise matrix.

### codex_visualizer.py
Interactive HTML dashboards. Coherence heat map, pattern radar (Chart.js), seam cards with citations, cross-tradition bar comparison. Single self-contained HTML file output.

### codex_cli.py (entry point: codex-tiekat)
Unified CLI wrapping all four modules:
  codex-tiekat analyze   — full analysis, one text
  codex-tiekat compare   — cross-tradition comparison
  codex-tiekat filter    — institutional filter only
  codex-tiekat patterns  — TIEKAT patterns only
  codex-tiekat seams     — editorial seam detection
  codex-tiekat pipeline  — N texts, pairwise matrix, all dashboards
  codex-tiekat explain   — explain any pattern type or module
  codex-tiekat list      — list traditions and pattern types
