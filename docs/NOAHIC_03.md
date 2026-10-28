# NOAHIC-03 — Witness-Aware Textual Comparison Gate

## The main discovery

The **Book of Jubilees was probably composed in Hebrew**, but the complete surviving manuscript tradition is **Ge'ez (Classical Ethiopic)**. Hebrew fragments from the Dead Sea Scrolls survive for other portions of the book; chapter 10 is not identified in the known preserved Hebrew loci catalogued for this pilot. This is a **provisional attestation gap**, not proof that a fragment never existed.

The medieval medical prologue of **Sefer Asaf** is transmitted in Hebrew, with modern editions based on medieval manuscripts. Thus a direct ancient-Hebrew-vs-medieval-Hebrew lexical comparison of these **exact two passages** is unavailable using presently identified original-language witnesses.

Modern Hebrew translations or retroversions of Jubilees cannot fill that gap as though they were ancient Hebrew transcriptions. The source issue is scientifically more important than a premature pattern score.

## Verified leads for the witness registry

- **Jubilees 10, Ge'ez:** [BibleSRC Book of Jubilees Ge'ez](https://biblesrc.org/text/jubilees), which credits the EOTC printed edition encoded by Beta maṣāḥǝft and lists CC BY-SA 4.0. The actual digitized edition is a **translation of an older Hebrew composition**, not an autograph Hebrew witness. License attribution and ShareAlike conditions apply to adapted/distributed text; source text is **not vendored here**.
- **Sefer Asaf prologue, medieval Hebrew:** [Z. Muntner (1958), Project Ben-Yehuda](https://benyehuda.org/read/53511). The site says the Hebrew edition was published **with permission**. This does not automatically allow republication under CODEX's MIT license; **no Hebrew edition content is bundled**. For background, see the [Posen Library's Book of Asaf](https://www.posenlibrary.com/entry/book-asaf).
- **Ancient Hebrew Jubilees elsewhere:** [IAA Dead Sea Scrolls Library, 4Q216](https://www.deadseascrolls.org.il/explore-the-archive/manuscript/4Q216-1?locale=en). 4Q216 is an authentic Hebrew Jubilees witness, but its published fragments preserve the beginning of the book, not the chapter 10 healing passage. Consult comprehensive published fragment lists for the full coverage claim.
- **Modern Hebrew version of Jubilees:** [Sefaria, Jubilees 10](https://www.sefaria.org/Book_of_Jubilees.10.10?lang2=en&with=About). Its Hebrew version should be treated as a **modern textual rendering**, not evidence that the Hebrew original of chapter 10 has survived.
- **Contextual scholarship:** [John C. Reeves's translation of Jellinek's three Sefer Noah compositions](https://pages.charlotte.edu/john-reeves/research-projects/medieval-jewish-pseudepigrapha/jellineks-sefer-noah/). Three conceptually related texts should not be collapsed into one witness.

## What the module does

`src/codex/noahic_witness.py` provides a strict Unicode-aware source registry. It:

1. Validates language, script, source edition, coverage and rights metadata.
2. Clearly labels printed editions, medieval copies, ancient translations, modern translations and unattested gaps.
3. Rejects text from a missing source locus.
4. Blocks comparisons between different source languages, and blocks purported **original-language** comparisons when an input is a modern translation or ancient version.
5. Blocks automatic alignment of material whose edition reuse permissions are unresolved.
6. For eligible **same-language, rights-cleared, registered** excerpts, lists literal shared two-token sequences only. This is merely a descriptive lexical report, **not** evidence of copying or manuscript ancestry.

All example snippets in tests are **synthetic Unicode fixtures**. They are not purported ancient phrases. No ancient-language reconstruction, translation or OCR occurs in this version.

## Commands

```shell
pip install -e .[dev]
python -m codex.noahic_witness validate
python -m codex.noahic_witness list
python -m codex.noahic_witness plan
pytest tests/test_noahic_witness.py
```

An optional local comparison accepts two JSON files:

```shell
python -m codex.noahic_witness compare LEFT.json RIGHT.json
```

Each file must have these fields:

```json
{
  "schema": "noahic-03/local-excerpt-v0.1",
  "witness_id": "REGISTERED_WITNESS_ID",
  "locus": "EXACT_SOURCE_LOCUS",
  "source_url": "EXACT_REGISTRY_SOURCE_URL",
  "editor": "WHO_TRANSCRIBED_THIS",
  "transcription_note": "HOW_IT_WAS_TRANSCRIBED_AND_CHECKED",
  "text": "USER-SUPPLIED_SOURCE_TEXT"
}
```

**Do not commit copyrighted transcriptions to the repository.** This local interface does not download any text; it never declares user-supplied transcription academically verified.

## Research gates we cannot bypass

- **GATE-A:** Actual manuscript attestation and edition identification.
- **GATE-B:** Source-language status: original-language witness vs ancient version vs modern translation.
- **GATE-C:** Reuse permission and audit trail for imported text.
- **GATE-D:** Locus coverage, uncertainty, restorations and damaged lines.
- **GATE-E:** Independent human philological review for cross-language parallels.
- **GATE-F:** Historical borrowing inference requires chronology, wording, controls, and competing explanations, none of which are completed here.

### Next research action

Work on a **translation-aware, manually reviewed bilingual alignment** between Ge'ez Jubilees 10 and Hebrew Sefer Asaf, anchored to scholarly translations, while keeping every cross-language equivalence explicitly tagged as editorial judgment. In parallel investigate whether other ancient texts preserve wording for the 1/10 Mastema partition. Only then broaden the statistical baseline.

The existence of a lost physical medical book written by the biblical Noah has **not** been established.
