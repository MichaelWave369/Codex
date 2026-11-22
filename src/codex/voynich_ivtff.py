"""Provenance-preserving IVTFF reader and conservative Yale atlas bridge.

EVA is a transliteration scheme, not a translation. This module preserves
line IDs and checksums and does not assign Voynich glyphs semantic meaning.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from codex.voynich_sources import SCHEMA as ATLAS_SCHEMA

SCHEMA = "vgve-ivtff-index/0.1"
BRIDGE_SCHEMA = "vgve-ivtff-atlas-bridge/0.1"
SOURCE_URL = "https://www.voynich.nu/data/ZL3b-n.txt"
HEADER = re.compile(r"^#=IVTFF\s+(\S+)\s+(\S+)")
PAGE = re.compile(r"^<(f[^>,\s]+)>\s*(.*)$")
LOCUS = re.compile(r"^<(f[^>,\s]+),([^>]+)>\s*(.*)$")
FOLIO = re.compile(r"^f\d{1,3}[rv](?:[1-6])?$")


class TranscriptionError(ValueError):
    """The source or its link to an image atlas cannot be verified."""


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def _seal(value: dict[str, Any]) -> dict[str, Any]:
    value["receipt_sha256"] = hashlib.sha256(_canonical(value)).hexdigest()
    return value


def _verify(value: dict[str, Any], schema: str) -> None:
    if not isinstance(value, dict) or value.get("schema_version") != schema:
        raise TranscriptionError(f"Expected a {schema} document")
    signature = value.get("receipt_sha256")
    unsigned = {key: item for key, item in value.items() if key != "receipt_sha256"}
    if signature != hashlib.sha256(_canonical(unsigned)).hexdigest():
        raise TranscriptionError("Document receipt checksum mismatch")


def index_ivtff(raw: bytes, expected_sha256: str | None = None) -> dict[str, Any]:
    """Index ZL 3b lines from local bytes without storing any transcription text."""
    if len(raw) > 4_000_000:
        raise TranscriptionError("Unexpectedly large IVTFF input")
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256.lower():
        raise TranscriptionError("IVTFF source SHA-256 does not match expected bytes")
    try:
        lines = raw.decode("utf-8-sig").splitlines()
    except UnicodeDecodeError as error:
        raise TranscriptionError("Expected UTF-8 IVTFF source bytes") from error
    if not lines:
        raise TranscriptionError("Empty IVTFF document")
    match = HEADER.match(lines[0])
    if not match or match.group(1) != "Eva-" or match.group(2) != "2.0":
        raise TranscriptionError("Expected IVTFF Eva- 2.0 header")

    pages: list[dict[str, Any]] = []
    seen_pages: set[str] = set()
    seen_loci: set[str] = set()
    current: dict[str, Any] | None = None
    for line_number, line in enumerate(lines[1:], start=2):
        if not line.strip() or line.startswith("#"):
            continue
        page_match = PAGE.match(line)
        if page_match:
            key, trailer = page_match.groups()
            if key in seen_pages:
                raise TranscriptionError(f"Duplicate page identifier: {key}")
            seen_pages.add(key)
            current = {
                "folio_id": key,
                "source_line": line_number,
                "page_variables_raw_sha256": hashlib.sha256(trailer.encode("utf-8")).hexdigest(),
                "loci": [],
            }
            pages.append(current)
            continue
        locus_match = LOCUS.match(line)
        if not locus_match:
            # Preserve unrecognized records as a failure, not silent data loss.
            raise TranscriptionError(f"Unrecognized IVTFF line {line_number}")
        key, locus_marker, body = locus_match.groups()
        if current is None:
            raise TranscriptionError(f"Locus before page at line {line_number}")
        prefix = key.split(".", 1)[0]
        if prefix != current["folio_id"]:
            raise TranscriptionError(f"Locus belongs to another folio at line {line_number}")
        if key in seen_loci:
            raise TranscriptionError(f"Duplicate locus identifier: {key}")
        if not body.strip():
            raise TranscriptionError(f"Empty transliteration at line {line_number}")
        seen_loci.add(key)
        current["loci"].append(
            {
                "locus_id": key,
                "locus_marker": locus_marker,
                "source_line": line_number,
                "payload_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "literal_characters": len(body),
                "question_mark_count": body.count("?"),
                "square_bracket_count": body.count("["),
            }
        )
    if not pages or not seen_loci:
        raise TranscriptionError("No IVTFF folio and locus data found")
    output = {
        "schema_version": SCHEMA,
        "title": "Zandbergen-Landini ZL 3b (EVA) structural index",
        "source_url": SOURCE_URL,
        "source_sha256": digest,
        "source_bytes": len(raw),
        "format": "IVTFF 2.0",
        "alphabet": "Eva-",
        "transliteration_edition": "ZL 3b",
        "edition_date": "2025-05-13",
        "page_count": len(pages),
        "locus_count": len(seen_loci),
        "pages": pages,
        "claim_boundary": (
            "Transliteration is not translation. No glyph semantics, plant identity, "
            "spiritual meaning, or historical decipherment is inferred."
        ),
    }
    return _seal(output)


def bridge_atlas(index: dict[str, Any], atlas: dict[str, Any]) -> dict[str, Any]:
    """Compare *literal* folio labels, never inventing aliases or page mappings."""
    _verify(index, SCHEMA)
    _verify(atlas, ATLAS_SCHEMA)
    matched: dict[str, list[dict[str, Any]]] = {}
    for canvas in atlas.get("canvases", []):
        if canvas.get("label_status") != "unambiguous":
            continue
        key = canvas.get("folio_key")
        if not isinstance(key, str) or not FOLIO.fullmatch(key):
            continue
        matched.setdefault(key, []).append(canvas)

    mappings = []
    for page in index["pages"]:
        key = page["folio_id"]
        candidates = matched.get(key, [])
        status = (
            "UNMAPPED"
            if not candidates
            else "MULTIPLE_EXPLICIT_CANVASES"
            if len(candidates) > 1
            else "EXACT_LABEL_MATCH"
        )
        mappings.append(
            {
                "folio_id": key,
                "status": status,
                "locus_count": len(page["loci"]),
                "canvas_ids": [item["canvas_id"] for item in candidates],
                "image_urls": [item["image_url"] for item in candidates],
            }
        )
    counts = {
        status: sum(record["status"] == status for record in mappings)
        for status in ("EXACT_LABEL_MATCH", "MULTIPLE_EXPLICIT_CANVASES", "UNMAPPED")
    }
    return _seal(
        {
            "schema_version": BRIDGE_SCHEMA,
            "transliteration_source_sha256": index["source_sha256"],
            "transliteration_receipt_sha256": index["receipt_sha256"],
            "manifest_sha256": atlas["manifest_sha256"],
            "atlas_receipt_sha256": atlas["receipt_sha256"],
            "mapping_counts": counts,
            "mappings": mappings,
            "review_status": "METADATA CROSSWALK ONLY; HUMAN SOURCE CHECK REQUIRED",
            "limitations": (
                "Exact label match does not establish image-to-text alignment, "
                "physical foliation, reliable transcription, or glyph meaning. "
                "Split/combined foldout labels are not silently normalized."
            ),
        }
    )


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, result: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {path} ({result['receipt_sha256']})")


def main() -> None:
    """Offline deterministic IVTFF indexing and optional Yale IIIF crosswalk."""
    parser = argparse.ArgumentParser(description="VGVE IVTFF structural-source bridge")
    actions = parser.add_subparsers(dest="command", required=True)
    source = actions.add_parser("index")
    source.add_argument("file", type=Path)
    source.add_argument("--sha256", help="Optional expected raw file SHA-256")
    source.add_argument("--out", type=Path, required=True)
    bridge = actions.add_parser("bridge")
    bridge.add_argument("index", type=Path)
    bridge.add_argument("atlas", type=Path)
    bridge.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "index":
            result = index_ivtff(args.file.read_bytes(), expected_sha256=args.sha256)
        else:
            result = bridge_atlas(_load(args.index), _load(args.atlas))
    except (TranscriptionError, json.JSONDecodeError) as error:
        parser.error(str(error))
    _write(args.out, result)


if __name__ == "__main__":
    main()
