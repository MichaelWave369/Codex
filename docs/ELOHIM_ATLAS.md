# Elohim creation atlas — pilot v0.1

Research question: Who is addressed in Genesis 1:26, what can the surviving
sources establish, and which later accounts actually supply names or counts?

This local-first, dependency-free research module records **curated textual
observations**, not automatic translations, historical events or metaphysical facts.
It is complementary to the CODEX symbolic decoder and is deliberately separate
from lexical pattern scoring.

## Use

```bash
python -m codex.elohim_atlas list
python -m codex.elohim_atlas show genesis-1
python -m codex.elohim_atlas compare genesis-1 apocryphon-john
python -m codex.elohim_atlas compare enki-ninmah atrahasis
```

The records have stable IDs, tradition, passage locator, external source URL,
relationship to the research question, human-annotated motifs, observation,
nullable count, explicit count scope, and a limitation. The comparison returns
sorted intersections and differences, not similarity scores or identity matches.
No remote request occurs during execution. Modern translations are linked, not
redistributed. Sources are reference links, not checksum-pinned manuscript images.

## Findings and competing explanations

* Genesis 1:26 uses first-person plural speech; 1:27 attributes creation using
  singular grammar. The plural noun form Elohim alone is not proof of multiple
  gods. The actual addressee count is unknown.
* Divine council, self-deliberation and later Trinitarian readings must remain
  distinct hypotheses; Philo's assistant interpretation is reception evidence.
* Deuteronomy 32:8 has an attested textual variant. That establishes variation
  in that verse, not the deletion of an explanatory passage in Genesis.
* Sumerian and Akkadian formation narratives provide comparative material; the
  later Apocryphon of John gives its own seven-power model. The number cannot
  be carried into another tradition.

## Research lanes

Initial records cover Hebrew, Sumerian, Akkadian, Hellenistic Jewish and Gnostic
material. Expand to Ugaritic, Egyptian, Greek, Enochian and rabbinic witnesses
only when an edition, passage and contextual interpretation can be documented.
The lanes are not mutually exclusive religious categories.

Next stage: add a witness-level registry (edition, manuscript ID, date range,
language, translation attribution, textual variants), independent annotations,
negative controls, and an entity/role graph that distinguishes local aliases
from cross-cultural analogies. Record competing explanations and preserve
contradictory evidence. Do not infer common origin from motif overlap.

## Acceptance boundaries

Unknown values stay null. Counts belong to named groups in specific sources.
A later reinterpretation cannot become an earlier manuscript witness. A link
does not imply that a physical manuscript has been inspected. No claim of
missing Genesis chapters, genetic engineering, or literal divine ancestry is
established by this pilot. No claim about what believers should believe.

## Phase 2: original-language and witness pilot

```bash
python -m codex.elohim_language lexicon
python -m codex.elohim_language lexicon צלם
python -m codex.elohim_language grammar
python -m codex.elohim_language witnesses
```

Nine curated Hebrew forms from Genesis 1:26–27 are searchable by exact ID,
unpointed surface form or lemma. This is not an automatic morphological parser.
Hebrew vowel and cantillation marks are ignored during lookup; Greek is preserved.
The grammar report separates first-person plural speech, singular narration,
plural objects, and the plural-form noun Elohim. None establishes a headcount.

The Deuteronomy 32:8 pilot records three reported reading families separately:
Masoretic sons of Israel, Qumran sons of God, and Greek angels of God.
See [Emanuel Tov's textual comparison](https://thetorah.com/article/the-sons-of-israel-or-god-deuteronomy-32-8)
and the [official 4Q37 catalog](https://www.deadseascrolls.org.il/explore-the-archive/manuscript/4Q37-1).
The registry is not an exhaustive critical apparatus. Other Greek readings
require separate witness-level documentation. No original reading is reconstructed
automatically. No manuscript image transcription has been independently verified.
The Hebrew readings are reported lexical forms, not diplomatic transcriptions.

Next: extend to the Genesis 3:22 and 11:7 plural passages, Isaiah 6:8,
and Genesis 5:1–3 parentage parallels; obtain edition-level anchors and
independent transcription review before expanding to cross-cultural entity graphs.

## Phase 3: source-scoped relationship graph

```bash
python -m codex.elohim_graph export
python -m codex.elohim_graph neighbors elohim
python -m codex.elohim_graph neighbors namma
python -m codex.elohim_graph --analogies export
```

The pilot exports 21 nodes across four traditions, 18 textual relationships,
and two optional comparative analogies. Node kinds distinguish narrative
entities, collectives, titles and lexical terms. Edges carry a passage locator,
a reference URL and a status. The source URLs are reference editions or
scholarly discussions, not independently verified manuscript transcriptions.
The Ugaritic edge cites a scholarly discussion of KTU 1.4 VI 46. Analogy edges
identify both passages; consult the corresponding textual edges for the
other reference edition.

For example, Psalm 82 uses Elohim of both its presiding figure and the
assembly; connecting them to a lexical node is not an assertion that they
are identical. Exodus 6:2–3 and Genesis 14:22 supply context-specific title
relationships, not proof of an invariant historical identity across cultures.
The Sumerian and Gnostic creation relationships remain distinct.

Neighbor queries return direct edges only. The graph never resolves a shared
title into a common entity, performs transitive identity inference, or assigns
an identity or count to the addressees of Genesis 1:26. Analogies are
excluded by default and opt in explicitly. They are annotations, not proof
of dependence. The graph is selective, not a complete pantheon or a claim
about the historical existence of the figures.

Next: attach explicitly scoped numerical claims to passages and editions;
distinguish group size, cosmological structure and symbolic numbers.

## Phase 4: numerical evidence registry

```bash
python -m codex.elohim_numbers list
python -m codex.elohim_numbers match 7
python -m codex.elohim_numbers contrast genesis-rest john-long-powers
python -m codex.elohim_numbers contrast john-short-angels john-long-angels
```

Nine records retain numerical value (nullable), unit, referent scope, edition,
passage locator, source URL and basis (explicit, reported reading, doctrinal
or unknown). The seventh day of Genesis is an ordinal, not a count of beings:
it serves as a negative control against the seven powers in the long
Apocryphon of John. Exact matches are descriptive, not significance tests.

The short and long Apocryphon recensions report 360 and 365 angelic beings
respectively in their accounts of the hierarchy. Preserve each scope; the
arithmetic difference does not establish that the two count identical groups.
See the [short](https://www.gnosis.org/naghamm/apocjn-short.html) and
[long](https://www.gnosis.org/naghamm/apocjn-long.html) translations by
Waldstein and Wisse. The 70 sons of Athirat entry uses the conventional
reading of KTU 1.4 VI 46, not a settled census of all Ugaritic gods.
The [Charles translation of 1 Enoch 6:6](https://openscrollproject.org/app/ancient/1EN-6)
reports 200 descending Watchers, not creation participants.
Catholic catechetical paragraphs 253–255 describe three divine persons of
one God, not three gods or a manuscript count in Genesis.

No count of Genesis 1:26 addressees is supplied by these records. This is a
small purposive seed, not a representative corpus. No p-values, digit-root
significance, inferred common identity or historical dependence are produced.
Future statistical work requires independent annotations, a defined sampling
frame, preregistered hypotheses, and correction for multiple comparisons.
Reference links were checked via indexed source excerpts; manuscript images
and full critical apparatus were not independently verified.
