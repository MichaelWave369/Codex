"""Build a provenance-first atlas from Yale's saved IIIF Voynich manifest.

This parses IIIF Presentation 2 and 3 JSON offline. It never guesses content,
transcribes glyphs, translates writing, downloads images, or assigns operators.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from codex.voynich_engine import OPERATORS

SCHEMA = "vgve-folio-atlas/0.1"
ASSIGNMENT_SCHEMA = "vgve-blind-annotation/0.1"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
CATALOG_URL = "https://collections.library.yale.edu/catalog/2002046"
FOLIO_PATTERN = re.compile(r"(?<![A-Za-z0-9])(?:f(?:olio)?[.\s:-]*)?(\d{1,3}[rv](?:[1-6])?)(?![A-Za-z0-9])", re.I)


class AtlasError(ValueError):
    """A manifest or annotation request was ambiguous or incomplete."""


def _canonical(item: dict[str, Any]) -> bytes:
    return json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _receipt(item: dict[str, Any]) -> dict[str, Any]:
    item["receipt_sha256"] = hashlib.sha256(_canonical(item)).hexdigest()
    return item


def _label(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        for item in value:
            result = _label(item)
            if result:
                return result
    if isinstance(value, dict):
        # IIIF v3 language maps. Avoid dependence on original JSON key order.
        for key in ("en", "none", *sorted(key for key in value if key not in {"en", "none"})):
            result = _label(value.get(key))
            if result:
                return result
    return ""


def _canvas_image(canvas: dict[str, Any], *, version: int) -> str | None:
    if version == 2:
        images = canvas.get("images", [])
        if not isinstance(images, list):
            return None
        for image in images:
            if not isinstance(image, dict):
                continue
            resource = image.get("resource", {})
            if isinstance(resource, dict):
                url = resource.get("@id") or resource.get("id")
                if isinstance(url, str) and url.startswith("https://"):
                    return url
        return None

    pages = canvas.get("items", [])
    if not isinstance(pages, list):
        return None
    for page in pages:
        if not isinstance(page, dict):
            continue
        for annotation in page.get("items", []):
            if not isinstance(annotation, dict) or annotation.get("motivation") != "painting":
                continue
            body = annotation.get("body", {})
            if isinstance(body, dict):
                url = body.get("id") or body.get("@id")
                if isinstance(url, str) and url.startswith("https://"):
                    return url
    return None


def atlas_from_manifest(raw: bytes) -> dict[str, Any]:
    """Index documented folio labels without fabricating unavailable mappings."""
    try:
        manifest = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as error:
        raise AtlasError("Manifest must be valid UTF-8 JSON") from error
    if not isinstance(manifest, dict):
        raise AtlasError("Manifest must be a JSON object")
    manifest_id = manifest.get("id") or manifest.get("@id")
    if not isinstance(manifest_id, str) or manifest_id.rstrip("/") != MANIFEST_URL:
        raise AtlasError("Only the Yale Beinecke MS 408 manifest (2002046) is supported")
    if isinstance(manifest.get("items"), list):
        version = 3
        canvases = manifest["items"]
    else:
        version = 2
        sequences = manifest.get("sequences", [])
        canvases = (
            sequences[0].get("canvases", [])
            if isinstance(sequences, list) and sequences and isinstance(sequences[0], dict)
            else []
        )
    if not isinstance(canvases, list) or not canvases:
        raise AtlasError("IIIF manifest contains no canvases")
    seen: set[str] = set()
    entries = []
    for index, canvas in enumerate(canvases, start=1):
        if not isinstance(canvas, dict):
            raise AtlasError(f"Canvas {index} must be an object")
        canvas_id = canvas.get("id") or canvas.get("@id")
        if not isinstance(canvas_id, str) or not canvas_id.startswith("https://"):
            raise AtlasError(f"Canvas {index} lacks an HTTPS IIIF identifier")
        if canvas_id in seen:
            raise AtlasError(f"Duplicate IIIF canvas identifier: {canvas_id}")
        seen.add(canvas_id)
        label = _label(canvas.get("label"))
        candidates = sorted({f"f{match.lower()}" for match in FOLIO_PATTERN.findall(label)})
        entries.append(
            {
                "order": index,
                "canvas_id": canvas_id,
                "label": label,
                "folio_key": candidates[0] if len(candidates) == 1 else None,
                "folio_candidates": candidates,
                "label_status": (
                    "unambiguous" if len(candidates) == 1 else "ambiguous"
                    if candidates else "unresolved"
                ),
                "image_url": _canvas_image(canvas, version=version),
            }
        )
    atlas = {
        "schema_version": SCHEMA,
        "title": "Beinecke MS 408: source-only atlas",
        "institution": "Yale University, Beinecke Rare Book & Manuscript Library",
        "manifest_url": MANIFEST_URL,
        "catalog_url": CATALOG_URL,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "iiif_presentation_version": version,
        "canvas_count": len(entries),
        "canvases": entries,
        "boundary": (
            "Canvas metadata and literal labels only. This atlas contains no decipherment, "
            "glyph reading, automatic visual interpretation, or historical hypothesis validation."
        ),
    }
    return _receipt(atlas)


def blank_assignments(atlas: dict[str, Any], folios: list[str]) -> dict[str, Any]:
    """Make empty observation sheets; withhold interpretive hypotheses."""
    if atlas.get("schema_version") != SCHEMA:
        raise AtlasError("Not a VGVE folio atlas")
    if not folios:
        raise AtlasError("Specify one or more --folio values")
    index: dict[str, list[dict[str, Any]]] = {}
    for canvas in atlas.get("canvases", []):
        if canvas.get("label_status") == "unambiguous":
            key = canvas["folio_key"]
            index.setdefault(key, []).append(canvas)
    assignments = []
    for requested in folios:
        key = requested.lower().strip()
        if not key.startswith("f"):
            key = f"f{key}"
        matches = index.get(key, [])
        if len(matches) != 1:
            raise AtlasError(f"{key} has {len(matches)} unique, verifiable canvas mappings")
        canvas = matches[0]
        if canvas["image_url"] is None:
            raise AtlasError(f"{key} has no image URL in the manifest")
        assignments.append(
            {
                "folio": key,
                "canvas_id": canvas["canvas_id"],
                "image_url": canvas["image_url"],
                "source_label": canvas["label"],
                "observer_id": "",
                "observations": [],
                "operator_sequence": [],
                "alternative_explanations": [],
                "status": "UNANNOTATED",
            }
        )
    if len(set(folios)) != len(folios):
        raise AtlasError("Do not request duplicate folios")
    result = {
        "schema_version": ASSIGNMENT_SCHEMA,
        "catalog_url": CATALOG_URL,
        "manifest_sha256": atlas["manifest_sha256"],
        "blinding": (
            "Reviewer is not given the target Source-to-embodiment hypothesis or "
            "another reviewer's annotations. Not blinded to manuscript identity."
        ),
        "allowed_operators": sorted(OPERATORS),
        "assignments": assignments,
        "review_status": "PENDING INDEPENDENT HUMAN ANNOTATION",
        "boundary": "No interpretations are auto-generated; do not count blanks as evidence.",
    }
    return _receipt(result)


def _save(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """Offline CLI for manifest indexing and empty study assignment generation."""
    parser = argparse.ArgumentParser(description="Voynich primary-source atlas, offline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    ingest = subparsers.add_parser("index", help="Index a previously downloaded Yale IIIF JSON")
    ingest.add_argument("manifest", type=Path)
    ingest.add_argument("--out", type=Path, required=True)
    blind = subparsers.add_parser("assign", help="Generate hypothesis-blind blank annotation sheets")
    blind.add_argument("atlas", type=Path)
    blind.add_argument("--folio", action="append", required=True)
    blind.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "index":
            result = atlas_from_manifest(args.manifest.read_bytes())
        else:
            result = blank_assignments(
                json.loads(args.atlas.read_text(encoding="utf-8")), args.folio
            )
    except (AtlasError, json.JSONDecodeError) as error:
        parser.error(str(error))
    _save(args.out, result)
    print(f"{args.out}: {result['receipt_sha256']}")


if __name__ == "__main__":
    main()
