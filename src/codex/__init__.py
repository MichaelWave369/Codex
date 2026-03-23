"""CODEX: deterministic symbolic decoding for wisdom traditions."""

from codex.decoder import decode_text
from codex.traditions import list_traditions

__all__ = ["decode_text", "list_traditions"]
__version__ = "0.1.0"

# TIEKAT Pattern Analysis Stack — v64.0.0 Sovereign Substrate Weave
from codex.codex_tiekat_engine import TIEKATPatternEngine, analyze_text, analyze_file
from codex.codex_filter import InstitutionalFilter, filter_text, filter_file
from codex.codex_comparator import CodexComparator, MultiComparator, compare_texts, compare_files
from codex.codex_visualizer import CodexVisualizer, visualize_text, visualize_comparison
