"""Session-state utilities for CODEX Operator Studio."""

from __future__ import annotations

import streamlit as st

DEFAULT_SAMPLE_A = (
    "Jesus said: The kingdom of God is within you and all around you. "
    "If you bring forth what is within you what you bring forth will save you."
)
DEFAULT_SAMPLE_B = (
    "The All is Mind. As above so below. Know thyself and thou shalt know the universe. "
    "Freedom is the birthright of every soul."
)


def init_state() -> None:
    """Initialize all expected session keys."""
    defaults = {
        "mode": "Analyze",
        "analyze_text": "",
        "analyze_tradition": "generic",
        "analyze_source": "Operator Input",
        "compare_text_a": "",
        "compare_text_b": "",
        "compare_tradition_a": "generic",
        "compare_tradition_b": "generic",
        "compare_source_a": "Text A",
        "compare_source_b": "Text B",
        "analyze_result": None,
        "compare_result": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def load_sample(mode: str) -> None:
    """Load sample content into current mode text fields."""
    if mode == "Analyze":
        st.session_state["analyze_text"] = DEFAULT_SAMPLE_A
        st.session_state["analyze_source"] = "Sample: Thomas-style"
    else:
        st.session_state["compare_text_a"] = DEFAULT_SAMPLE_A
        st.session_state["compare_text_b"] = DEFAULT_SAMPLE_B
        st.session_state["compare_source_a"] = "Sample A"
        st.session_state["compare_source_b"] = "Sample B"


def clear_mode(mode: str) -> None:
    """Clear text + results for the selected mode."""
    if mode == "Analyze":
        st.session_state["analyze_text"] = ""
        st.session_state["analyze_result"] = None
    else:
        st.session_state["compare_text_a"] = ""
        st.session_state["compare_text_b"] = ""
        st.session_state["compare_result"] = None
