"""NOAHIC-01: provenance-first comparison of curated manuscript descriptions.

A deterministic motif index, not a decipherer or historical stemma.
"""

from __future__ import annotations

import argparse
import json
from importlib import resources
from typing import Any

_SCHEMA = "noahic-01/seed-v0.1"
_ROLES = {"noah_medicine", "direct_noah_book", "control"}
_WARNING = (
    "Motifs are curator-assigned descriptions, not measured original-language "
    "textual similarity. Shared motifs do not establish manuscript descent, "
    "common authorship, medical efficacy, or recovery of a lost Book of Noah."
)


def load_corpus() -> dict[str, Any]:
    """Load the source-linked pilot corpus, failing on broken provenance."""
    path = resources.files("codex.data").joinpath("noahic_seed_v0_1.json")
    corpus = json.loads(path.read_text(encoding="utf-8"))
    validate_corpus(corpus)
    return corpus


def validate_corpus(corpus: dict[str, Any]) -> None:
    """Validate schema, source links, classification, and motif sequences."""
    if corpus.get("schema") != _SCHEMA:
        raise ValueError("Unrecognized Noahic corpus schema")
    items = corpus.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("Corpus requires a nonempty items list")
    ids: set[str] = set()
    for item in items:
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            raise ValueError("Missing or duplicate item ID")
        ids.add(identifier)
        if item.get("role") not in _ROLES:
            raise ValueError(f"Unsupported role for {identifier}")
        for field in ("work", "locus", "period", "tradition", "witness", "claim", "caution"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"Missing {field} for {identifier}")
        for field in ("agents", "motifs", "sequence"):
            values = item.get(field)
            if not isinstance(values, list) or not all(
                isinstance(value, str) and value for value in values
            ):
                raise ValueError(f"Invalid {field} for {identifier}")
        if not set(item["sequence"]).issubset(item["motifs"]):
            raise ValueError(f"Unindexed sequence motif for {identifier}")
        sources = item.get("sources")
        if not isinstance(sources, list) or not sources or not all(
            isinstance(source, dict)
            and isinstance(source.get("type"), str)
            and source.get("url", "").startswith("https://")
            for source in sources
        ):
            raise ValueError(f"At least one https source required for {identifier}")


def _ordered_shared(left: list[str], right: list[str]) -> list[str]:
    """Find one deterministic longest common subsequence of editorial motifs."""
    table = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for i, a in enumerate(left, 1):
        for j, b in enumerate(right, 1):
            table[i][j] = (
                table[i - 1][j - 1] + 1
                if a == b
                else max(table[i - 1][j], table[i][j - 1])
            )
    result: list[str] = []
    i, j = len(left), len(right)
    while i and j:
        if left[i - 1] == right[j - 1]:
            result.append(left[i - 1])
            i -= 1
            j -= 1
        elif table[i - 1][j] >= table[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return result[::-1]


def compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Compare metadata only; never infer common ancestry from motif overlap."""
    shared_motifs = sorted(set(left["motifs"]) & set(right["motifs"]))
    shared_agents = sorted(set(left["agents"]) & set(right["agents"]))
    if left["role"] == "noah_medicine" and right["role"] == "noah_medicine":
        category = "noahic_medicine_parallel"
    elif left["role"] != "control" and right["role"] != "control":
        category = "distinct_noah_book_traditions"
    elif shared_motifs or shared_agents:
        category = "contextual_parallel_with_control"
    else:
        category = "no_indexed_parallel"
    return {
        "left": left["id"],
        "right": right["id"],
        "category": category,
        "shared_motifs": shared_motifs,
        "shared_agents": shared_agents,
        "ordered_shared_motifs": _ordered_shared(left["sequence"], right["sequence"]),
        "left_sources": left["sources"],
        "right_sources": right["sources"],
        "left_caution": left["caution"],
        "right_caution": right["caution"],
        "establishes_common_source": False,
        "method_warning": _WARNING,
    }


def matrix(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return all pairwise comparisons, including the negative controls."""
    return [
        compare(left, right)
        for index, left in enumerate(items)
        for right in items[index + 1 :]
    ]


def render_comparison(report: dict[str, Any]) -> str:
    """Provide a citation-bearing Markdown report without inflated confidence."""
    def show(values: list[str]) -> str:
        return ", ".join(values) if values else "none"

    source_lines = [
        *[f"- {report['left']}: {entry['url']}" for entry in report["left_sources"]],
        *[f"- {report['right']}: {entry['url']}" for entry in report["right_sources"]],
    ]
    return "\n".join(
        [
            f"# NOAHIC-01: {report['left']} vs {report['right']}",
            "",
            f"**Category:** {report['category']}",
            f"**Shared editorial motifs:** {show(report['shared_motifs'])}",
            f"**Shared agents:** {show(report['shared_agents'])}",
            f"**Ordered motif subsequence:** {show(report['ordered_shared_motifs'])}",
            "**Proves a common lost source?** No.",
            "",
            "## Cautions",
            f"- {report['left_caution']}",
            f"- {report['right_caution']}",
            "",
            "## Provenance",
            *source_lines,
            "",
            "## Method boundary",
            _WARNING,
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    """Command-line research tool: python -m codex.noahic."""
    parser = argparse.ArgumentParser(description="NOAHIC-01 evidence index")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("validate")
    pair = sub.add_parser("compare")
    pair.add_argument("left")
    pair.add_argument("right")
    pair.add_argument("--json", action="store_true")
    sub.add_parser("matrix")
    args = parser.parse_args(argv)
    items = load_corpus()["items"]
    index = {item["id"]: item for item in items}
    if args.command == "list":
        for item in items:
            print(f"{item['id']:24} [{item['role']}] {item['work']} / {item['locus']}")
    elif args.command == "validate":
        print(f"VALID: {_SCHEMA}; {len(items)} passages")
    elif args.command == "matrix":
        print(json.dumps({"warning": _WARNING, "pairs": matrix(items)}, indent=2))
    elif args.command == "compare":
        for key in (args.left, args.right):
            if key not in index:
                parser.error(f"Unknown passage: {key}")
        if args.left == args.right:
            parser.error("Choose two different passages")
        result = compare(index[args.left], index[args.right])
        print(json.dumps(result, indent=2) if args.json else render_comparison(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
