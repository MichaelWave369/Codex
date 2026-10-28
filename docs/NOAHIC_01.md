# NOAHIC-01: Ancient Knowledge Transmission Pilot (v0.1)

A narrow, falsifiable, **provenance-first** research adapter for the CODEX workbench.

The broader **Voynich Green Vessel Engine (VGVE)** and Voynich Scientific Alpha remain distinct systems. This initial implementation is a bounded, deterministic CODEX experiment whose structured receipts can later be connected to VGVE's provenance and counter-hypothesis gates. It is **not** an implementation of Voynich decipherment or ancient-language translation.

## Scope / research questions

1. How does the medicinal knowledge sequence in *Jubilees* 10 compare with the **later** *Sefer Asaf* / *Sefer Noah* prologue?
2. Which sources explicitly refer to a **book attributed to Noah**, versus merely sharing healing, angelic, Flood, or revelation motifs?
3. Do negative controls such as *Tobit*, 4Q560, 11Q11, and the *Paraphrase of Shem* reveal that the apparent overlap is broader than Noahic literature?

## Seed corpus

The curated seed has **9 source records**, each with work/locus, transmission caveat, date range, agent index, editorial motif tags, an ordered-event annotation when available, and provenance URLs.

| ID | Locus | Evidence classification | Key distinction |
|---|---|---|---|
| `jubilees_10` | Jubilees ch. 10 | Noah medicinal-book narrative | Angel is **unnamed** in this passage |
| `asaf_prologue` | Sefer Asaf medical prologue | Later Noah medicinal-book narrative | Names **Raphael**; post-Flood; Mount Lubar |
| `razim_prologue` | Sefer ha-Razim preface | Different revealed Noah-book tradition | **Raziel**, pre-Flood, celestial mysteries |
| `aramaic_levi_10_10` | Aramaic Levi 10:10 | Noah book cited in priestly material | Blood is **ritual**, not medical; wording in Greek witness |
| `genesis_apocryphon_1q20` | 1Q20 col. V 29+ | Probable Noah-book heading | Initial word restored; not a medicine-book identification |
| `tobit_6` | Tobit 3, 6, 11 | Negative control | Raphael/fish healing, **not** Noah's book |
| `qumran_4q560` | 4Q560 | Negative control | Fragmentary Aramaic incantation, **not** Noah |
| `qumran_11q11` | 11Q11 | Negative control | Protective psalm tradition, **not** Noah |
| `paraphrase_of_shem` | Nag Hammadi VII,1 | Negative control | Gnostic cosmic revelation to Shem, **not** Noah's remedies |

This corpus comprises **scholarly descriptions and human-assigned motifs**, not the text of any manuscript. It is intentionally small: a basis for falsifiable work, not an encyclopedic declaration.

## Running the pilot

Requires Python 3.12+ and an editable install of this CODEX repository:

```shell
pip install -e .[dev]
python -m codex.noahic validate
python -m codex.noahic list
python -m codex.noahic compare jubilees_10 asaf_prologue
python -m codex.noahic compare jubilees_10 tobit_6 --json
python -m codex.noahic matrix > noahic_matrix.json
pytest tests/test_noahic.py
```

## Mechanism and evidence firewall

- The engine computes **shared indexed motifs**, **shared named agents**, and the longest common subsequence of **manually assigned** narrative stages.
- The *Jubilees* versus *Sefer Asaf* pair has six matching annotated stages: affliction → prayer → angelic instruction → herbal remedies → written record → transmission to Shem.
- That ordering is an **annotator description** of English narrative summaries. It is not an independent linguistic or statistical discovery.
- **All** comparison reports include source URLs, witness-specific cautions, and an explicit `establishes_common_source: false` result.
- Do not equate "angel" with Raphael in Jubilees 10; do not equate Raziel with Raphael; do not equate ritual blood instructions with medicinal blood treatments.
- Later manuscript attribution does **not** constitute an authenticated chain back to the historical Noah.
- No speculation about medicinal effectiveness, supernatural causes of disease, universal translation from Noah, or Voynich connections may be promoted to a finding.
- Control comparisons are mandatory before claiming a distinctive shared narrative.
- No numerical similarity metric is given the semantics of a probability, certainty rating, or proof of influence.

## Research bibliography / source points

- *Book of Jubilees* 10: [Sefaria translation](https://www.sefaria.org/Book_of_Jubilees.10.1-13); Chontel Syfox, [“Israel's First Physician and Apothecary” (2018)](https://journals.sagepub.com/doi/full/10.1177/0951820718805635).
- John C. Reeves, [translations of Jellinek's Sefer Noah](https://pages.charlotte.edu/john-reeves/research-projects/medieval-jewish-pseudepigrapha/jellineks-sefer-noah/) (editorial compilation of **three distinct** compositions).
- Michael E. Stone, [“The Book(s) Attributed to Noah”](https://apocryphalstone.com/uploads/bibliography/362_Book%28s%29%20attributed.pdf), esp. Aramaic Levi 10:10 and Genesis Apocryphon col. V.
- SBL Press catalog, [*Sefer ha-Razim* translation and context](https://bibliovault.org/BV.book.epl?ISBN=9780891306153).
- Ida Fröhlich, [“Demons, Scribes, and Exorcists in Qumran”](https://arabist.hu/volumes/volume-23/ida-frohlich-2001/).
- *Oxford Handbook of the Psalms*, [11Q11 discussion](https://academic.oup.com/edited-volume/35006/chapter/298748176).
- [Nag Hammadi *Paraphrase of Shem*](https://ccdl.claremont.edu/digital/api/collection/cce/id/1552/download).

## Next research gate (not yet implemented)

1. Obtain licensed/permission-compatible **critical transcriptions**, including Aramaic/Hebrew/Coptic/Greek witness and line references; do not silently substitute modern translations for original text.
2. Add independent double-blind motif annotation with intercoder agreement.
3. Run unrelated healing narratives as baselines and shuffled-order controls to estimate generic-motif frequency.
4. Test rare textual n-grams, translation-aware alignment, documented textual variants, and chronological dependence *separately* from the symbolic VGVE operators.
5. Export fixed-schema source receipts and counterexamples to the VGVE/Field Atlas bridge **only after passing tests**.

**Status:** Research seed + deterministic comparison experiment. No decipherment claim.
