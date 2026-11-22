"""Preregistered, source-locked Voynich visual/text pilot.

No glyph meanings are inferred. The preregistered primary endpoint measures
whether independent reviewers' consensus FLOW labels track folio locus counts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

from codex.voynich_ivtff import BRIDGE_SCHEMA
from codex.voynich_ivtff import SCHEMA as INDEX_SCHEMA
from codex.voynich_ivtff import _verify as verify_source
from codex.voynich_review import (
    PROTOCOL_SCHEMA,
    ReviewError,
    _checked_annotations,
    compare_reviews,
    create_protocol,
)
from codex.voynich_review import _verify as verify_review
from codex.voynich_sources import SCHEMA as ATLAS_SCHEMA

PLAN_SCHEMA = "vgve-preregistered-pilot/0.1"
RESULT_SCHEMA = "vgve-pilot-result/0.1"
SEED = "vgve-pilot-v1:2026-11-22"
ALPHA = 0.05
SHUFFLES = 999
DEFAULT_SAMPLE_SIZE = 32


class StudyError(ValueError):
    """An invalid source lock, study plan, or reviewer input blocks inference."""


def _bytes(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )


def _seal(data: dict[str, Any]) -> dict[str, Any]:
    data["receipt_sha256"] = hashlib.sha256(_bytes(data)).hexdigest()
    return data


def _verify(data: dict[str, Any], schema: str) -> None:
    if not isinstance(data, dict) or data.get("schema_version") != schema:
        raise StudyError(f"Expected document schema: {schema}")
    checksum = data.get("receipt_sha256")
    unsigned = {key: value for key, value in data.items() if key != "receipt_sha256"}
    if not isinstance(checksum, str) or checksum != hashlib.sha256(_bytes(unsigned)).hexdigest():
        raise StudyError(f"Invalid checksum for {schema}")


def _validate_lock(
    index: dict[str, Any],
    atlas: dict[str, Any],
    bridge: dict[str, Any],
    lock: dict[str, Any],
) -> None:
    for source, schema in ((index, INDEX_SCHEMA), (atlas, ATLAS_SCHEMA), (bridge, BRIDGE_SCHEMA)):
        try:
            verify_source(source, schema)
        except Exception as error:
            raise StudyError(f"Source integrity error: {error}") from error
    if lock.get("schema_version") != "vgve-source-lock/0.1":
        raise StudyError("Unsupported source lock")
    requirements = [
        (index["source_sha256"], lock["zl3b"]["source_sha256"]),
        (atlas["manifest_sha256"], lock["yale"]["manifest_sha256"]),
        (index["page_count"], lock["zl3b"]["page_section_count"]),
        (index["locus_count"], lock["zl3b"]["locus_record_count"]),
        (atlas["canvas_count"], lock["yale"]["iiif_canvas_count"]),
        (bridge["transliteration_receipt_sha256"], index["receipt_sha256"]),
        (bridge["atlas_receipt_sha256"], atlas["receipt_sha256"]),
        (bridge["manifest_sha256"], atlas["manifest_sha256"]),
        (bridge["transliteration_source_sha256"], index["source_sha256"]),
    ]
    expected_counts = {
        "EXACT_LABEL_MATCH": lock["literal_crosswalk"]["exact_label_matches"],
        "MULTIPLE_EXPLICIT_CANVASES": lock["literal_crosswalk"][
            "multiple_explicit_canvas_matches"
        ],
        "UNMAPPED": lock["literal_crosswalk"]["unmapped_transcription_sections"],
    }
    if bridge["mapping_counts"] != expected_counts or any(a != b for a, b in requirements):
        raise StudyError("Pinned source/bridge data changed: human review required")


def make_plan(
    index: dict[str, Any],
    atlas: dict[str, Any],
    bridge: dict[str, Any],
    lock: dict[str, Any],
    *,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Freeze a deterministic folio cohort, primary endpoint and independent review grid."""
    _validate_lock(index, atlas, bridge, lock)
    if not 12 <= sample_size <= 50 or sample_size % 4:
        raise StudyError("Sample size must be divisible by 4 and between 12 and 50")

    pages = {page["folio_id"]: page for page in index["pages"]}
    canvas_index = {item["canvas_id"]: item for item in atlas["canvases"]}
    eligible = []
    for match in bridge["mappings"]:
        if match["status"] != "EXACT_LABEL_MATCH":
            continue
        key = match["folio_id"]
        if key not in pages or len(match["canvas_ids"]) != 1:
            raise StudyError("Crosswalk metadata inconsistency")
        canvas = canvas_index.get(match["canvas_ids"][0])
        if (
            canvas is None
            or canvas["folio_key"] != key
            or canvas["label_status"] != "unambiguous"
            or canvas["image_url"] != match["image_urls"][0]
        ):
            raise StudyError(f"Crosswalk no longer points to the locked atlas: {key}")
        if canvas["image_url"] is None:
            continue
        count = len(pages[key]["loci"])
        if count < 1 or count != match["locus_count"]:
            raise StudyError(f"Invalid textual locus count for {key}")
        eligible.append((key, count))
    if len(eligible) < sample_size:
        raise StudyError(f"Only {len(eligible)} strictly mapped, image-backed folios eligible")
    ordered = sorted(
        eligible,
        key=lambda item: (
            hashlib.sha256(f"{SEED}:{item[0]}".encode()).hexdigest(),
            item[0],
        ),
    )
    selection = ordered[:sample_size]
    holdout = sample_size // 4
    # The cohort and reserved holdout membership are determined without any visual reviews.
    records = [
        {
            "folio_id": key,
            "text_loci_count": count,
            "partition": "HOLDOUT" if index_in_sample < holdout else "DEVELOPMENT",
        }
        for index_in_sample, (key, count) in enumerate(selection)
    ]
    try:
        protocol = create_protocol(
            atlas, [row["folio_id"] for row in records], rows=2, cols=2
        )
    except ReviewError as error:
        raise StudyError(f"Could not lock review grid: {error}") from error
    plan = {
        "schema_version": PLAN_SCHEMA,
        "study_id": "VGVE-PILOT-001",
        "source_lock_id": lock["schema_version"],
        "source_manifest_sha256": atlas["manifest_sha256"],
        "source_ivtff_sha256": index["source_sha256"],
        "atlas_receipt_sha256": atlas["receipt_sha256"],
        "transcription_receipt_sha256": index["receipt_sha256"],
        "crosswalk_receipt_sha256": bridge["receipt_sha256"],
        "review_protocol_receipt_sha256": protocol["receipt_sha256"],
        "seed": SEED,
        "eligible_folios": len(eligible),
        "sample_size": sample_size,
        "holdout_size": holdout,
        "grid": {"rows": 2, "cols": 2},
        "records": records,
        "hypothesis": (
            "Among prespecified held-out folios, the prevalence of FLOW labels "
            "independently assigned by both reviewers is positively rank-correlated "
            "with IVTFF locus count per folio."
        ),
        "primary_metric": "Spearman rank correlation on HOLDOUT only",
        "predictor": "Total IVTFF loci in a folio section",
        "response": "Fraction of all fixed cells that both reviewers label FLOW",
        "alpha_one_sided": ALPHA,
        "permutations": SHUFFLES,
        "control": "Shuffle response across held-out folios, retaining feature marginals",
        "power_warning": "Small exploratory pilot, underpowered for most realistic effects",
        "exclusion_policy": (
            "No post-hoc exclusions. Incomplete reviews, unavailable folios, and "
            "source mismatches block evaluation rather than silently removing cases."
        ),
        "review_status": "PRE-ANNOTATION: NO EMPIRICAL OUTCOME",
        "claim_boundary": (
            "A positive association, if later observed, would not decipher the "
            "Voynich script or prove a shared ancient metaphysical decoder."
        ),
    }
    return _seal(plan), protocol


def _midranks(values: list[float]) -> list[float]:
    positions = sorted(range(len(values)), key=lambda idx: values[idx])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[positions[end]] == values[positions[start]]:
            end += 1
        rank = ((start + 1) + end) / 2
        for index in positions[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def _spearman(first: list[float], second: list[float]) -> float | None:
    if len(first) != len(second) or len(first) < 3:
        raise StudyError("Need three or more paired held-out observations")
    x, y = _midranks(first), _midranks(second)
    x_mean, y_mean = sum(x) / len(x), sum(y) / len(y)
    covariance = sum((a - x_mean) * (b - y_mean) for a, b in zip(x, y, strict=True))
    xx = sum((a - x_mean) ** 2 for a in x)
    yy = sum((b - y_mean) ** 2 for b in y)
    if xx == 0 or yy == 0:
        return None
    return covariance / math.sqrt(xx * yy)


def evaluate(
    plan: dict[str, Any],
    protocol: dict[str, Any],
    first: dict[str, Any],
    second: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate a frozen held-out hypothesis only after two complete independent reviews."""
    _verify(plan, PLAN_SCHEMA)
    try:
        verify_review(protocol, PROTOCOL_SCHEMA)
    except ReviewError as error:
        raise StudyError(f"Invalid review protocol: {error}") from error
    if plan["review_protocol_receipt_sha256"] != protocol["receipt_sha256"]:
        raise StudyError("Review protocol differs from preregistered plan")
    if plan["atlas_receipt_sha256"] != protocol["atlas_receipt_sha256"]:
        raise StudyError("Source atlas differs from preregistered plan")
    if (
        plan["seed"] != SEED
        or plan["permutations"] != SHUFFLES
        or plan["alpha_one_sided"] != ALPHA
        or plan["grid"] != {"rows": 2, "cols": 2}
        or plan["primary_metric"] != "Spearman rank correlation on HOLDOUT only"
    ):
        raise StudyError("Frozen statistical protocol differs from implemented method")
    try:
        agreement = compare_reviews(protocol, first, second)
        a = _checked_annotations(protocol, first)
        b = _checked_annotations(protocol, second)
    except ReviewError as error:
        raise StudyError(f"Invalid independent review: {error}") from error

    expected = {row["folio_id"] for row in plan["records"]}
    grouped: dict[str, list[str]] = {}
    for region in protocol["regions"]:
        key = region["folio"]
        if key not in expected:
            raise StudyError("Unexpected folio in independent review protocol")
        grouped.setdefault(key, []).append(region["region_id"])
    if set(grouped) != expected or any(len(ids) != 4 for ids in grouped.values()):
        raise StudyError("Review protocol does not cover every preregistered 2x2 grid")

    measures = []
    for row in plan["records"]:
        ids = grouped[row["folio_id"]]
        numerator = sum(
            a[region_id]["operator"] == "FLOW" and b[region_id]["operator"] == "FLOW"
            for region_id in ids
        )
        measures.append(
            {
                "folio_id": row["folio_id"],
                "partition": row["partition"],
                "loci_count": row["text_loci_count"],
                "consensus_flow_fraction": numerator / len(ids),
            }
        )
    held_out = [row for row in measures if row["partition"] == "HOLDOUT"]
    if len(held_out) != plan["holdout_size"] or len(held_out) < 3:
        raise StudyError("Holdout partition is invalid")

    x = [float(row["loci_count"]) for row in held_out]
    y = [row["consensus_flow_fraction"] for row in held_out]
    observed = _spearman(x, y)
    p_value = None
    if observed is not None:
        rng = random.Random(SEED + ":permutation")
        hit_count = 0
        for _ in range(SHUFFLES):
            shuffled = y.copy()
            rng.shuffle(shuffled)
            result = _spearman(x, shuffled)
            if result is not None and result >= observed - 1e-12:
                hit_count += 1
        p_value = (1 + hit_count) / (1 + SHUFFLES)

    status = (
        "INDETERMINATE"
        if observed is None
        else "PILOT_POSITIVE_ASSOCIATION"
        if observed > 0 and p_value is not None and p_value <= ALPHA
        else "NO_PREREGISTERED_POSITIVE_SIGNAL"
    )
    return _seal(
        {
            "schema_version": RESULT_SCHEMA,
            "study_id": plan["study_id"],
            "plan_receipt_sha256": plan["receipt_sha256"],
            "review_agreement_receipt_sha256": agreement["receipt_sha256"],
            "holdout_n": len(held_out),
            "heldout_observations": held_out,
            "spearman_rho": None if observed is None else round(observed, 6),
            "permutation_p_one_sided": None if p_value is None else round(p_value, 6),
            "permutations": SHUFFLES,
            "alpha": ALPHA,
            "verdict": status,
            "agreement_cohen_kappa": agreement["cohen_kappa"],
            "limitations": [
                "Statistical association does not imply glyph semantics or decipherment.",
                "The primary test has low power and is not an ancient-text comparison.",
                "Grid annotations remain vulnerable to human priming and shared assumptions.",
                "Folios may differ in layout, scan conditions, and text visibility.",
                "Source mapping is based on literal metadata labels, not full manual alignment.",
            ],
        }
    )


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, obj: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """Offline CLI: prepare preregistration, or score sealed independent reviews."""
    parser = argparse.ArgumentParser(description="VGVE preregistered pilot")
    actions = parser.add_subparsers(dest="action", required=True)
    prepare = actions.add_parser("prepare")
    for name in ("index", "atlas", "bridge", "lock"):
        prepare.add_argument(name, type=Path)
    prepare.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE)
    prepare.add_argument("--out-plan", type=Path, required=True)
    prepare.add_argument("--out-protocol", type=Path, required=True)
    score = actions.add_parser("score")
    for name in ("plan", "protocol", "first", "second"):
        score.add_argument(name, type=Path)
    score.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == "prepare":
            plan, protocol = make_plan(
                _load(args.index),
                _load(args.atlas),
                _load(args.bridge),
                _load(args.lock),
                sample_size=args.sample_size,
            )
            _write(args.out_plan, plan)
            _write(args.out_protocol, protocol)
            print(f"Prepared {len(plan['records'])} folios, holdout={plan['holdout_size']}")
            print(f"PLAN SHA256: {plan['receipt_sha256']}")
        else:
            report = evaluate(
                _load(args.plan),
                _load(args.protocol),
                _load(args.first),
                _load(args.second),
            )
            _write(args.out, report)
            print(f"Primary verdict: {report['verdict']} (no decipherment claims)")
    except (StudyError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
