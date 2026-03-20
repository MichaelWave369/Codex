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
