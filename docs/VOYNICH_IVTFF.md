# VGVE Phase 4: real transliteration source, conservative IIIF crosswalk

This phase brings CODEX closer to **real, provenance-preserving manuscript
measurements**, not an alleged decipherment. It is intentionally separate from
the analyst-assigned symbolic operator engine.

## Published sources

- Yale Beinecke MS 408: <https://collections.library.yale.edu/catalog/2002046>
- Yale IIIF manifest: <https://collections.library.yale.edu/manifests/2002046>
- Zandbergen-Landini **ZL 3b**, dated **2025-05-13**, IVTFF 2.0/EVA:
  <https://www.voynich.nu/data/ZL3b-n.txt>
- Transliteration and format context: <https://www.voynich.nu/transcr.html>

The official IVTFF format specifies distinct page and locus records, and
identifies paragraph, label, circle, and radial text loci. It does not make
Voynich glyphs into a verified language translation.

## What the new code does

1. Index a **saved local copy** of the actual ZL3b IVTFF data, validating its
   `#=IVTFF Eva- 2.0` header.
2. Record the raw-source SHA-256, declared edition, page identifiers, locus
   identifiers, locus markers, original file line numbers, raw payload hashes,
   literal lengths, and literal `?` and `[` marker counts.
3. **Do not copy the transliterated textual payload** into outputs or GitHub.
4. Verify the receipt SHA-256 before accepting a previously generated index.
5. If an official Yale IIIF atlas is present, join the two by **literal,
   unambiguous folio labels only**. Report unmatched and multi-canvas labels
   instead of fabricating matches.

### Offline commands

```bash
python -m codex.voynich_ivtff index ZL3b-n.txt --out zl3b_index.json
python -m codex.voynich_ivtff bridge zl3b_index.json yale_atlas.json \
  --out source_crosswalk.json
```

For source content pinned to a known digest, add:

```bash
python -m codex.voynich_ivtff index ZL3b-n.txt \
  --sha256 YOUR_INDEPENDENTLY_VERIFIED_SHA256 --out zl3b_index.json
```

Do not copy a hash from another mirror without establishing it refers to the
same raw bytes and exact source edition.

## No local setup required for GitHub-hosted checks

`.github/workflows/vgve-source-probe.yml` runs on this PR and is designed for
manual re-runs through GitHub Actions after merge. It retrieves both sources
on a temporary GitHub runner and stores **only computed metadata receipts**
as a seven-day workflow artifact, never the raw text or Yale images.

The artifact includes `status.txt`. Each upstream is explicitly marked as
fetched/indexed, unavailable, or fetched but rejected. A network or parsing
failure **is not** scientific evidence, and the workflow must never invent
a successful download. Yale has previously returned HTTP 403 in tool contexts,
so success must be confirmed from the actual GitHub run and its receipt artifact.

The usual project CI still tests the parser **offline** using synthetic records.
A passing fixture test does not prove the live parser accepted the complete
historical transcription.

## Research boundary and caveats

- **Transliteration != translation.** EVA is a reproducible way of representing
  perceived characters. It does not prove their linguistic meaning.
- Page IDs and canvas labels are **not** guaranteed to identify the same
  physical surface, especially folded and partial images.
- A literal `?` or `[` count is **not** a calibrated uncertainty score.
- Unrecognized IVTFF records raise errors instead of silently disappearing.
  If the real corpus contains unhandled legal features of the formal format,
  extend the parser against the IVTFF specification and add a regression test.
- Source SHA-256 checksums prove reproducibility of input bytes, not that the
  source transcription is objectively correct.
- Human annotation, blind review, alternative hypotheses, and holdout controls
  remain required before linking visual patterns to semantic interpretations.

## Next empirical milestone

Use the source crosswalk to select only verified, appropriately distinct
folios. Compare neutral text-structure observations (e.g., locus counts and
literal textual marker distributions) with independently scored image-region
annotations. Pre-register the statistical comparison before seeing results.
Negative controls must include unrelated manuscripts and simple page-layout
features. This remains **exploratory** unless a held-out study succeeds.
