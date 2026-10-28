# NOAHIC-02: Distinctive Feature Audit and Control Gate

**Purpose:** Audit a small set of witness-located narrative details in *Jubilees* 10 and the later Hebrew *Sefer Asaf / Sefer Noah* medical prologue. This is not a manuscript decipherment, numerical probability model, textual stemma, or validation of ancient medical claims.

## Why this rung exists

NOAHIC-01 indexed nine source records and demonstrated manually assigned six-stage overlap between *Jubilees* and the later medical prologue. NOAHIC-02 asks a narrower question: which **particular** details match, which change their **narrative function**, and which are **explicitly absent only within a specified passage**?

The distinctive candidate is the arrangement under Mastema in which **one tenth** of the spirits remain active. *Jubilees* 10:9/11 describes nine parts restrained and one left; Reeves's translation of the Sefer Asaf prologue depicts one tenth left before Mastema. This is a meaningful textual parallel, **not** an independent measurement of historical transmission.

**Mount Lubar offers a useful disagreement**: in *Jubilees* 10:15 it is Noah's burial place; in the prologue it identifies where the book was given to Noah. Sharing a named location does not make the location's function identical.

**Raphael is explicitly named only in the later prologue**. Jubilees 10:10-12 names no Raphael in that passage. This distinction is not a claim that Raphael never appears elsewhere in Jubilees.

## Run

```shell
pip install -e .[dev]
python -m codex.noahic_feature_audit validate
python -m codex.noahic_feature_audit compare
python -m codex.noahic_feature_audit compare --json
python -m codex.noahic_feature_audit controls
pytest tests/test_noahic_feature_audit.py
```

The review data is in `src/codex/data/noahic_feature_audit_v0_2.json`. It provides nine paired feature annotations, edition/source URLs, locus-level references, interpretative notes, and explicitly **unreviewed** controls. Status values are `attested`, `not_attested_in_locus`, and `unreviewed`. They must not be silently collapsed.

## Feature classifications

- **Shared with same narrative role:** Noah's descendants afflicted; Noah's prayer; Mastema; one tenth of spirits remains; plant-based healing; the book going to Shem.
- **Shared name with different narrative role:** Mount Lubar (burial vs. medical revelation).
- **Passage-level asymmetries:** Raphael explicitly named; later multilingual medical-transmission genealogy.

These are **curator classifications from secondary English-language readings**, not an independent algorithmically discovered collation in Hebrew, Aramaic, Ethiopic or Greek. Even the proposed distinctive features may prove common in independent literature.

## Provenance

- [Jubilees 10:1-15, R. H. Charles translation (1913)](https://axialcommons.org/read/jubilees-charles-1913/3/). Loci are from Charles; different sites/editions may number passages differently.
- [John C. Reeves, translation of Jellinek's Sefer Noah, composition 1 (Sefer Asaf prologue)](https://pages.charlotte.edu/john-reeves/research-projects/medieval-jewish-pseudepigrapha/jellineks-sefer-noah/). Reeves specifies Jellinek combined **three conceptually related but distinct works**.
- [Posen Library: The Book of Asaf](https://www.posenlibrary.com/entry/book-asaf). Composition date and manuscript witness are **much later** than Jubilees, and the origin story is a literary claim.

## Rarity gate: no green shortcut

The seven other NOAHIC-01 records, including Tobit, Qumran fragments, and the Gnostic Paraphrase of Shem, are *unreviewed for this exact nine-feature questionnaire*. They are not automatic negative examples.

As a result, the tool **always reports `rarity_evaluable=false`** and **`historical_dependence_established=false`**. A reader may verify the shared details in translations, but a shared detail's prevalence has not been sampled or estimated. No false independent probability is computed from curated motifs or later copying.

## Next research gate

1. Acquire rights-compatible scholarly transcription/translation pairs and exact manuscript IDs, including source-language morphology and textual variants.
2. Pre-register an annotation protocol and a representative reference set of other healing, exorcism and angelic-revelation narratives.
3. Double-annotate passages independently, note disagreements, and measure inter-annotator reliability.
4. Compare rarer lexical sequences and exact wording *within specific witness languages*, not only English translations.
5. Make a falsification report identifying alternative literary sources and possible direct dependence on Jubilees, rather than assuming a lost intermediary.
6. Only after independently validating source material, consider a reviewed export to VGVE or Field Atlas.

The historical question is whether later versions **adapt an earlier documented story**, or depend on some intermediary; the existence of a medical book written by the biblical Noah is not demonstrated.
