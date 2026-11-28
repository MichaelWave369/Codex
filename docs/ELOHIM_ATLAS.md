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
