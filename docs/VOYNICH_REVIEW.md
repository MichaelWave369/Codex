# VGVE Phase 3: locked-region blind review and agreement

**Claim boundary:** this protocol evaluates consistency among **human interpretations**
of visual source regions. It is not a decipherment of the Voynich Manuscript,
proof that medieval authors knew metaphysical machinery, or an automatic vision model.

The research design follows the legacy VGVE v1.0 safeguards:
**source anchor → observation → mapping → counter-hypothesis → receipt**.

## Why fixed regions?

A researcher can accidentally choose only illustrations that support a preferred
hypothesis. To counter that selection effect, the new module creates a
**regular, predetermined grid** for each folio canvas. Every preselected
cell must be evaluated, including ambiguous, empty, or visually irrelevant ones.

The code **does not recognize objects** or claim that grids correspond to
independent medieval diagrams. This is an initial region-control mechanism.

## Prerequisites

Run the Phase 2 Yale IIIF atlas importer against your own downloaded
official manifest. The file used must have a valid source and atlas receipt.

```bash
python -m codex.voynich_sources index yale_2002046.json --out yale_atlas.json
```

If the actual atlas does **not** contain a unique `f78r` folio mapping, stop:
the program will not guess a source folio based on page order. A separately
verified folio-to-canvas crosswalk remains future work.

## Reproducible experimental flow

1. Freeze the full list of study folios and the neutral operator codebook **before**
   inspecting the comparative results.
2. Make a fixed-region protocol. It contains only canvas identities, image URLs,
   unambiguous folio labels, and bounding rectangles in 0–1000 normalized units.

```bash
python -m codex.voynich_review protocol yale_atlas.json --folio f78r --rows 2 --cols 2 --out protocol.json
```

3. Make two independent blank review sheets, preferably for reviewers who have
   not been told the Source-to-matter-to-experience-to-return interpretation.

```bash
python -m codex.voynich_review blank protocol.json --reviewer analyst-a --out a.json
python -m codex.voynich_review blank protocol.json --reviewer analyst-b --out b.json
```

4. Each reviewer privately examines the linked image regions and sets every
   region's `operator`, `evidence`, and, for a non-abstention label,
   `counter_hypothesis`. Allowed operators include `BIND`, `EMBODY`,
   `FLOW`, `CYCLE`, `RETURN`, etc. `NO_PATTERN` and `UNDECIDED`
   are allowed: don't force a meaning when there isn't one.
5. Each reviewer must edit `blinding_asserted` to `true` **only if they genuinely
   worked independently without seeing the preferred theory**, set
   `status` to `COMPLETE`, and recompute the JSON receipt after edits. The
   program checks the assertion but cannot independently verify honesty.
6. Compare the two completed, receipt-valid reviews:

```bash
python -m codex.voynich_review score protocol.json a.json b.json --out agreement.json
```

The current SHA receipt is a tamper-evident checksum **only** and is *not*
a cryptographic signature or proof of who authored a review. A future
operator UI can recalculate it for reviewers and validate linked revisions.

## Output explained

- `raw_agreement`: identical choices / total preregistered regions.
- `chance_expected_agreement`: expected matching under independent rater
  marginals.
- `cohen_kappa`: chance-corrected agreement; **undefined** if both reviewers
  assigned exactly the same single label to every cell.
- `operator_disagreements`: exact region IDs and the different reports.
- `manifest_sha256`, `protocol_receipt_sha256` and individual review receipts:
  make it possible to identify inputs that produced the score.

High kappa demonstrates *repeatability*, not semantic truth. Reviewers may
share assumptions. A mixed set of empty and information-rich regions can also
make agreement statistics misleading.

## Operator codebook: provisional definitions

The word `operator` means an **analyst's classification**, never a reading
of Voynich letters.

| Operator | Working visual cue (must be independently defined more precisely) |
|---|---|
| BIND | Distinct elements shown connected or joined |
| FLOW | Directional movement, stream, or continuity is visibly suggested |
| CYCLE | Repeated round/cyclic forms or visible loops |
| DIFFERENTIATE | One form appears divided into distinct forms |
| EMBODY | A distinguishable figure or form sits within a boundary |
| EXPERIENCE | A viewpoint or perceiver is unambiguously drawn, if at all |
| INTEGRATE | Multiple visual paths appear to converge |
| RETURN | A trajectory visibly leads to an earlier node |
| NO_PATTERN | No relevant spatial relationship visible under the codebook |
| UNDECIDED | Cannot tell from the available evidence |

These visual cues are **not yet validated** and some are difficult to operationalize.
The full engine recognizes 14 interpretive operators plus the two abstention
states. Until independent coders agree on a locked codebook, no claims about
operator frequencies in authentic folios are justified.

## Negative-control strategy

Pre-register ordinary botanical illustrations, unrelated medieval manuscript
diagrams, and shuffled-operator baselines as distinct controls. Keep analyst
training examples separate from held-out folios and unseen ancient texts.

The end goal is **not** to make every text say the same thing. It is to ask
whether a precisely defined structural model makes predictions that competing
models cannot explain as well.

## Primary-source caveat

Yale's official IIIF manifest is the source of truth. As of this research phase,
direct retrieval of that endpoint from our tool environment returned 403.
Independent third-party audits of its 213 canvases may inform the questions,
but must not silently replace verified primary-source metadata. No authentic
Yale visual review is claimed to have occurred in this PR.
