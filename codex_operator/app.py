"""Streamlit front-end for CODEX Operator Studio Interface v1.2."""

from __future__ import annotations

import json
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


def _save_session_payload() -> dict[str, Any]:
    analyze_result = st.session_state.get("analyze_result")
    compare_result = st.session_state.get("compare_result")
    return {
        "mode": st.session_state.get("mode", "Analyze"),
        "inputs": {
            "analyze_text": st.session_state.get("analyze_text", ""),
            "analyze_source": st.session_state.get("analyze_source", "Operator Input"),
            "analyze_tradition": st.session_state.get("analyze_tradition", "generic"),
            "compare_text_a": st.session_state.get("compare_text_a", ""),
            "compare_text_b": st.session_state.get("compare_text_b", ""),
            "compare_source_a": st.session_state.get("compare_source_a", "Text A"),
            "compare_source_b": st.session_state.get("compare_source_b", "Text B"),
            "compare_tradition_a": st.session_state.get("compare_tradition_a", "generic"),
            "compare_tradition_b": st.session_state.get("compare_tradition_b", "generic"),
        },
        "results": {
            "analyze": {
                "pattern_dict": analyze_result.get("pattern_dict") if analyze_result else None,
                "filter_dict": analyze_result.get("filter_dict") if analyze_result else None,
                "pattern_text": analyze_result.get("pattern_text") if analyze_result else "",
                "filter_text": analyze_result.get("filter_text") if analyze_result else "",
                "pattern_markdown": (
                    analyze_result.get("pattern_markdown") if analyze_result else ""
                ),
                "filter_markdown": analyze_result.get("filter_markdown") if analyze_result else "",
                "html": analyze_result.get("html") if analyze_result else "",
            },
            "compare": {
                "comparison_dict": (
                    compare_result.get("comparison_dict") if compare_result else None
                ),
                "dashboard_text": compare_result.get("dashboard_text") if compare_result else "",
                "markdown": compare_result.get("markdown") if compare_result else "",
                "html": compare_result.get("html") if compare_result else "",
            },
        },
    }


def _load_session_payload(payload: dict[str, Any]) -> None:
    inputs = payload.get("inputs", {})
    for key, value in inputs.items():
        st.session_state[key] = value

    st.session_state["mode"] = payload.get("mode", "Analyze")

    analyze = payload.get("results", {}).get("analyze", {})
    if analyze.get("pattern_dict") and analyze.get("filter_dict"):
        st.session_state["analyze_result"] = {
            "pattern_dict": analyze["pattern_dict"],
            "filter_dict": analyze["filter_dict"],
            "pattern_text": analyze.get("pattern_text", ""),
            "filter_text": analyze.get("filter_text", ""),
            "pattern_markdown": analyze.get("pattern_markdown", ""),
            "filter_markdown": analyze.get("filter_markdown", ""),
            "html": analyze.get("html", ""),
            "loaded_from_session": True,
        }

    compare = payload.get("results", {}).get("compare", {})
    if compare.get("comparison_dict"):
        st.session_state["compare_result"] = {
            "comparison_dict": compare["comparison_dict"],
            "dashboard_text": compare.get("dashboard_text", ""),
            "markdown": compare.get("markdown", ""),
            "html": compare.get("html", ""),
            "loaded_from_session": True,
        }


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


def _exports_block(items: list[tuple[str, str, str]], html: str, html_name: str) -> None:
    st.markdown("#### Exports")
    d1, d2, d3 = st.columns(3)
    with d1:
        for label, content, filename in items[:2]:
            text_download(label, content, filename)
    with d2:
        for label, content, filename in items[2:4]:
            text_download(label, content, filename)
    with d3:
        if html:
            st.download_button(
                "Download HTML",
                data=html,
                file_name=html_name,
                mime="text/html",
                use_container_width=True,
            )


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
        st.markdown(
            (
                '<div class="empty">No analysis yet. Paste text and run analysis '
                "to populate tabs.</div>"
            ),
            unsafe_allow_html=True,
        )
        return

    pattern_dict = result.get("pattern_dict", {})
    filter_dict = result.get("filter_dict", {})

    tab_overview, tab_patterns, tab_filter, tab_seams, tab_raw = st.tabs(
        ["Overview", "Patterns", "Filter Map", "Seams", "Raw JSON"]
    )

    with tab_overview:
        metric_cards(
            [
                ("Word Count", str(pattern_dict.get("word_count", 0))),
                ("Sentence Count", str(pattern_dict.get("sentence_count", 0))),
                ("Verse Count", str(pattern_dict.get("verse_count", 0))),
                ("Match Count", str(pattern_dict.get("match_count", 0))),
                ("High Confidence", str(pattern_dict.get("high_confidence", 0))),
                ("Epsilon Density", f"{pattern_dict.get('epsilon_density', 0):.4f}"),
                ("Omega Density", f"{pattern_dict.get('omega_density', 0):.4f}"),
                ("C* Density", f"{pattern_dict.get('c_star_density', 0):.4f}"),
            ]
        )
        _exports_block(
            [
                ("Patterns Markdown", result.get("pattern_markdown", ""), "codex_patterns.md"),
                ("Filter Markdown", result.get("filter_markdown", ""), "codex_filter.md"),
                ("Patterns Text", result.get("pattern_text", ""), "codex_patterns.txt"),
                ("Filter Text", result.get("filter_text", ""), "codex_filter.txt"),
            ],
            html=result.get("html", ""),
            html_name="codex_analyze.html",
        )

    with tab_patterns:
        matches = pattern_dict.get("matches", [])
        if not matches:
            st.markdown(
                '<div class="empty">No pattern matches found for this run.</div>',
                unsafe_allow_html=True,
            )
        pattern_options = ["ALL"] + sorted({m.get("pattern_type", "") for m in matches})
        confidence_options = ["ALL"] + sorted({m.get("confidence", "") for m in matches})

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            selected_pattern = st.selectbox("Pattern type", pattern_options)
        with f2:
            selected_conf = st.selectbox("Confidence", confidence_options)
        with f3:
            high_only = st.checkbox("High confidence only", value=False)
        with f4:
            structural_only = st.checkbox("Structural only", value=False)

        filtered_matches: list[dict[str, Any]] = []
        shown = 0
        for match in matches:
            conf = match.get("confidence", "")
            if selected_pattern != "ALL" and match.get("pattern_type") != selected_pattern:
                continue
            if selected_conf != "ALL" and conf != selected_conf:
                continue
            if high_only and conf not in {Confidence.HIGH.value, Confidence.STRUCTURAL.value}:
                continue
            if structural_only and conf != Confidence.STRUCTURAL.value:
                continue

            filtered_matches.append(match)
            shown += 1
            with st.container(border=True):
                st.markdown(f"**{match.get('pattern_type', 'UNKNOWN')}** · `{conf}`")
                st.caption(match.get("tiekat_principle", ""))
                st.write(match.get("description", ""))
                if match.get("structural_value") is not None:
                    st.write(f"Structural value: `{match['structural_value']}`")
                excerpts = [
                    e.get("excerpt", "") for e in match.get("evidence", []) if e.get("excerpt")
                ]
                evidence_block(excerpts, "No excerpts for this match.")
        if shown == 0 and matches:
            st.markdown(
                '<div class="empty">No matches satisfy current filters.</div>',
                unsafe_allow_html=True,
            )

        chart_scope = st.radio(
            "Pattern distribution basis",
            options=["Filtered set", "Full set"],
            horizontal=True,
            key="pattern_dist_scope",
        )
        source_for_chart = filtered_matches if chart_scope == "Filtered set" else matches
        distribution: dict[str, int] = {}
        for match in source_for_chart:
            pattern_type = match.get("pattern_type", "UNKNOWN")
            distribution[pattern_type] = distribution.get(pattern_type, 0) + 1
        if distribution:
            st.caption(
                f"Pattern distribution chart ({chart_scope.lower()}, n={len(source_for_chart)})."
            )
            st.bar_chart(
                {k: v for k, v in sorted(distribution.items(), key=lambda kv: kv[0])},
                use_container_width=True,
            )

    with tab_filter:
        passages = filter_dict.get("passages", [])
        if not passages:
            st.markdown(
                '<div class="empty">No passage analyses available.</div>',
                unsafe_allow_html=True,
            )
        if passages:
            chart_rows = []
            for passage in passages:
                chart_rows.append(
                    {
                        "passage_index": passage.get("passage_index", 0),
                        "coherence": passage.get("coherence_score", 0.0),
                        "PURE_SIGNAL": (
                            passage.get("coherence_score", 0.0)
                            if passage.get("coherence_level") == "PURE_SIGNAL"
                            else None
                        ),
                        "STRONG_SIGNAL": (
                            passage.get("coherence_score", 0.0)
                            if passage.get("coherence_level") == "STRONG_SIGNAL"
                            else None
                        ),
                        "MIXED": (
                            passage.get("coherence_score", 0.0)
                            if passage.get("coherence_level") == "MIXED"
                            else None
                        ),
                        "FILTERED": (
                            passage.get("coherence_score", 0.0)
                            if passage.get("coherence_level") == "FILTERED"
                            else None
                        ),
                        "INSTITUTIONAL": (
                            passage.get("coherence_score", 0.0)
                            if passage.get("coherence_level") == "INSTITUTIONAL"
                            else None
                        ),
                    }
                )
            st.caption("Coherence chart (passage index vs coherence score).")
            st.line_chart(
                data=chart_rows,
                x="passage_index",
                y=["coherence"],
                use_container_width=True,
            )
            st.caption("Coherence levels (point markers by level).")
            st.scatter_chart(
                data=chart_rows,
                x="passage_index",
                y=["PURE_SIGNAL", "STRONG_SIGNAL", "MIXED", "FILTERED", "INSTITUTIONAL"],
                use_container_width=True,
            )
        for passage in passages:
            idx = passage.get("passage_index", "?")
            score = passage.get("coherence_score", 0)
            level = passage.get("coherence_level", "UNKNOWN")
            with st.expander(
                f"Passage {idx} · coherence {score:.3f} · {level}",
                expanded=False,
            ):
                st.write(passage.get("passage_text", passage.get("passage_preview", "")))
                m1, m2, m3 = st.columns(3)
                m1.write(f"Signal hits: **{passage.get('signal_hits', 0)}**")
                m2.write(f"Filter hits: **{passage.get('filter_hits', 0)}**")
                m3.write(f"Words: **{passage.get('word_count', 0)}**")
                st.write(f"Recovery note: {passage.get('recovery_note', '—')}")
                st.write("Layer counts:")
                st.json(passage.get("layer_counts", {}), expanded=False)
                hits = passage.get("hits", [])
                if hits:
                    st.write("Detected hits:")
                    for hit in hits:
                        st.markdown(f"- `{hit.get('layer_type', 'LAYER')}`: {hit.get('note', '')}")
                        if hit.get("excerpt"):
                            evidence_block([hit["excerpt"]])
                else:
                    st.caption("No explicit hit excerpts recorded for this passage.")

    with tab_seams:
        seams = filter_dict.get("editorial_seams", [])
        if not seams:
            st.markdown(
                '<div class="empty">No editorial seams detected for this run.</div>',
                unsafe_allow_html=True,
            )
        for seam in seams:
            with st.container(border=True):
                st.markdown(
                    f"**{seam.get('seam_id', 'SEAM')}** · `{seam.get('confidence', 'N/A')}`"
                )
                st.write(
                    f"Passage before/after: {seam.get('passage_before')} "
                    f"→ {seam.get('passage_after')} | "
                    f"Coherence drop: {seam.get('coherence_drop', 0):.3f}"
                )
                st.write(f"Filter layers: {', '.join(seam.get('filter_layers', [])) or 'None'}")
                st.write(f"Signal layers: {', '.join(seam.get('signal_layers', [])) or 'None'}")
                evidence_block(seam.get("evidence", []), "No seam evidence excerpts.")
                st.caption(seam.get("scholarly_parallel", ""))

    with tab_raw:
        json_panel(
            {
                "pattern_report": pattern_dict,
                "filter_report": filter_dict,
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
        st.markdown(
            '<div class="empty">No comparison yet. Provide both texts and run comparison.</div>',
            unsafe_allow_html=True,
        )
        return

    comparison_dict = result.get("comparison_dict", {})
    tab_overview, tab_shared, tab_div, tab_raw = st.tabs(
        ["Overview", "Shared Signals", "Divergence", "Raw JSON"]
    )

    with tab_overview:
        metric_cards(
            [
                ("Convergence Index", f"{comparison_dict.get('convergence_index', 0):.4f}"),
                ("Convergence State", comparison_dict.get("convergence_state", "UNKNOWN")),
                ("Shared Pattern Count", str(comparison_dict.get("shared_pattern_count", 0))),
                ("Epsilon Δ", f"{comparison_dict.get('epsilon_delta', 0):.4f}"),
                ("Omega Δ", f"{comparison_dict.get('omega_delta', 0):.4f}"),
                ("C* Δ", f"{comparison_dict.get('c_star_delta', 0):.4f}"),
            ]
        )
        _exports_block(
            [
                ("Compare Markdown", result.get("markdown", ""), "codex_compare.md"),
                ("Compare Dashboard", result.get("dashboard_text", ""), "codex_compare.txt"),
                ("Source A", st.session_state.get("compare_source_a", ""), "source_a.txt"),
                ("Source B", st.session_state.get("compare_source_b", ""), "source_b.txt"),
            ],
            html=result.get("html", ""),
            html_name="codex_compare.html",
        )

    with tab_shared:
        shared = comparison_dict.get("shared_signals", [])
        if not shared:
            st.markdown(
                '<div class="empty">No shared signals above threshold.</div>',
                unsafe_allow_html=True,
            )
        for signal in shared:
            with st.container(border=True):
                st.markdown(
                    f"**{signal.get('pattern_type', 'UNKNOWN')}** · "
                    f"convergence `{signal.get('convergence_score', 0):.3f}`"
                )
                st.caption(signal.get("tiekat_principle", ""))
                left, right = st.columns(2)
                with left:
                    st.write(f"A ({signal.get('source_a', 'A')}):")
                    evidence_block([signal.get("evidence_a", "")])
                with right:
                    st.write(f"B ({signal.get('source_b', 'B')}):")
                    evidence_block([signal.get("evidence_b", "")])

    with tab_div:
        divergences = comparison_dict.get("divergence_signals", [])
        if not divergences:
            st.markdown(
                '<div class="empty">No major divergence signals detected.</div>',
                unsafe_allow_html=True,
            )
        for divergence in divergences:
            with st.container(border=True):
                st.markdown(f"**{divergence.get('pattern_type', 'UNKNOWN')}**")
                st.caption(divergence.get("tiekat_principle", ""))
                left, right = st.columns(2)
                with left:
                    st.write("Tradition A")
                    status_a = "Strong" if divergence.get("strong_in") == "A" else "Weak/Absent"
                    st.write(f"Status: **{status_a}**")
                    st.write(f"Density: `{divergence.get('density_strong', 0):.4f}`")
                with right:
                    st.write("Tradition B")
                    status_b = "Strong" if divergence.get("strong_in") == "B" else "Weak/Absent"
                    st.write(f"Status: **{status_b}**")
                    st.write(f"Density: `{divergence.get('density_weak', 0):.4f}`")
                st.write(divergence.get("interpretation", ""))

    with tab_raw:
        json_panel(comparison_dict, "codex_compare_raw")


mode = st.sidebar.radio(
    "Mode",
    ["Analyze", "Compare"],
    index=0 if st.session_state["mode"] == "Analyze" else 1,
)
st.session_state["mode"] = mode
st.sidebar.markdown("---")
st.sidebar.caption("Local-first interface. No remote persistence in v1.2.")

session_upload = st.sidebar.file_uploader(
    "Import session (.json)",
    type=["json"],
    key="session_import",
)
if session_upload is not None:
    try:
        _load_session_payload(json.loads(session_upload.getvalue().decode("utf-8")))
        st.sidebar.success("Session imported.")
    except Exception as exc:  # noqa: BLE001 - UI feedback only
        st.sidebar.error(f"Invalid session file: {exc}")

session_blob = json.dumps(_save_session_payload(), indent=2, ensure_ascii=False)
st.sidebar.download_button(
    "Export session",
    data=session_blob,
    file_name="codex_operator_session.json",
    mime="application/json",
    use_container_width=True,
)

if mode == "Analyze":
    render_analyze()
else:
    render_compare()

st.markdown("---")
st.caption("CODEX Operator Studio v1.2 · additive UI layer over existing CODEX engines.")
