# VGVE Phase 5: preregistered visual/transliteration pilot

**Study ID:** VGVE-PILOT-001  
**Status:** Study design and source-locked preparation software. **No human
annotations or empirical result currently exist.** This is not a Voynich
decipherment or evidence for a Demiurge, a shared ancient decoder, or a
Source-to-body process.

## Scope: what the first study can actually test

The narrow, preregistered hypothesis is: **among held-out folio labels,
the fraction of fixed image cells independently assigned FLOW by *both*
reviewers has positive Spearman rank correlation with the number of IVTFF
textual loci assigned to the same folio label.**

This is a manuscript-layout association hypothesis, not a test of what the
Voynich text means. An association could be explained by illustration space,
page layout, folio conventions, visual priming, and section differences.

## What is frozen before any reviews

- Input bytes: SHA-256-pinned Yale IIIF and ZL 3b sources from
  [VOYNICH_SOURCE_LOCK.json](VOYNICH_SOURCE_LOCK.json).
- Eligible units: only folio IDs with exactly one literal bridge canvas
  mapping, a nonempty source image URL and one or more IVTFF loci.
- Deterministic sample selection: sort eligible folios by SHA-256 of
  `vgve-pilot-v1:2026-11-22:{folio_id}`; take the first 32.
- Fixed holdout: first 8 selected folios; remaining 24 development.
  Reviewers must not know held-out membership or see this source plan.
- Image observation unit: predefined **2×2 grid** on each folio canvas.
  Do not select pretty pictures or symbol-heavy regions post hoc.
- Response: proportion of *all four cells per folio* where two independent
  reviews both say **FLOW**; NO_PATTERN and UNDECIDED count in denominator.
- Primary test: one-sided positive Spearman correlation of rank-transformed
  IVTFF loci count versus consensus-FLOW fraction on holdout only.
- Randomization control: 999 seeded permutations of response labels among
  held-out folios (seed `vgve-pilot-v1:2026-11-22:permutation`).
- Predeclared threshold: p ≤ 0.05; tied ranks and constant-input
  degeneracy handled deterministically.
- Small sample caveat: 8 held-out folios is **underpowered** and this remains
  an exploratory pilot regardless of the p-value.

The planned test is not optimized after examining review outcomes.

## GitHub-hosted preparation (no PC work)

The workflow [VGVE preregistered pilot preparation](../.github/workflows/vgve-study-prereg.yml)
fetches the primary sources and rechecks the pinned hashes on GitHub Actions.
It generates machine-readable metadata artifacts:

- `pilot_plan.json`: exact sample, holdout partition, source hashes,
  primary endpoint, permutations and analysis lock.
- `neutral_grid_protocol.json`: deterministic blank 2×2 image regions,
  source canvas URLs, provenance receipt.
- `pilot_summary.json`: machine-readable planning status and plan receipt.
- Source metadata indices, **not raw manuscript images or transcription text**.

The job MUST fail if either upstream changed, the strict crosswalk fails, or
fewer than 32 image-backed, literally matched folios are available.

The plan is reproducible from the pinned raw bytes plus source code. Keep the
GitHub run's receipt SHA and commit SHA as the frozen preregistration record.

## Human study steps, not yet completed

1. Lock the operation definitions. Reviewer A and reviewer B independently
   annotate the same prespecified grid without seeing the planned effect,
   reviewer's choices or each other's results.
2. Permit NO_PATTERN and UNDECIDED; do not force symbolic interpretations.
   Require evidence and counter-hypotheses for non-abstentions.
3. Use the existing `codex.voynich_review seal` workflow for both complete,
   independently produced review sheets.
4. Run the Phase 5 scorer with the frozen plan and original protocol:

```bash
python -m codex.voynich_study score pilot_plan.json \
  neutral_grid_protocol.json reviewer_a_sealed.json \
  reviewer_b_sealed.json --pilot-lock docs/VOYNICH_PILOT_LOCK.json \
  --out pilot_result.json
```

It checks the frozen plan SHA from the repository lock, source/protocol hashes,
reviewer coverage and independence assertions.
If the documents are incomplete, it **blocks evaluation**. It reports
Spearman rho, permutation p-value, the reviewer agreement checksum and Cohen's
kappa, and an explicit verdict. "PILOT_POSITIVE_ASSOCIATION" is a statistical
signal label, never a decipherment or historical truth label.

## Controls and constraints

The included permutation control keeps textual measurements and visual-label
marginals fixed, but does **not** account for section-level confounding or
cultural borrowing. A truly convincing cross-text engine would additionally
need independent manuscript controls, expert coders, separate translations and
philological context, image-vs-text section stratification, and untouched
external holdouts. None of those are supplied or inferred by this pilot.

The program is written using the Python standard library and existing CODEX
packages, with synthetic-only regression fixtures. GitHub's source-prep
workflow is the first run that can build the plan on verified real metadata;
it does not and must not generate fake observer input.

**Evidence first. Patterns second. Interpretations last.**


## Frozen first live preregistration

The first successful GitHub-hosted source run recorded 178 strictly eligible
folios, selected 32 and reserved 8 as the untouched holdout. Its plan receipt
is pinned in [`VOYNICH_PILOT_LOCK.json`](VOYNICH_PILOT_LOCK.json). This lock
was committed before collecting visual annotations. GitHub Actions now checks
that the complete plan receipt, cohort size and holdout size are identical
to that frozen record on subsequent runs.

A source-locked planning artifact is **not** a scored experiment. There is no
positive or negative semantic finding until independent reviews are collected.
