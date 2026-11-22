# VGVE Phase 2: Yale source atlas and blind-review preparation

**Status:** functioning offline IIIF metadata importer, no Voynich decipherment.
This feature adds source provenance before anyone assigns metaphysical or
biological meaning to an illustration.

## Source anchors

1. **Manuscript:** Beinecke MS 408, Yale Beinecke Rare Book & Manuscript Library.
   - Institutional overview: <https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript>
   - Digital catalog: <https://collections.library.yale.edu/catalog/2002046>
   - Official IIIF manifest: <https://collections.library.yale.edu/manifests/2002046>
2. **Transliteration (separate future pipeline):** René Zandbergen's account of
   EVA and IVTFF, including transcription editions and uncertainty:
   <https://www.voynich.nu/transcr.html>.
   EVA is a *transliteration scheme*, **not a decoded language**.

The IIIF importer does **not** ingest text or derive readings from visual data.
A manifest's URLs identify images; an annotated observer is still required to
support a visual claim. Respect holding-library image terms before redistributing
binary scans.

## Download source (manual acquisition)

Download the manifest from the Yale digital library or save the JSON from your
browser. Some network environments may reject direct automated requests; a
download failure must be reported as such, **never** replaced with fabricated
metadata or an unofficial mirror without explicit provenance.

```bash
curl -fL --retry 3 https://collections.library.yale.edu/manifests/2002046 -o yale_2002046.json
python -m codex.voynich_sources index yale_2002046.json --out yale_atlas.json
```

The indexer supports IIIF Presentation **2** or **3** and captures:

- The **SHA-256 hash of the exact manifest bytes** as downloaded.
- The institution, canonical manifest and catalog URL.
- The IIIF canvas ID, original label, order, and first HTTPS image-body link.
- An **unambiguous** folio key only where the canvas label explicitly contains
  exactly one recognizable folio identifier such as `f78r`.
- An `ambiguous` or `unresolved` label state otherwise.
- A separate deterministic SHA-256 atlas receipt.

The tool does not assert an exact page count before reading the actual source,
nor does it automatically map "page 141" to a historical folio.

## Independent reviewer assignments

```bash
python -m codex.voynich_sources assign yale_atlas.json --folio f78r --out reviewer_a_blank.json
```

Repeat with a second reviewer **separately**. Assignments are deliberately
blank: no figure counts, symbolic associations, creation/escape readings, or
operator sequences are auto-inserted. A reviewer can add neutral observations
and separately propose operators, explaining visual evidence precisely.

**Important:** `--folio` works only when the actual Yale canvas labels have
a unique, explicit folio mapping. If the IIIF manifest uses only page numbers
or ambiguous foldout labels, the tool stops rather than pretending it knows the
mapping. A separate manually verified crosswalk is a future feature.

The blank forms keep the target Source → matter → experience → return theory
out of the annotation task, but reviewers can still identify the manuscript.
This is hypothesis-blind preparation, **not double-blind research**.

## Research program after this PR

1. Check real IIIF metadata, images, foliation, and Yale attribution manually.
2. Add edition-locked IVTFF/EVA transliterations with explicit uncertainty;
   never claim EVA symbols translate the Voynich writing.
3. Register independently sourced ancient-text passages with author, edition,
   translator, chapter, line ranges, and reuse rights.
4. Set an **operator codebook before coding**, quantify independent annotator
   agreement, and adjudicate conflicts in a recorded process.
5. Pre-register and freeze hypotheses, negative controls, held-out manuscripts,
   and analysis parameters; then run the established cross-text comparator.
6. Require alternative explanations such as ordinary iconographic similarity,
   shared cultural influence, generic narrative structure, and annotator bias.

## Reproducibility and safety checks

```bash
pytest tests/test_voynich_sources.py tests/test_voynich_engine.py
ruff check src/codex/voynich_sources.py tests/test_voynich_sources.py
ruff format --check src/codex/voynich_sources.py tests/test_voynich_sources.py
```

The importer rejects wrong manuscript IDs, missing/duplicate canvas identities,
unverifiable source folios, duplicate selected folios, and altered atlas receipts.

**Claim boundary:** A successful ingestion demonstrates primary-source metadata
and a reproducible workflow. It does not establish a cipher solution, a universal
ancient engine, or a Source/Demiurge cosmology.
