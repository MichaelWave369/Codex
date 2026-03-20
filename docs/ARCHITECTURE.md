# CODEX Architecture (MVP)

## Why deterministic first
The first release uses deterministic lexicon matching to provide:
- transparent behavior,
- reproducible outputs,
- inspectable evidence spans,
- low operational complexity.

This foundation helps contributors validate assumptions before introducing probabilistic methods.

## Current flow
1. Select tradition adapter (metadata, normalization rules, lexicon extensions).
2. Normalize text with simple substitution rules.
3. Load shared pattern lexicon from JSON.
4. Merge tradition-specific terms into shared tags.
5. Match terms directly in normalized text.
6. Emit structured `DecodeResult` with conservative confidence and cautionary notes.

## Why this is extensible
- Pattern files are editable JSON resources.
- Tradition adapters are isolated modules with small, explicit contracts.
- Rendering is separated from decoding (Markdown and JSON outputs).
- Tests assert behavior at lexicon, registry, decoder, and renderer levels.

## Phase 2 options
- Broaden multilingual lexicons with editorial review workflows.
- Add corpus packaging and citation-aware evidence indexing.
- Implement cross-tradition comparative reports with explicit uncertainty controls.
- Add optional ML-assisted ranking as a secondary layer, never replacing deterministic evidence.
