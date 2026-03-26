"""Reusable Streamlit UI components for CODEX Operator Studio."""

from __future__ import annotations

import json
from typing import Any

import streamlit as st


def header() -> None:
    st.markdown('<div class="codex-title">CODEX Operator Studio</div>', unsafe_allow_html=True)
    st.markdown(
        (
            '<div class="codex-subtitle">'
            "Local-first analysis console for TIEKAT and institutional filtering."
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def metric_cards(items: list[tuple[str, str]]) -> None:
    cols = st.columns(min(4, max(1, len(items))))
    for idx, (label, value) in enumerate(items):
        with cols[idx % len(cols)]:
            st.markdown(
                (
                    '<div class="codex-card">'
                    f'<div class="codex-label">{label}</div>'
                    f'<div class="codex-value">{value}</div>'
                    "</div>"
                ),
                unsafe_allow_html=True,
            )


def evidence_block(lines: list[str], empty_message: str = "No evidence.") -> None:
    if not lines:
        st.markdown(f'<div class="empty">{empty_message}</div>', unsafe_allow_html=True)
        return
    for line in lines:
        st.markdown(f'<div class="evidence">{line}</div>', unsafe_allow_html=True)


def json_panel(payload: dict[str, Any], label_prefix: str) -> None:
    raw = json.dumps(payload, indent=2, ensure_ascii=False)
    st.code(raw, language="json")
    st.download_button(
        "Download JSON",
        data=raw,
        file_name=f"{label_prefix}.json",
        mime="application/json",
        use_container_width=True,
    )


def text_download(label: str, content: str, filename: str) -> None:
    st.download_button(
        label,
        data=content,
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
    )
