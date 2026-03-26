# CODEX

**CODEX** is an exploratory symbolic analysis toolkit: a deterministic, TIEKAT-inspired decoder for recurring metaphors and motifs in ancient wisdom tradition excerpts.

This repository exists to create a technically honest foundation for studying symbolic structure across texts without overstating certainty. The software is designed for hypothesis generation, not doctrinal authority or historical proof.

## Scope of the MVP

- Rule-based lexical matching only (no LLM calls).
- Two proof-of-concept tradition adapters:
  - Gospel of Thomas style sayings
  - Hermetic correspondence style excerpts
- Structured outputs with evidence spans and conservative confidence labels.
- Human-readable Markdown and machine-readable JSON output modes.

## Explicit non-goals

- Not a truth engine.
- Not a system for theological or historical certainty claims.
- Not a replacement for scholarship, translation work, or tradition-based interpretation.
- Not a universalizing claim that all traditions are identical.

## Installation

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## CLI usage

List available traditions:

```bash
codex list-traditions
```

Show a bundled sample:

```bash
codex sample --tradition thomas
codex sample --tradition hermetic
```

Decode a file and print both Markdown + JSON:

```bash
codex decode --tradition thomas --input src/codex/data/samples/gospel_of_thomas_sample.txt
```

Output only JSON:

```bash
codex decode --tradition hermetic --input src/codex/data/samples/hermetic_sample.txt --json
```

Explain starter pattern groups:

```bash
codex explain-patterns
```

## Repository structure

```text
.
├── docs/
│   ├── ARCHITECTURE.md
│   └── ETHICS.md
├── src/codex/
│   ├── cli.py
│   ├── decoder.py
│   ├── ethics.py
│   ├── lexicon.py
│   ├── models.py
│   ├── renderer.py
│   ├── traditions/
│   └── data/
└── tests/
```

## Quality and CI

The CI workflow runs:
- `ruff check`
- `ruff format --check`
- `pytest`

## Roadmap

1. Expand lexicon governance and term provenance.
2. Add richer corpora support with citation-aware ingest metadata.
3. Implement controlled cross-tradition comparison reports.
4. Add optional ML-assisted ranking under strict uncertainty and transparency constraints.

## Ethical framing

Please read [docs/ETHICS.md](docs/ETHICS.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before extending this project.

## CODEX Operator Studio (Streamlit, v1.2)

CODEX Operator Studio is a local-first operator interface for running the existing CODEX engines without replacing CLI workflows.

### What it provides

- **Analyze mode**: run TIEKAT + Institutional Filter on one text.
- **Compare mode**: run cross-tradition comparison on two texts.
- Structured tabs for overview, patterns/filter/seams/shared/divergence, and raw JSON.
- **Passage Inspector** in Filter Map: expandable per-passage details (coherence, hits, layer counts, notes, evidence).
- **Pattern Explorer filters**: pattern type, confidence, high-confidence-only, structural-only.
- **Coherence charts**: per-passage line + level-distinguished scatter views.
- **Pattern distribution chart**: compact counts by pattern type (filtered vs full set).
- **Side-by-side comparison evidence**: two-column A/B reading in Shared Signals and Divergence tabs.
- **Session export/import**: save and reload local session JSON (mode, inputs, latest result payloads).
- Export actions for JSON, Markdown, dashboard text, and HTML.
- Session-state-only behavior (no database in v1).

### Install UI dependency

```bash
pip install -e .[dev,ui]
```

### Run

```bash
streamlit run codex_operator/app.py
```

### Quick usage

1. Choose **Analyze** or **Compare** mode.
2. Paste text (or upload `.txt` / `.md`).
3. Select tradition(s) and source label(s).
4. Run analysis and inspect structured tabs.
5. Export JSON/Markdown/text/HTML outputs from the results pane.
