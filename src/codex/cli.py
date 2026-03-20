"""Typer CLI entrypoint for CODEX MVP."""

from __future__ import annotations

from pathlib import Path

import typer
from codex.decoder import decode_text
from codex.lexicon import load_base_patterns
from codex.renderer import to_json, to_markdown
from codex.traditions import get_tradition, list_traditions, load_sample_text

app = typer.Typer(help="Deterministic symbolic decoder for ancient wisdom tradition excerpts.")


@app.command("list-traditions")
def list_traditions_cmd() -> None:
    """List all registered tradition adapters."""
    for tradition in list_traditions():
        typer.echo(f"{tradition.key}: {tradition.display_name}")
        typer.echo(f"  {tradition.description}")


@app.command("sample")
def sample_cmd(tradition: str = typer.Option(..., "--tradition", "-t")) -> None:
    """Print bundled sample text for a tradition."""
    selected = get_tradition(tradition)
    typer.echo(load_sample_text(selected))


@app.command("decode")
def decode_cmd(
    tradition: str = typer.Option(..., "--tradition", "-t"),
    input_path: Path = typer.Option(..., "--input", "-i", exists=True, readable=True),
    json_out: bool = typer.Option(False, "--json", help="Print JSON only."),
    markdown_out: bool = typer.Option(False, "--markdown", help="Print markdown only."),
) -> None:
    """Decode an input text file and emit markdown and JSON outputs."""
    text = input_path.read_text(encoding="utf-8")
    result = decode_text(text=text, tradition_key=tradition, source=str(input_path))

    if json_out and not markdown_out:
        typer.echo(to_json(result))
        return
    if markdown_out and not json_out:
        typer.echo(to_markdown(result))
        return

    typer.echo(to_markdown(result))
    typer.echo("\n---\n")
    typer.echo(to_json(result))


@app.command("explain-patterns")
def explain_patterns_cmd() -> None:
    """List base pattern groups and their starter terms."""
    patterns = load_base_patterns()
    for tag, terms in patterns.items():
        typer.echo(f"{tag}:")
        typer.echo(f"  {', '.join(terms)}")


if __name__ == "__main__":
    app()
