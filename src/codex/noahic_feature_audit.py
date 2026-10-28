"""NOAHIC-02 passage-level feature audit with negative-evidence safeguards.

This tool compares *editorial annotations*, not manuscript transcriptions.
Neither shared features nor the 'candidate_distinctive' flag imply textual
dependence, numerical rarity, provenance, or an independently decoded text.
"""

from __future__ import annotations

import argparse
import json
from importlib import resources
from typing import Any

from codex.noahic import load_corpus

SCHEMA = "noahic-02/feature-audit-v0.2"
STATUSES = {"attested", "not_attested_in_locus", "unreviewed"}
CAUTION = (
    "Features reflect curated English-language readings. "
    "'Not attested in locus' is not absence from an entire work. "
    "Unreviewed controls must not be counted as negative instances. "
    "This analysis cannot prove rarity, literary descent, or authenticity."
)


def load_audit() -> dict[str, Any]:
    """Load the versioned passage-level audit and validate its constraints."""
    path = resources.files("codex.data").joinpath("noahic_feature_audit_v0_2.json")
    audit = json.loads(path.read_text(encoding="utf-8"))
    validate_audit(audit)
    return audit


def validate_audit(audit: dict[str, Any]) -> None:
    """Require locators for positive and explicitly scoped negative claims."""
    if audit.get("schema") != SCHEMA:
        raise ValueError("Unknown feature audit schema")
    corpus = load_corpus()
    corpus_ids = {entry["id"] for entry in corpus["items"]}
    pair = audit.get("pair")
    if not isinstance(pair, list) or len(pair) != 2 or len(set(pair)) != 2:
        raise ValueError("Expected exactly two distinct target passage IDs")
    if not set(pair).issubset(corpus_ids):
        raise ValueError("Unknown target passage ID")
    sources = audit.get("sources")
    if not isinstance(sources, dict) or set(sources) != set(pair):
        raise ValueError("Pair must have two provenance records")
    for item in sources.values():
        if not isinstance(item, dict) or not item.get("url", "").startswith("https://"):
            raise ValueError("Missing source URL")
        if not isinstance(item.get("edition"), str) or not item["edition"]:
            raise ValueError("Missing witness or edition label")

    controls = audit.get("controls")
    if not isinstance(controls, list) or {item.get("id") for item in controls} != (
        corpus_ids - set(pair)
    ):
        raise ValueError("Controls must cover every other corpus item")
    if any(item.get("status") != "unreviewed" or not item.get("note") for item in controls):
        raise ValueError("Unassessed control must remain explicitly unreviewed")
    features = audit.get("features")
    if not isinstance(features, list) or not features:
        raise ValueError("Audit must contain reviewed features")
    ids: set[str] = set()
    for feature in features:
        feature_id = feature.get("id")
        if not isinstance(feature_id, str) or not feature_id or feature_id in ids:
            raise ValueError("Missing or duplicate feature ID")
        ids.add(feature_id)
        if not isinstance(feature.get("label"), str) or not feature["label"]:
            raise ValueError("Feature label missing")
        if not isinstance(feature.get("candidate_distinctive"), bool):
            raise ValueError("Distinctiveness annotation must be boolean")
        attestations = feature.get("attestations")
        if not isinstance(attestations, dict) or set(attestations) != set(pair):
            raise ValueError("Each feature must have two scoped annotations")
        for entry in attestations.values():
            if not isinstance(entry, dict) or entry.get("status") not in STATUSES:
                raise ValueError("Unknown attestation status")
            if (
                not isinstance(entry.get("locus"), str)
                or not entry["locus"].strip()
                or not isinstance(entry.get("note"), str)
                or not entry["note"].strip()
            ):
                raise ValueError("Feature requires a precise locus and audit note")
            if entry["status"] == "attested":
                if not isinstance(entry.get("role"), str) or not entry["role"]:
                    raise ValueError("Positive attestation requires contextual role")
            elif entry.get("role") is not None:
                raise ValueError("Unattested or unreviewed entry cannot invent a role")


def comparison(audit: dict[str, Any]) -> dict[str, Any]:
    """Classify pair features while avoiding manufactured probabilities."""
    validate_audit(audit)
    left, right = audit["pair"]
    same_context: list[dict[str, Any]] = []
    context_shift: list[dict[str, Any]] = []
    asymmetry: list[dict[str, Any]] = []
    unresolved: list[str] = []
    for feature in audit["features"]:
        lhs, rhs = feature["attestations"][left], feature["attestations"][right]
        record = {
            "feature_id": feature["id"],
            "label": feature["label"],
            "candidate_distinctive": feature["candidate_distinctive"],
            "left": lhs,
            "right": rhs,
        }
        statuses = {lhs["status"], rhs["status"]}
        if "unreviewed" in statuses:
            unresolved.append(feature["id"])
        elif statuses == {"attested"}:
            if lhs["role"] == rhs["role"]:
                same_context.append(record)
            else:
                context_shift.append(record)
        else:
            asymmetry.append(record)

    return {
        "schema": SCHEMA,
        "pair": audit["pair"],
        "source_witnesses": audit["sources"],
        "shared_same_role": same_context,
        "shared_different_role": context_shift,
        "asymmetric_attestations": asymmetry,
        "unresolved_features": unresolved,
        "control_count": len(audit["controls"]),
        "control_reviews_completed": 0,
        "controls": audit["controls"],
        "rarity_evaluable": False,
        "historical_dependence_established": False,
        "warning": CAUTION,
    }


def render_markdown(result: dict[str, Any]) -> str:
    """Readable summary with witness locators and missing controls exposed."""
    lines = [
        "# NOAHIC-02: Feature audit",
        "",
        f"Pair: {result['pair'][0]} vs {result['pair'][1]}",
        "",
    ]
    sections = (
        ("Same-role overlap", "shared_same_role"),
        ("Same name but changed role", "shared_different_role"),
        ("Passage-level asymmetries", "asymmetric_attestations"),
    )
    for title, key in sections:
        lines.extend((f"## {title}", ""))
        if not result[key]:
            lines.append("- None in this curated audit")
        for feature in result[key]:
            left, right = result["pair"]
            lref, rref = feature["left"]["locus"], feature["right"]["locus"]
            lines.append(f"- **{feature['label']}** | {left}: {lref} | {right}: {rref}")
        lines.append("")
    lines.extend(
        (
            "## Baseline limitations",
            "",
            f"- Unreviewed controls: {result['control_count']}",
            "- Rarity inference: **not evaluable**",
            "- Historical dependence: **not established**",
            "",
            "## Sources",
        )
    )
    for source_id, item in result["source_witnesses"].items():
        lines.append(f"- {source_id}: {item['url']} ({item['edition']})")
    lines.extend(("", "## Method caution", CAUTION, ""))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Command line: python -m codex.noahic_feature_audit [validate|compare|controls]."""
    parser = argparse.ArgumentParser(description="NOAHIC-02 feature audit")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    compare_command = commands.add_parser("compare")
    compare_command.add_argument("--json", action="store_true")
    commands.add_parser("controls")
    args = parser.parse_args(argv)
    audit = load_audit()
    if args.command == "validate":
        print(f"VALID: {SCHEMA}; {len(audit['features'])} features")
    elif args.command == "controls":
        print(json.dumps(audit["controls"], indent=2))
    else:
        report = comparison(audit)
        print(json.dumps(report, indent=2) if args.json else render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
