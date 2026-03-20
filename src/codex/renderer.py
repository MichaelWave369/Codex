"""Render decode results as Markdown and JSON strings."""

from __future__ import annotations

import json

from codex.models import DecodeResult


def to_json(result: DecodeResult) -> str:
    """Render decode result as pretty JSON."""
    return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)


def to_markdown(result: DecodeResult) -> str:
    """Render decode result as human-readable markdown report."""
    lines = [
        "# CODEX Decode Summary",
        "",
        f"- **Source**: `{result.source}`",
        f"- **Tradition**: `{result.tradition_name}` (`{result.tradition_key}`)",
        f"- **Matched pattern groups**: {len(result.matches)}",
        "",
        "## Matched Patterns",
    ]

    if not result.matches:
        lines.extend(["", "No deterministic lexical matches found."])
    else:
        for match in result.matches:
            lines.extend(
                [
                    "",
                    f"### `{match.tag}`",
                    f"- Matched terms: {', '.join(match.matched_terms)}",
                    f"- Interpretive note: {match.interpretive_note}",
                    f"- Confidence: **{match.confidence.level}** ({match.confidence.rationale})",
                    "- Evidence spans:",
                ]
            )
            for span in match.evidence:
                clean_context = span.context.replace("\n", " ")
                lines.append(
                    f"  - `{span.phrase}` at [{span.start}, {span.end}] → “{clean_context}”"
                )

    lines.extend(["", "## Cautionary Note", "", result.cautionary_note])
    return "\n".join(lines)
