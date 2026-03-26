"""CODEX: deterministic symbolic decoding for wisdom traditions."""

from .codex_comparator import CodexComparator, MultiComparator, compare_files, compare_texts
from .codex_filter import InstitutionalFilter, filter_file, filter_text
from .codex_tiekat_engine import TIEKATPatternEngine, analyze_file, analyze_text
from .codex_visualizer import CodexVisualizer, visualize_comparison, visualize_text
from .decoder import decode_text
from .traditions import list_traditions

__all__ = [
    "CodexComparator",
    "CodexVisualizer",
    "InstitutionalFilter",
    "MultiComparator",
    "TIEKATPatternEngine",
    "__version__",
    "analyze_file",
    "analyze_text",
    "compare_files",
    "compare_texts",
    "decode_text",
    "filter_file",
    "filter_text",
    "list_traditions",
    "visualize_comparison",
    "visualize_text",
]
__version__ = "0.1.0"
