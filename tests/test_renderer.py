import json

from codex.decoder import decode_text
from codex.renderer import to_json, to_markdown


def test_json_output_shape() -> None:
    result = decode_text("inner light", tradition_key="thomas", source="unit")
    payload = json.loads(to_json(result))
    assert payload["tradition_key"] == "thomas"
    assert "matches" in payload


def test_markdown_renderer_contains_sections() -> None:
    result = decode_text("inner light and breath", tradition_key="thomas", source="unit")
    md = to_markdown(result)
    assert "# CODEX Decode Summary" in md
    assert "## Matched Patterns" in md
    assert "## Cautionary Note" in md
