"""NOAHIC-03: witness-aware, provenance-gated textual alignment.

No ancient text is bundled. Exact matches are descriptive, never evidence
by themselves of manuscript descent, authenticity, or recovered lost books.
"""

from __future__ import annotations

import argparse
import json
import unicodedata
from importlib import resources
from pathlib import Path
from typing import Any

SCHEMA = "noahic-03/witness-registry-v0.1"
TRANSCRIPTION_SCHEMA = "noahic-03/local-excerpt-v0.1"
LANGUAGES = {"he": "hebrew", "gez": "ethiopic"}
NON_ORIGINAL = {
    "modern_translation_not_original_witness",
    "ancient_version_in_translation",
}
CAUTION = (
    "Identical Unicode tokens are not an authenticated historical parallel. "
    "The original Hebrew wording of Jubilees 10 is not present among the "
    "identified extant Hebrew fragments in this witness registry; do not "
    "back-translate Ge'ez or mistake modern Hebrew versions for original text."
)


def load_registry() -> dict[str, Any]:
    """Load the source-linked manuscript witness registry."""
    path = resources.files("codex.data").joinpath("noahic_witness_registry_v0_3.json")
    registry = json.loads(path.read_text(encoding="utf-8"))
    validate_registry(registry)
    return registry


def validate_registry(registry: dict[str, Any]) -> None:
    """Validate witness IDs, covered loci, and explicit transmission status."""
    if registry.get("schema") != SCHEMA:
        raise ValueError("Unrecognized witness registry schema")
    entries = registry.get("witnesses")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Registry witnesses missing")
    seen: set[str] = set()
    for entry in entries:
        ident = entry.get("id")
        if not isinstance(ident, str) or not ident or ident in seen:
            raise ValueError("Missing or duplicate witness ID")
        seen.add(ident)
        if LANGUAGES.get(entry.get("language")) != entry.get("script"):
            raise ValueError(f"Inconsistent language/script for {ident}")
        for field in (
            "work_id",
            "locus",
            "witness_type",
            "relationship_to_composition",
            "coverage",
            "ingestion",
            "license_status",
            "license_note",
            "edition",
            "notes",
        ):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                raise ValueError(f"Missing {field}: {ident}")
        if not entry.get("source_url", "").startswith("https://"):
            raise ValueError(f"Missing HTTPS source: {ident}")
        if entry["coverage"] not in {
            "attested",
            "not_attested_in_identified_extant_fragments",
        }:
            raise ValueError(f"Invalid coverage status: {ident}")
        if entry["coverage"] != "attested" and entry["ingestion"] != "unavailable":
            raise ValueError(f"Unattested locus must not be ingestible: {ident}")
        if entry["relationship_to_composition"] == "modern_translation_not_original_witness":
            if entry["witness_type"] != "modern_hebrew_version":
                raise ValueError(f"Translation falsely labeled witness: {ident}")


def witness_plan(registry: dict[str, Any]) -> dict[str, Any]:
    """Report actual feasibility without inventing equivalent source texts."""
    validate_registry(registry)
    records = registry["witnesses"]
    left, right = registry["target_pair"]
    candidates = [
        {
            "witness_id": entry["id"],
            "work_id": entry["work_id"],
            "language": entry["language"],
            "coverage": entry["coverage"],
            "source_url": entry["source_url"],
            "relationship": entry["relationship_to_composition"],
            "ingestion": entry["ingestion"],
            "license_status": entry["license_status"],
        }
        for entry in records
        if entry["work_id"] in (left, right)
    ]
    original_witnesses = [
        entry
        for entry in records
        if entry["coverage"] == "attested"
        and entry["relationship_to_composition"] not in NON_ORIGINAL
    ]
    direct_pair = any(
        first["work_id"] == left
        and second["work_id"] == right
        and first["language"] == second["language"]
        for first in original_witnesses
        for second in original_witnesses
    )
    return {
        "target_pair": [left, right],
        "registered_witnesses": candidates,
        "direct_original_language_pair_available": direct_pair,
        "unverified_gap": (
            "No identified Qumran Hebrew manuscript currently listed as preserving "
            "Jubilees chapter 10; this is not a claim of absolute absence."
        ),
        "next_action": (
            "Obtain rights-cleared original-language transcriptions with line/locus "
            "and edition IDs; use an explicitly translation-aware philological review "
            "for Ge'ez Jubilees versus Hebrew Sefer Asaf."
        ),
        "warning": CAUTION,
    }


def _unicode_tokens(value: str) -> list[str]:
    """Tokenize Unicode letter sequences, preserving combining marks."""
    text = unicodedata.normalize("NFC", value)
    result: list[str] = []
    current: list[str] = []
    for char in text:
        category = unicodedata.category(char)
        if category.startswith("L") or (category.startswith("M") and current):
            current.append(char)
        elif current:
            result.append("".join(current))
            current = []
    if current:
        result.append("".join(current))
    return result


def _script_of(token: str) -> str:
    """Conservatively recognize Hebrew and Ethiopic script; reject ambiguity."""
    seen: set[str] = set()
    for char in token:
        value = ord(char)
        if 0x0590 <= value <= 0x05FF:
            seen.add("hebrew")
        elif 0x1200 <= value <= 0x139F or 0x2D80 <= value <= 0x2DDF:
            seen.add("ethiopic")
        elif unicodedata.category(char).startswith("L"):
            seen.add("other")
    return next(iter(seen)) if len(seen) == 1 else "mixed_or_unknown"


def _validate_local_excerpt(excerpt: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    """Reject unsupported script, missing provenance, and placeholder text."""
    if excerpt.get("schema") != TRANSCRIPTION_SCHEMA:
        raise ValueError("Unsupported excerpt schema")
    index = {w["id"]: w for w in registry["witnesses"]}
    ident = excerpt.get("witness_id")
    if ident not in index:
        raise ValueError("Unregistered source witness")
    witness = index[ident]
    if witness["coverage"] != "attested":
        raise ValueError("A missing source-locus cannot supply a transcription")
    for key in ("locus", "editor", "transcription_note"):
        if not isinstance(excerpt.get(key), str) or not excerpt[key].strip():
            raise ValueError(f"Missing local provenance field: {key}")
    if not isinstance(excerpt.get("text"), str) or not excerpt["text"].strip():
        raise ValueError("No transcription supplied")
    if excerpt.get("source_url") != witness["source_url"]:
        raise ValueError("Source URL must match registered edition")
    tokens = _unicode_tokens(excerpt["text"])
    if not tokens or any(_script_of(token) != witness["script"] for token in tokens):
        raise ValueError("Excerpt has absent, mixed, or mismatched script")
    return witness


def compare_local_excerpts(
    left: dict[str, Any], right: dict[str, Any], registry: dict[str, Any]
) -> dict[str, Any]:
    """Use exact n-grams only when witnesses and language are comparable."""
    a = _validate_local_excerpt(left, registry)
    b = _validate_local_excerpt(right, registry)
    reasons = []
    if a["id"] == b["id"]:
        reasons.append("Same witness ID; not independent comparison")
    if a["language"] != b["language"]:
        reasons.append("Different source languages: automatic lexical match prohibited")
    if a["relationship_to_composition"] in NON_ORIGINAL:
        reasons.append("Left is a translation/version, not original composition wording")
    if b["relationship_to_composition"] in NON_ORIGINAL:
        reasons.append("Right is a translation/version, not original composition wording")
    if a["license_status"] in {"rights_review_required", "cc_by_sa_verify"}:
        reasons.append("Left edition has unresolved reuse permissions")
    if b["license_status"] in {"rights_review_required", "cc_by_sa_verify"}:
        reasons.append("Right edition has unresolved reuse permissions")
    result: dict[str, Any] = {
        "left_witness": a["id"],
        "right_witness": b["id"],
        "status": "blocked" if reasons else "provisional_lexical_only",
        "reasons": reasons,
        "identical_bigrams": [],
        "original_language_dependence_proven": False,
        "warning": CAUTION,
    }
    if reasons:
        return result
    left_tokens = _unicode_tokens(left["text"])
    right_tokens = _unicode_tokens(right["text"])
    left_bigrams = {(left_tokens[i], left_tokens[i + 1]) for i in range(len(left_tokens) - 1)}
    right_bigrams = {(right_tokens[i], right_tokens[i + 1]) for i in range(len(right_tokens) - 1)}
    result["identical_bigrams"] = [list(pair) for pair in sorted(left_bigrams & right_bigrams)]
    return result


def main(argv: list[str] | None = None) -> int:
    """Entry point: python -m codex.noahic_witness [plan|list|validate|compare]."""
    parser = argparse.ArgumentParser(description="NOAHIC-03 witness gate")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan")
    commands.add_parser("list")
    commands.add_parser("validate")
    comp = commands.add_parser("compare")
    comp.add_argument("left", type=Path)
    comp.add_argument("right", type=Path)
    args = parser.parse_args(argv)
    registry = load_registry()
    if args.command == "validate":
        print(f"VALID: {SCHEMA}; {len(registry['witnesses'])} witnesses")
    elif args.command == "plan":
        print(json.dumps(witness_plan(registry), indent=2))
    elif args.command == "list":
        for entry in registry["witnesses"]:
            print(
                f"{entry['id']} | {entry['language']} | {entry['coverage']} | "
                f"{entry['relationship_to_composition']}"
            )
    else:
        a = json.loads(args.left.read_text(encoding="utf-8"))
        b = json.loads(args.right.read_text(encoding="utf-8"))
        print(json.dumps(compare_local_excerpts(a, b, registry), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
