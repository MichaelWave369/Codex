"""Theme helpers for CODEX Operator Studio."""

from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """Apply a compact dark operator-style theme."""
    st.markdown(
        """
        <style>
        :root {
            --bg: #07090f;
            --panel: #101626;
            --ink: #e9edf7;
            --muted: #9aa3b8;
            --gold: #c8a97e;
            --teal: #55d4cf;
            --danger: #e06c75;
            --ok: #8fce84;
            --border: #1f2a44;
        }
        .stApp {
            background: radial-gradient(circle at top, #10182c 0%, var(--bg) 55%);
            color: var(--ink);
        }
        .codex-title {
            font-size: 1.6rem;
            font-weight: 700;
            letter-spacing: .04em;
            color: var(--gold);
            margin-bottom: .2rem;
        }
        .codex-subtitle {
            color: var(--muted);
            margin-bottom: 1rem;
        }
        .codex-card {
            border: 1px solid var(--border);
            background: linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,.01));
            border-radius: .6rem;
            padding: .7rem .8rem;
            margin-bottom: .6rem;
        }
        .codex-label {
            color: var(--muted);
            font-size: .78rem;
            text-transform: uppercase;
            letter-spacing: .05em;
        }
        .codex-value {
            color: var(--ink);
            font-size: 1.15rem;
            font-weight: 600;
        }
        .evidence {
            border-left: 3px solid var(--gold);
            background: rgba(200,169,126,.08);
            padding: .45rem .65rem;
            border-radius: .2rem;
            margin-bottom: .35rem;
            color: var(--ink);
        }
        .empty {
            color: var(--muted);
            border: 1px dashed var(--border);
            border-radius: .5rem;
            padding: .8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
