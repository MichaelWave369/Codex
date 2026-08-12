"""Mothership Reader Bus v0.1 adapter for CODEX.

The adapter preserves CODEX's evidence-first boundary: lexical matches and source
spans are observations; any downstream synthesis remains interpretation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from codex.decoder import decode_text

MOTHERSHIP_READER_SCHEMA = "parallax.mothership.reader-envelope.v0.1"
ClaimClass = Literal[
    "computed",
    "source_observation",
    "symbolic_interpretation",
    "modeled_theoretical",
    "experimental",
]


@dataclass(slots=True)
class ReaderObservation:
    id: str
    claim_class: ClaimClass
    label: str
    value: Any
    source: str | None = None
    confidence: str | None = None
    note: str | None = None


@dataclass(slots=True)
class ReaderInterpretation:
    id: str
    framework: str
    claim_class: Literal[
        "symbolic_interpretation",
        "modeled_theoretical",
        "experimental",
    ]
    summary: str
    based_on: list[str] = field(default_factory=list)
    note: str | None = None


@dataclass(slots=True)
class ReaderProvenance:
    id: str
    kind: Literal["code", "dataset", "library", "source", "operator"]
    label: str
    version: str | None = None
    locator: str | None = None
    note: str | None = None


@dataclass(slots=True)
class ReaderWarning:
    code: str
    message: str
    severity: Literal["info", "caution", "blocked"] = "info"


@dataclass(slots=True)
class MothershipReaderEnvelope:
    schema: str
    reader: dict[str, str]
    input: dict[str, Any]
    observations: list[ReaderObservation]
    interpretations: list[ReaderInterpretation]
    provenance: list[ReaderProvenance]
    warnings: list[ReaderWarning]
    claim_boundary: str
    receipt_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical_payload(envelope: MothershipReaderEnvelope) -> str:
    payload = envelope.to_dict()
    payload.pop("receipt_hash", None)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _receipt_hash(envelope: MothershipReaderEnvelope) -> str:
    digest = hashlib.sha256(_canonical_payload(envelope).encode("utf-8")).hexdigest()
    return f"RDR-{digest[:16].upper()}"


def run_codex_reader(
    text: str,
    tradition_key: str,
    source: str = "input",
) -> MothershipReaderEnvelope:
    """Run a deterministic CODEX decode in the shared reader envelope."""
    result = decode_text(text=text, tradition_key=tradition_key, source=source)

    observations: list[ReaderObservation] = []
    interpretations: list[ReaderInterpretation] = []

    for index, match in enumerate(result.matches, start=1):
        observation_id = f"codex.pattern.{index}.{match.tag}"
        observations.append(
            ReaderObservation(
                id=observation_id,
                claim_class="source_observation",
                label=f"Lexical pattern match: {match.tag}",
                value={
                    "tag": match.tag,
                    "matched_terms": list(match.matched_terms),
                    "evidence": [asdict(span) for span in match.evidence],
                },
                source=result.source,
                confidence=match.confidence.level,
                note=match.confidence.rationale,
            )
        )
        interpretations.append(
            ReaderInterpretation(
                id=f"codex.interpretation.{index}.{match.tag}",
                framework=f"CODEX tradition adapter: {result.tradition_name}",
                claim_class="symbolic_interpretation",
                summary=match.interpretive_note,
                based_on=[observation_id],
                note=(
                    "Interpretation is downstream of explicit lexical evidence "
                    "and does not establish historical or metaphysical truth."
                ),
            )
        )

    envelope = MothershipReaderEnvelope(
        schema=MOTHERSHIP_READER_SCHEMA,
        reader={
            "id": "codex.symbolic_corpus",
            "name": "CODEX Symbolic Corpus Reader",
            "version": "0.1.0",
            "implementation": "Codex/src/codex/decoder.py",
        },
        input={
            "kind": "symbolic_corpus_excerpt",
            "payload": {
                "text": text,
                "tradition_key": tradition_key,
                "source": source,
            },
        },
        observations=observations,
        interpretations=interpretations,
        provenance=[
            ReaderProvenance(
                id="prov.codex.decoder",
                kind="code",
                label="CODEX deterministic decoder",
                locator="src/codex/decoder.py",
            ),
            ReaderProvenance(
                id="prov.codex.tradition",
                kind="dataset",
                label=result.tradition_name,
                locator=f"src/codex/traditions/{result.tradition_key}.py",
                note="Tradition adapter and lexicon extension selected by the operator.",
            ),
            ReaderProvenance(
                id="prov.codex.source",
                kind="source",
                label=source,
                note="Source label supplied for the analyzed excerpt.",
            ),
        ],
        warnings=[
            ReaderWarning(
                code="CODEX_HYPOTHESIS_ONLY",
                severity="info",
                message=result.cautionary_note,
            )
        ],
        claim_boundary=(
            "CODEX reports deterministic lexical evidence and explicitly labeled "
            "symbolic interpretation. It does not prove doctrine, historical "
            "relationships, universal tradition identity, psychology, or "
            "metaphysical truth."
        ),
    )
    envelope.receipt_hash = _receipt_hash(envelope)
    return envelope
