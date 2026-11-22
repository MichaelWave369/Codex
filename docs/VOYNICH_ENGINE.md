# Voynich Symbolic Engine: cross-text research pilot

**Status:** experimental, local-first, non-decipherment, no historical claims.

This module extends CODEX with one narrow, falsifiable question: do *human-assigned,
source-anchored sequences of symbolic operators* recur across independently annotated
sources more than a simple shuffled-order baseline predicts?

It implements a small subset of the earlier **Voynich Green Vessel Engine (VGVE)
v1.0** specification. It does not claim that Voynich glyphs have been read, that
all ancient traditions encode a shared truth, or that "Source" or a "Demiurge"
exists as a measurable biological mechanism.

## Run offline

```bash
python -m codex.voynich_engine examples/voynich_symbolic_demo.json --out receipt.json
python -m pytest tests/test_voynich_engine.py
```

The bundled records are **entirely invented**. The Voynich-inspired diagram is
not a genuine folio or a transcription. A positive result on this fixture is a
software regression check, **not a scientific finding**.

## Packet schema (v0.1)

- `schema_version`: `vgve-cross-text/0.1`
- `hypothesis`: analyst's testable question
- `claimed_decipherment`: must be `false`
- `records`: 2+ source-anchored records from at least two traditions
- `record.source`: `kind` (`historical` or `synthetic`), `title`, `reference`,
  `url` for historical sources, and `text` for textual quotes
- `record.claim_label`: `ARCHITECTURAL MAPPING`, `EMPIRICAL HYPOTHESIS`, or `NON-CLAIM`
- `record.counter_hypothesis`: a plausible alternate interpretation
- `record.anchors`: 2+ ordered entries, each with `operator`, `kind`,
  `location`, and `evidence`

Text anchors must be exact substrings of `source.text`; visual descriptions
require a location label but **cannot be automatically verified** from images.
An annotator must verify that visual labels are fair to the source before
including them in a historical research packet. Represent source order explicitly
in the ordered `anchors` array.

## Declared operators

`BIND`, `CYCLE`, `DIFFERENTIATE`, `DISSOLVE`, `EMBODY`, `EXPERIENCE`,
`FLOW`, `GROW`, `INTEGRATE`, `MIRROR`, `RECURSE`, `RENEW`, `RETURN`, `TRANSFORM`.

These operators are interpretive labels, *not* translations. The proposed
Source → embodiment → experience → return reading is one hypothesis alongside
other possible explanations. Do not treat resemblance as historical proof.

## Comparison and controls

- Build each record's adjacent ordered operator-pair set.
- Compute pairwise Jaccard overlap of those transition sets.
- Estimate an exploratory one-sided p-value with 199 deterministic shuffles
  of the second sequence (seed 369), preserving label frequencies.
- Report shared transitions, provenance, counter-hypotheses, method limits,
  claim boundaries, and a canonical JSON SHA-256 receipt.

**Critically:** this is not a confirmatory test. The operator assignments are
subjective, the shuffled-order null is weak, and p-values are uncorrected for
multiple comparisons. For genuine testing, pre-register operator definitions,
use blind independent annotators, maintain inter-rater agreement statistics,
lock analysis parameters, hold out unseen texts, add negative-control corpora,
and compare against competing hypotheses and models of cultural transmission.

## Source acquisition and reproducibility backlog

1. Import primary Voynich folio images from Yale Beinecke MS 408 and carefully
   distinguish image annotations from linguistic transcriptions.
2. Track EVA/IVTFF transcription edition and uncertainty; never infer a
   translation from transliteration symbols.
3. Register historical editions, translators, exact passage locations,
   copyright/licensing, and provenance for comparison corpora.
4. Create blinded folio/ancient-text annotation batches with independent reviewers.
5. Publish analysis plans and negative controls *before* running the benchmark.
6. Verify reports by recomputing SHA-256 after removing `receipt_sha256`.

## Alignment with VGVE v1.0 canon

`Observe → Anchor → Map → Score → Guard → Counter-check → Emit → Receipt`

The machine does not autonomously discover hidden meanings. Its job is to
organize observations and give hypotheses a fair chance to **fail**.

No medical, herbal, fertility, or psychoactive preparation instructions belong
in this research module. This experimental adapter leaves the established
CODEX pipeline and interfaces unchanged.
