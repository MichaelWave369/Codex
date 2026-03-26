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

## CODEX Operator Studio (Streamlit, v2.0)

CODEX Operator Studio is a local-first operator interface for running existing CODEX engines
without replacing CLI workflows.

### Modes

- **Analyze**: run TIEKAT + Institutional Filter on one text.
- **Compare**: run cross-tradition comparison on two texts.
- **Workspace**: browse and curate saved local analysis bundles.

### v2.0 workspace features

- Local workspace storage in **`.codex_workspace/`** (auto-created when needed).
- **Save current session to workspace** from the Workspace mode toolbar.
- **Bundle browser** with metadata, mode filters, text/tag/operator search, and load/delete actions.
- **Findings index** aggregated across workspace bundles from pinned findings.
- **Notes index** aggregated across workspace bundles with searchable previews.
- **Bundle comparison** panel for side-by-side metadata/signal inspection.
- Bundle export/import remains local-first (no remote persistence layer).

### Existing analysis features

- Structured tabs for overview, patterns/filter/seams/shared/divergence, and raw JSON.
- Passage inspector, pattern filters, coherence charts, distribution chart, and Pattern ↔ Passage linking.
- Side-by-side comparison evidence and Delta Lens for convergence/divergence focus.
- Deterministic Analyze/Compare summaries, analyst notes, pinned findings, and Workbench Markdown export.
- Export actions for JSON, Markdown, dashboard text, and HTML.

### Install UI dependency

```bash
pip install -e .[dev,ui]
```

### Run

```bash
streamlit run codex_operator/app.py
```

### Quick usage

1. Choose **Analyze**, **Compare**, or **Workspace** mode.
2. Paste text (or upload `.txt` / `.md`) for Analyze/Compare.
3. Select tradition(s) and source label(s), then run analysis.
4. Save sessions into Workspace for local bundle library management.
5. Use Workspace browser/indexes/comparison to revisit findings and notes.
