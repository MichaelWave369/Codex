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

## CODEX Operator Studio (Streamlit, v2.1)

CODEX Operator Studio is a local-first operator interface for running existing CODEX engines
without replacing CLI workflows.

### Modes

- **Analyze**: run TIEKAT + Institutional Filter on one text.
- **Compare**: run cross-tradition comparison on two texts.
- **Workspace**: browse and curate saved local analysis bundles.

### v2.1 workspace intelligence

- Local workspace storage in **`.codex_workspace/`** (auto-created when needed).
- **Save current session to workspace** from the Workspace mode toolbar.
- **Recent Sessions** panel (top 3–5 latest bundles) with one-click **Resume**.
- **Quick Resume Last Session** action in Workspace toolbar.
- **Favorites/Starred bundles** with persistent `metadata.favorite` state.
- **Bundle browser** with metadata, mode/tag/operator/text filters, favorites-only toggle, and
  load/favorite/delete actions.
- **Sorting options**: newest, oldest, most pins, most notes, alphabetical.
- **Findings index** aggregated across workspace bundles from pinned findings.
- **Notes index** aggregated across workspace bundles with searchable previews.
- **Bundle comparison** panel for side-by-side metadata/signal inspection.
- **Lightweight metadata editing** (project/operator/tags/description) with save-back to loaded
  bundle.
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

## License

Codex is released under the MIT License.

The public repository contains the open symbolic-analysis runtime, schemas,
examples, tests, documentation, and safety boundaries.

Private Parallax / PHI369 canon packs, proprietary adapters, unreleased prompts,
private source atlases, closed-source integrations, EVIE private decks, and
other non-public PHI369 Labs materials are not included in this license unless
explicitly published in this repository.

## Voynich symbolic comparison pilot (research branch)

An optional, local-first **VGVE** cross-text adapter compares *human-annotated*
symbolic operator sequences using adjacency overlap, seeded shuffle controls,
historical provenance gates, counter-hypotheses, and SHA-256 receipts.

This is a **hypothesis-testing workbench**, **not a Voynich translation**.
The bundled example is synthetic, not historical evidence.

```bash
python -m codex.voynich_engine examples/voynich_symbolic_demo.json --out receipt.json
```

See [the research protocol](docs/VOYNICH_ENGINE.md) for safeguards, limitations,
and the planned primary-source / blind-annotation work.

### Phase 3: hypothesis-blind region review

The optional `codex.voynich_review` module extends VGVE with **fixed spatial
region protocols, two independent observer sheets, protocol-bound review
sealing, and Cohen's kappa agreement reports**. Its blank sheets contain no
Voynich translation or preloaded cosmological interpretation.

See [the review protocol](docs/VOYNICH_REVIEW.md) for the complete CLI workflow,
codebook, uncertainty categories, and negative-control requirements.

### Phase 4: real IVTFF transliteration and source crosswalk

The new `codex.voynich_ivtff` module indexes the ZL 3b EVA transliteration
with strict IVTFF header and line validation, SHA-256 source checksums, and a
conservative bridge to verified Yale IIIF folio labels. It **does not translate
the manuscript or infer symbolic meaning**.

A GitHub Actions source probe can fetch live upstream data and emit
metadata-only artifacts without installing anything locally. Read the
[Phase 4 protocol](docs/VOYNICH_IVTFF.md) before interpreting results.

### Phase 5: preregistered, source-locked statistical pilot

The optional `codex.voynich_study` module selects a deterministic cohort
from verified Yale IIIF and ZL 3b IVTFF metadata, freezes a 25% held-out
folio partition, and declares a single statistical endpoint **before**
independent image-region annotations. It will not invent observer data.

A [GitHub-hosted preparation workflow](.github/workflows/vgve-study-prereg.yml)
creates the source-bound study plan and neutral grid protocol without requiring
local setup. Read the [preregistered pilot design](docs/VOYNICH_PREREGISTERED_PILOT.md)
for test method, sample-size limitations, and claim boundaries.

## Elohim creation atlas (research pilot)

A local-first, source-anchored comparative registry distinguishes textual observations,
manuscript variants, cultural parallels and later interpretations of creation narratives.
Unknown counts remain unknown; motif overlap does not establish common identity.

```bash
python -m codex.elohim_atlas list
python -m codex.elohim_atlas compare genesis-1 apocryphon-john
```

See [the research protocol](docs/ELOHIM_ATLAS.md).
