"""Streamlit front-end for CODEX Operator Studio Interface v1."""

from __future__ import annotations

from typing import Any

import streamlit as st

from codex.codex_comparator import CodexComparator
from codex.codex_filter import InstitutionalFilter
from codex.codex_tiekat_engine import Confidence, TIEKATPatternEngine
from codex.codex_visualizer import CodexVisualizer
from codex_operator.components import (
    evidence_block,
    header,
    json_panel,
    metric_cards,
    text_download,
)
from codex_operator.state import clear_mode, init_state, load_sample
from codex_operator.theme import apply_theme

st.set_page_config(page_title="CODEX Operator Studio", page_icon="🜂", layout="wide")
apply_theme()
init_state()
header()

KNOWN_TRADITIONS = TIEKATPatternEngine.KNOWN_TRADITIONS


def _read_upload(upload: Any) -> str:
    if upload is None:
        return ""
    return upload.getvalue().decode("utf-8", errors="replace")


def run_analyze(text: str, tradition: str, source: str) -> dict[str, Any]:
    filter_engine = InstitutionalFilter(tradition=tradition)
    pattern_engine = TIEKATPatternEngine(tradition=tradition)
    visualizer = CodexVisualizer()

    filter_report = filter_engine.analyze(text, source=source)
    pattern_report = pattern_engine.analyze(text, source=source)

    return {
        "filter_report": filter_report,
        "pattern_report": pattern_report,
        "filter_dict": filter_report.to_dict(),
        "pattern_dict": pattern_report.to_dict(),
        "filter_text": filter_engine.render_dashboard(filter_report),
        "filter_markdown": filter_engine.render_markdown(filter_report),
        "pattern_text": pattern_engine.render_dashboard(pattern_report),
        "pattern_markdown": pattern_engine.render_markdown(pattern_report),
        "html": visualizer.full_dashboard(
            filter_report=filter_report,
            tiekat_report=pattern_report,
            title=f"CODEX Operator Studio — {source}",
            source_label=source,
        ),
    }


def run_compare(
    text_a: str,
    text_b: str,
    tradition_a: str,
    tradition_b: str,
    source_a: str,
    source_b: str,
) -> dict[str, Any]:
    ta = TIEKATPatternEngine(tradition=tradition_a)
    tb = TIEKATPatternEngine(tradition=tradition_b)
    comparator = CodexComparator()
    visualizer = CodexVisualizer()

    report_a = ta.analyze(text_a, source=source_a)
    report_b = tb.analyze(text_b, source=source_b)
    comp = comparator.compare(report_a, report_b)

    return {
        "report_a": report_a,
        "report_b": report_b,
        "comparison": comp,
        "comparison_dict": comp.to_dict(),
        "dashboard_text": comparator.render_dashboard(comp),
        "markdown": comparator.render_markdown(comp),
        "html": visualizer.full_dashboard(
            tiekat_report=report_a,
            comparison_report=comp,
            title=f"CODEX Operator Studio — {source_a} vs {source_b}",
            source_label=f"{source_a} vs {source_b}",
        ),
    }


def render_analyze() -> None:
    st.subheader("Analyze")
    ctl1, ctl2, ctl3 = st.columns([1, 1, 2])
    with ctl1:
        if st.button("Load sample", use_container_width=True):
            load_sample("Analyze")
    with ctl2:
        if st.button("Clear", use_container_width=True):
            clear_mode("Analyze")
    with ctl3:
        upload = st.file_uploader("Upload .txt/.md", type=["txt", "md"], key="an_upload")

    if upload is not None:
        st.session_state["analyze_text"] = _read_upload(upload)

    st.session_state["analyze_source"] = st.text_input(
        "Source label", st.session_state["analyze_source"]
    )
    st.session_state["analyze_tradition"] = st.selectbox(
        "Tradition",
        options=list(KNOWN_TRADITIONS.keys()),
        index=list(KNOWN_TRADITIONS.keys()).index(st.session_state["analyze_tradition"]),
    )
    st.session_state["analyze_text"] = st.text_area(
        "Source text",
        value=st.session_state["analyze_text"],
        height=220,
        placeholder="Paste or type source text…",
    )

    if st.button("Run single-text analysis", type="primary", use_container_width=True):
        text = st.session_state["analyze_text"].strip()
        if not text:
            st.warning("Please provide source text first.")
        else:
            with st.spinner("Running filter + TIEKAT analysis…"):
                st.session_state["analyze_result"] = run_analyze(
                    text=text,
                    tradition=st.session_state["analyze_tradition"],
                    source=st.session_state["analyze_source"],
                )

    result = st.session_state.get("analyze_result")
    if not result:
        return

    pattern_report = result["pattern_report"]
    filter_report = result["filter_report"]

    tab_overview, tab_patterns, tab_filter, tab_seams, tab_raw = st.tabs(
        ["Overview", "Patterns", "Filter Map", "Seams", "Raw JSON"]
    )

    with tab_overview:
        metric_cards(
            [
                ("Word Count", str(pattern_report.word_count)),
                ("Sentence Count", str(pattern_report.sentence_count)),
                ("Verse Count", str(pattern_report.verse_count)),
                ("Match Count", str(pattern_report.match_count)),
                ("High Confidence", str(len(pattern_report.high_confidence_matches))),
                ("Epsilon Density", f"{pattern_report.epsilon_density:.4f}"),
                ("Omega Density", f"{pattern_report.omega_density:.4f}"),
                ("C* Density", f"{pattern_report.c_star_density:.4f}"),
            ]
        )
        st.markdown("#### Exports")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            json_panel(
                {
                    "pattern_report": result["pattern_dict"],
                    "filter_report": result["filter_dict"],
                },
                "codex_analyze",
            )
        with col2:
            text_download("Download Markdown", result["pattern_markdown"], "codex_patterns.md")
            text_download("Download Filter Markdown", result["filter_markdown"], "codex_filter.md")
        with col3:
            text_download("Download Dashboard Text", result["pattern_text"], "codex_patterns.txt")
            text_download("Download Filter Text", result["filter_text"], "codex_filter.txt")
        with col4:
            st.download_button(
                "Download HTML",
                data=result["html"],
                file_name="codex_analyze.html",
                mime="text/html",
                use_container_width=True,
            )

    with tab_patterns:
        matches = pattern_report.matches
        pattern_options = ["ALL"] + sorted({m.pattern_type.value for m in matches})
        confidence_options = ["ALL"] + sorted({m.confidence.value for m in matches})

        f1, f2, f3 = st.columns(3)
        with f1:
            selected_pattern = st.selectbox("Pattern type", pattern_options)
        with f2:
            selected_conf = st.selectbox("Confidence", confidence_options)
        with f3:
            high_only = st.checkbox("High/Structural only", value=False)

        for match in matches:
            if selected_pattern != "ALL" and match.pattern_type.value != selected_pattern:
                continue
            if selected_conf != "ALL" and match.confidence.value != selected_conf:
                continue
            if high_only and match.confidence not in (Confidence.HIGH, Confidence.STRUCTURAL):
                continue

            with st.container(border=True):
                st.markdown(f"**{match.pattern_type.value}** · `{match.confidence.value}`")
                st.caption(match.tiekat_principle)
                st.write(match.description)
                if match.structural_value is not None:
                    st.write(f"Structural value: `{match.structural_value}`")
                evidence_block([e.excerpt for e in match.evidence], "No excerpts for this match.")

    with tab_filter:
        for passage in filter_report.passages:
            with st.container(border=True):
                st.markdown(
                    f"**Passage {passage.passage_index}** · "
                    f"coherence `{passage.coherence_score:.3f}` · "
                    f"`{passage.coherence_level.value}`"
                )
                st.write(passage.passage_text)
                c1, c2 = st.columns(2)
                c1.write(f"Signal hits: **{passage.signal_hits}**")
                c2.write(f"Filter hits: **{passage.filter_hits}**")
                st.caption(passage.recovery_note)

    with tab_seams:
        seams = filter_report.editorial_seams
        if not seams:
            st.markdown(
                '<div class="empty">No editorial seams detected for this run.</div>',
                unsafe_allow_html=True,
            )
        for seam in seams:
            with st.container(border=True):
                st.markdown(f"**{seam.seam_id}** · `{seam.confidence.value}`")
                st.write(
                    f"Passage before/after: {seam.passage_before} → {seam.passage_after} | "
                    f"Coherence drop: {seam.coherence_drop:.3f}"
                )
                st.write(f"Filter layers: {', '.join(seam.filter_layers) or 'None'}")
                st.write(f"Signal layers: {', '.join(seam.signal_layers) or 'None'}")
                evidence_block(seam.evidence, "No seam evidence excerpts.")
                st.caption(seam.scholarly_parallel)

    with tab_raw:
        json_panel(
            {
                "pattern_report": result["pattern_dict"],
                "filter_report": result["filter_dict"],
            },
            "codex_analyze_raw",
        )


def render_compare() -> None:
    st.subheader("Compare")
    ctl1, ctl2 = st.columns([1, 1])
    with ctl1:
        if st.button("Load sample pair", use_container_width=True):
            load_sample("Compare")
    with ctl2:
        if st.button("Clear compare", use_container_width=True):
            clear_mode("Compare")

    up1, up2 = st.columns(2)
    with up1:
        upload_a = st.file_uploader("Upload Text A", type=["txt", "md"], key="cmp_upload_a")
    with up2:
        upload_b = st.file_uploader("Upload Text B", type=["txt", "md"], key="cmp_upload_b")

    if upload_a is not None:
        st.session_state["compare_text_a"] = _read_upload(upload_a)
    if upload_b is not None:
        st.session_state["compare_text_b"] = _read_upload(upload_b)

    labels = st.columns(2)
    with labels[0]:
        st.session_state["compare_source_a"] = st.text_input(
            "Source A", st.session_state["compare_source_a"]
        )
    with labels[1]:
        st.session_state["compare_source_b"] = st.text_input(
            "Source B", st.session_state["compare_source_b"]
        )

    traditions = st.columns(2)
    tkeys = list(KNOWN_TRADITIONS.keys())
    with traditions[0]:
        st.session_state["compare_tradition_a"] = st.selectbox(
            "Tradition A",
            options=tkeys,
            index=tkeys.index(st.session_state["compare_tradition_a"]),
        )
    with traditions[1]:
        st.session_state["compare_tradition_b"] = st.selectbox(
            "Tradition B",
            options=tkeys,
            index=tkeys.index(st.session_state["compare_tradition_b"]),
        )

    text_cols = st.columns(2)
    with text_cols[0]:
        st.session_state["compare_text_a"] = st.text_area(
            "Text A",
            value=st.session_state["compare_text_a"],
            height=220,
            placeholder="Paste or type Text A…",
        )
    with text_cols[1]:
        st.session_state["compare_text_b"] = st.text_area(
            "Text B",
            value=st.session_state["compare_text_b"],
            height=220,
            placeholder="Paste or type Text B…",
        )

    if st.button("Run comparison", type="primary", use_container_width=True):
        text_a = st.session_state["compare_text_a"].strip()
        text_b = st.session_state["compare_text_b"].strip()
        if not text_a or not text_b:
            st.warning("Please provide both Text A and Text B.")
        else:
            with st.spinner("Computing cross-tradition convergence…"):
                st.session_state["compare_result"] = run_compare(
                    text_a=text_a,
                    text_b=text_b,
                    tradition_a=st.session_state["compare_tradition_a"],
                    tradition_b=st.session_state["compare_tradition_b"],
                    source_a=st.session_state["compare_source_a"],
                    source_b=st.session_state["compare_source_b"],
                )

    result = st.session_state.get("compare_result")
    if not result:
        return

    comparison = result["comparison"]
    tab_overview, tab_shared, tab_div, tab_raw = st.tabs(
        ["Overview", "Shared Signals", "Divergence", "Raw JSON"]
    )

    with tab_overview:
        metric_cards(
            [
                ("Convergence Index", f"{comparison.convergence_index:.4f}"),
                ("Convergence State", comparison.convergence_state),
                ("Shared Pattern Count", str(comparison.shared_pattern_count)),
                ("Epsilon Δ", f"{comparison.epsilon_delta:.4f}"),
                ("Omega Δ", f"{comparison.omega_delta:.4f}"),
                ("C* Δ", f"{comparison.c_star_delta:.4f}"),
            ]
        )
        st.markdown("#### Exports")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            json_panel(result["comparison_dict"], "codex_compare")
        with c2:
            text_download("Download Markdown", result["markdown"], "codex_compare.md")
        with c3:
            text_download("Download Dashboard Text", result["dashboard_text"], "codex_compare.txt")
        with c4:
            st.download_button(
                "Download HTML",
                data=result["html"],
                file_name="codex_compare.html",
                mime="text/html",
                use_container_width=True,
            )

    with tab_shared:
        if not comparison.shared_signals:
            st.markdown(
                '<div class="empty">No shared signals above threshold.</div>',
                unsafe_allow_html=True,
            )
        for signal in comparison.shared_signals:
            with st.container(border=True):
                st.markdown(
                    f"**{signal.pattern_type.value}** · "
                    f"convergence `{signal.convergence_score:.3f}`"
                )
                st.caption(signal.tiekat_principle)
                st.write(f"A ({signal.source_a}):")
                evidence_block([signal.evidence_a])
                st.write(f"B ({signal.source_b}):")
                evidence_block([signal.evidence_b])

    with tab_div:
        if not comparison.divergence_signals:
            st.markdown(
                '<div class="empty">No major divergence signals detected.</div>',
                unsafe_allow_html=True,
            )
        for divergence in comparison.divergence_signals:
            with st.container(border=True):
                st.markdown(f"**{divergence.pattern_type.value}**")
                st.caption(divergence.tiekat_principle)
                st.write(
                    f"Strong in: **{divergence.strong_in}** | "
                    f"Weak/Absent in: **{divergence.weak_or_absent_in}**"
                )
                st.write(
                    f"Density strong: `{divergence.density_strong:.4f}` | "
                    f"Density weak: `{divergence.density_weak:.4f}`"
                )
                st.write(divergence.interpretation)

    with tab_raw:
        json_panel(result["comparison_dict"], "codex_compare_raw")


mode = st.sidebar.radio(
    "Mode",
    ["Analyze", "Compare"],
    index=0 if st.session_state["mode"] == "Analyze" else 1,
)
st.session_state["mode"] = mode
st.sidebar.markdown("---")
st.sidebar.caption("Local-first interface. No remote persistence in v1.")
st.sidebar.code("session_state only")

if mode == "Analyze":
    render_analyze()
else:
    render_compare()

st.markdown("---")
st.caption("CODEX Operator Studio v1 · additive UI layer over existing CODEX engines.")
