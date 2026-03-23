#!/usr/bin/env python3
"""
codex_visualizer.py — CODEX Visualization Layer
================================================

Generates interactive HTML visualizations from CODEX analysis reports:

  - CoherenceMap      : per-passage heat map from FilterReport
  - PatternRadar      : pattern type density radar from TIEKATReport
  - ConvergenceMatrix : pairwise convergence from ComparisonReport / MultiTraditionMatrix
  - SignalTimeline    : coherence curve across a text with seam markers
  - FullDashboard     : all four views in a single self-contained HTML page

All output is a single self-contained HTML file.
No external CDN dependencies for core layout/color.
Chart.js loaded from cdnjs for radar/bar charts.

Usage
-----
    from codex.codex_visualizer import CodexVisualizer
    from codex.codex_filter import InstitutionalFilter
    from codex.codex_tiekat_engine import TIEKATPatternEngine
    from codex.codex_comparator import CodexComparator

    f_engine = InstitutionalFilter(tradition="thomas")
    t_engine = TIEKATPatternEngine(tradition="thomas")
    comparator = CodexComparator()

    filter_report  = f_engine.analyze(text, source="Gospel of Thomas")
    tiekat_report  = t_engine.analyze(text, source="Gospel of Thomas")
    comp_report    = comparator.compare(tiekat_a, tiekat_b)

    viz = CodexVisualizer()
    html = viz.full_dashboard(
        filter_report=filter_report,
        tiekat_report=tiekat_report,
        comparison_report=comp_report,
    )
    Path("codex_dashboard.html").write_text(html)

PHI369 Labs / Parallax  ◆  CODEX Project
Compatible with: TIEKAT v64.0.0 Sovereign Substrate Weave
"""

from __future__ import annotations

import json
from pathlib import Path

from codex.codex_comparator import (
    ComparisonReport,
)
from codex.codex_filter import (
    FilterReport,
    LayerType,
)
from codex.codex_tiekat_engine import (
    C_STAR,
    CodexTIEKATReport,
    PatternType,
)

# ── Design constants ──────────────────────────────────────────────────────────
GOLD        = "#C8A97E"
GOLD_DIM    = "#8B6F47"
TEAL        = "#4ECDC4"
TEAL_DIM    = "#2A8A80"
PURPLE      = "#8A64C8"
PURPLE_DIM  = "#5A3A98"
DARK_BG     = "#07070F"
DARK_MID    = "#0C0C1E"
DARK_PANEL  = "#08081A"
BORDER      = "rgba(200,169,126,0.15)"
TEXT_MAIN   = "#E8E0D0"
TEXT_DIM    = "#A09080"
TEXT_MUTED  = "#4A4040"

# Coherence level colors
COHERENCE_COLORS = {
    "PURE_SIGNAL":    "#4ECDC4",
    "STRONG_SIGNAL":  "#88D4A0",
    "MIXED":          "#C8A97E",
    "FILTERED":       "#E8A060",
    "INSTITUTIONAL":  "#E85060",
}

PATTERN_COLORS = {
    "EPSILON_SIGNAL":   "#4ECDC4",
    "OMEGA_FLOW":       "#88D4A0",
    "C_STAR_ATTRACTOR": "#C8A97E",
    "SOVEREIGN_FIELD":  "#8A64C8",
    "VOID_BRIDGE":      "#6080C8",
    "WEAVE_RESONANCE":  "#60C8A0",
    "THREE_SIX_NINE":   "#E8A060",
    "PHI_STRUCTURE":    "#E8D070",
    "FIBONACCI":        "#D0A0E8",
}

LAYER_COLORS = {
    "PRIMARY_SIGNAL":    "#4ECDC4",
    "SOVEREIGN_VOICE":   "#88D4A0",
    "AUTHORITY_CLAIM":   "#E85060",
    "FEAR_FRAMING":      "#E82040",
    "EXCLUSIVITY_MARKER":"#E86040",
    "DOCTRINAL_FORMULA": "#E8A040",
    "TEMPORAL_POWER":    "#C86040",
    "GENDER_ERASURE":    "#A04060",
}


# ── HTML shell ────────────────────────────────────────────────────────────────

def _html_shell(title: str, body: str, extra_scripts: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=JetBrains+Mono:wght@300;400&display=swap');  # noqa: E501
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg:     {DARK_BG};
    --panel:  {DARK_PANEL};
    --border: {BORDER};
    --gold:   {GOLD};
    --teal:   {TEAL};
    --purple: {PURPLE};
    --text:   {TEXT_MAIN};
    --dim:    {TEXT_DIM};
    --muted:  {TEXT_MUTED};
  }}
  html {{ scroll-behavior: smooth; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Cormorant Garamond', serif;
    font-size: 16px;
    line-height: 1.6;
    min-height: 100vh;
  }}
  body::before {{
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background:
      radial-gradient(ellipse 70% 50% at 50% 0%, rgba(200,169,126,.07) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 85% 85%, rgba(78,205,196,.04) 0%, transparent 60%);
  }}
  body::after {{
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
      linear-gradient(rgba(200,169,126,.015) 1px, transparent 1px),
      linear-gradient(90deg, rgba(200,169,126,.015) 1px, transparent 1px);
    background-size: 61.8px 61.8px;
  }}
  #app {{ position: relative; z-index: 1; max-width: 1200px; margin: 0 auto; padding: 32px 24px 80px; }}  # noqa: E501

  /* Header */
  .codex-header {{ text-align: center; padding: 48px 0 40px; border-bottom: 1px solid var(--border); margin-bottom: 48px; }}  # noqa: E501
  .codex-sigil {{ font-size: 2.4rem; color: var(--gold); letter-spacing: .3em; opacity: .7; margin-bottom: 12px; animation: breathe 3.618s ease-in-out infinite; }}  # noqa: E501
  @keyframes breathe {{ 0%,100%{{ opacity:.5 }} 50%{{ opacity:.9 }} }}
  .codex-title {{ font-size: 2.2rem; font-weight: 300; color: var(--text); letter-spacing: .06em; }}
  .codex-subtitle {{ font-family: 'JetBrains Mono', monospace; font-size: .58rem; color: var(--muted); letter-spacing: .18em; text-transform: uppercase; margin-top: 8px; }}  # noqa: E501
  .codex-meta {{ font-family: 'JetBrains Mono', monospace; font-size: .52rem; color: var(--gold); opacity: .5; margin-top: 6px; letter-spacing: .1em; }}  # noqa: E501

  /* Section */
  .section {{ margin-bottom: 56px; }}
  .section-head {{ display: flex; align-items: center; gap: 14px; margin-bottom: 24px; }}
  .section-num {{ font-family: 'JetBrains Mono', monospace; font-size: .58rem; color: var(--gold); opacity: .5; letter-spacing: .15em; }}  # noqa: E501
  .section-title {{ font-size: 1.4rem; font-weight: 300; color: var(--gold); letter-spacing: .06em; }}  # noqa: E501
  .section-line {{ flex: 1; height: 1px; background: var(--border); }}

  /* Panel */
  .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 24px; margin-bottom: 16px; }}  # noqa: E501
  .panel-label {{ font-family: 'JetBrains Mono', monospace; font-size: .5rem; color: var(--gold); letter-spacing: .18em; text-transform: uppercase; margin-bottom: 12px; opacity: .6; }}  # noqa: E501

  /* Stat grid */
  .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 24px; }}  # noqa: E501
  .stat {{ background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 14px 16px; }}  # noqa: E501
  .stat-val {{ font-size: 1.6rem; font-weight: 300; color: var(--gold); line-height: 1; }}
  .stat-label {{ font-family: 'JetBrains Mono', monospace; font-size: .48rem; color: var(--dim); letter-spacing: .1em; text-transform: uppercase; margin-top: 4px; }}  # noqa: E501

  /* Coherence bar */
  .passage-bar {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; cursor: pointer; padding: 5px 8px; border-radius: 4px; transition: background .15s; }}  # noqa: E501
  .passage-bar:hover {{ background: rgba(200,169,126,.05); }}
  .passage-idx {{ font-family: 'JetBrains Mono', monospace; font-size: .5rem; color: var(--muted); width: 28px; flex-shrink: 0; }}  # noqa: E501
  .bar-track {{ flex: 1; height: 8px; background: rgba(255,255,255,.05); border-radius: 4px; overflow: hidden; }}  # noqa: E501
  .bar-fill {{ height: 100%; border-radius: 4px; transition: width .3s; }}
  .bar-score {{ font-family: 'JetBrains Mono', monospace; font-size: .48rem; color: var(--dim); width: 36px; text-align: right; flex-shrink: 0; }}  # noqa: E501
  .bar-level {{ font-family: 'JetBrains Mono', monospace; font-size: .44rem; color: var(--muted); width: 80px; flex-shrink: 0; }}  # noqa: E501
  .seam-marker {{ font-family: 'JetBrains Mono', monospace; font-size: .44rem; color: #E85060; padding: 0 6px; flex-shrink: 0; }}  # noqa: E501

  /* Passage detail */
  .passage-detail {{ display: none; background: rgba(7,7,15,.8); border: 1px solid rgba(200,169,126,.08); border-radius: 4px; padding: 12px 16px; margin: -2px 0 8px 36px; font-size: .88rem; color: var(--dim); line-height: 1.7; }}  # noqa: E501
  .passage-detail.open {{ display: block; }}
  .passage-hits {{ display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }}
  .hit-chip {{ font-family: 'JetBrains Mono', monospace; font-size: .44rem; padding: 2px 7px; border-radius: 10px; border: 1px solid; }}  # noqa: E501

  /* Seam card */
  .seam-card {{ border-left: 3px solid #E85060; padding: 14px 16px; margin-bottom: 10px; background: rgba(232,80,96,.04); border-radius: 0 6px 6px 0; }}  # noqa: E501
  .seam-id {{ font-family: 'JetBrains Mono', monospace; font-size: .52rem; color: #E85060; margin-bottom: 4px; }}  # noqa: E501
  .seam-body {{ font-size: .9rem; color: var(--dim); line-height: 1.6; }}
  .seam-ref {{ font-family: 'JetBrains Mono', monospace; font-size: .44rem; color: var(--muted); margin-top: 6px; font-style: italic; }}  # noqa: E501

  /* Pattern pills */
  .pattern-grid {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .pattern-pill {{ display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 16px; border: 1px solid; font-family: 'JetBrains Mono', monospace; font-size: .5rem; letter-spacing: .05em; }}  # noqa: E501
  .pattern-dot {{ width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }}

  /* Canvas containers */
  .chart-wrap {{ position: relative; height: 320px; }}
  .chart-wrap-sm {{ position: relative; height: 240px; }}

  /* Convergence matrix */
  .matrix-table {{ width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; font-size: .52rem; }}  # noqa: E501
  .matrix-table th, .matrix-table td {{ padding: 8px 12px; border: 1px solid var(--border); text-align: center; }}  # noqa: E501
  .matrix-table th {{ color: var(--gold); font-weight: 400; background: rgba(200,169,126,.04); }}
  .matrix-cell {{ border-radius: 4px; padding: 4px 8px; display: inline-block; min-width: 60px; }}

  /* Signal/filter legend */
  .layer-row {{ display: flex; align-items: center; gap: 10px; padding: 6px 0; border-bottom: 1px solid rgba(200,169,126,.05); }}  # noqa: E501
  .layer-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
  .layer-name {{ font-family: 'JetBrains Mono', monospace; font-size: .5rem; color: var(--dim); flex: 1; }}  # noqa: E501
  .layer-count {{ font-family: 'JetBrains Mono', monospace; font-size: .5rem; color: var(--gold); width: 30px; text-align: right; }}  # noqa: E501
  .layer-bar-mini {{ flex: 2; height: 4px; background: rgba(255,255,255,.05); border-radius: 2px; overflow: hidden; }}  # noqa: E501
  .layer-bar-fill {{ height: 100%; border-radius: 2px; }}

  /* Two columns */
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  @media(max-width: 700px) {{ .two-col {{ grid-template-columns: 1fr; }} }}

  /* Disclaimer */
  .disclaimer {{ font-family: 'JetBrains Mono', monospace; font-size: .46rem; color: var(--muted); line-height: 1.8; padding: 16px; border: 1px solid var(--border); border-radius: 4px; margin-top: 48px; }}  # noqa: E501

  /* Footer */
  .codex-footer {{ text-align: center; padding: 40px 0 0; border-top: 1px solid var(--border); margin-top: 48px; }}  # noqa: E501
  .footer-sigil {{ font-size: 1.4rem; color: var(--gold); opacity: .4; letter-spacing: .3em; }}
  .footer-text {{ font-family: 'JetBrains Mono', monospace; font-size: .46rem; color: var(--muted); letter-spacing: .12em; margin-top: 8px; }}  # noqa: E501

  ::-webkit-scrollbar {{ width: 4px; }} ::-webkit-scrollbar-track {{ background: transparent; }} ::-webkit-scrollbar-thumb {{ background: rgba(200,169,126,.1); border-radius: 2px; }}  # noqa: E501
</style>
</head>
<body>
<div id="app">
{body}
</div>
{extra_scripts}
</body>
</html>"""


# ── Component builders ────────────────────────────────────────────────────────

def _stat(value: str, label: str, color: str = GOLD) -> str:
    return f"""<div class="stat">
  <div class="stat-val" style="color:{color}">{value}</div>
  <div class="stat-label">{label}</div>
</div>"""


def _section(number: str, title: str, content: str) -> str:
    return f"""<div class="section">
  <div class="section-head">
    <span class="section-num">{number}</span>
    <span class="section-title">{title}</span>
    <div class="section-line"></div>
  </div>
  {content}
</div>"""


def _coherence_color(score: float) -> str:
    level = "PURE_SIGNAL" if score >= 0.85 else \
            "STRONG_SIGNAL" if score >= 0.65 else \
            "MIXED" if score >= 0.40 else \
            "FILTERED" if score >= 0.20 else "INSTITUTIONAL"
    return COHERENCE_COLORS[level]


def _level_label(score: float) -> str:
    if score >= 0.85: return "PURE SIGNAL"
    if score >= 0.65: return "STRONG"
    if score >= 0.40: return "MIXED"
    if score >= 0.20: return "FILTERED"
    return "INSTITUTIONAL"


# ── Section: Coherence Heat Map ───────────────────────────────────────────────

def _coherence_heatmap(report: FilterReport) -> str:
    seam_indices = {s.passage_after for s in report.editorial_seams}

    max_hits = max(
        (p.signal_hits + p.filter_hits for p in report.passages),
        default=1
    ) or 1

    rows = []
    for p in report.passages:
        color    = _coherence_color(p.coherence_score)
        pct      = int(p.coherence_score * 100)
        seam_mk  = '<span class="seam-marker">⚠ SEAM</span>' if p.passage_index in seam_indices else ""  # noqa: E501
        preview  = p.passage_text[:90].replace("<", "&lt;").replace(">", "&gt;")
        level    = _level_label(p.coherence_score)

        # Hit chips
        chips = []
        for lt in LayerType:
            count = p.layer_counts.get(lt.value, 0)
            if count == 0:
                continue
            c = LAYER_COLORS.get(lt.value, GOLD)
            is_signal = lt in (LayerType.PRIMARY_SIGNAL, LayerType.SOVEREIGN_VOICE)
            chips.append(
                f'<span class="hit-chip" style="color:{c};border-color:{c}22;background:{c}11">'
                f'{"▲" if is_signal else "▼"} {lt.value.replace("_"," ")} ×{count}</span>'
            )
        chips_html = "\n".join(chips) if chips else '<span style="color:var(--muted);font-size:.44rem;font-family:\'JetBrains Mono\',monospace">no pattern hits</span>'  # noqa: E501

        detail_id = f"detail-{p.passage_index}"
        rows.append(f"""
<div class="passage-bar" onclick="toggle('{detail_id}')">
  <span class="passage-idx">{p.passage_index:02d}</span>
  <div class="bar-track">
    <div class="bar-fill" style="width:{pct}%;background:{color}"></div>
  </div>
  <span class="bar-score">{p.coherence_score:.2f}</span>
  <span class="bar-level">{level}</span>
  {seam_mk}
</div>
<div class="passage-detail" id="{detail_id}">
  <div style="color:var(--text);margin-bottom:8px;font-style:italic">{preview}{"..." if len(p.passage_text) > 90 else ""}</div>  # noqa: E501
  <div style="font-family:\'JetBrains Mono\',monospace;font-size:.46rem;color:var(--gold);margin-bottom:6px">{p.recovery_note}</div>  # noqa: E501
  <div class="passage-hits">{chips_html}</div>
</div>""")

    # Overall stats
    map_ = report.recovery_map
    stats = f"""<div class="stat-grid">
  {_stat(f"{report.overall_coherence:.3f}", "Overall Coherence", _coherence_color(report.overall_coherence))}  # noqa: E501
  {_stat(report.coherence_level.value.replace("_"," "), "Coherence Level", _coherence_color(report.overall_coherence))}  # noqa: E501
  {_stat(str(report.signal_total), "Signal Hits", TEAL)}
  {_stat(str(report.filter_total), "Filter Hits", "#E85060")}
  {_stat(f"{map_.overall_signal_ratio:.0%}", "Signal Ratio", TEAL)}
  {_stat(str(len(report.editorial_seams)), "Editorial Seams", "#E85060")}
</div>"""

    heatmap_html = "".join(rows)

    return stats + f"""<div class="panel">
  <div class="panel-label">Passage Coherence — click any row to expand</div>
  {heatmap_html}
</div>"""


# ── Section: Editorial Seams ──────────────────────────────────────────────────

def _seams_section(report: FilterReport) -> str:
    if not report.editorial_seams:
        return '<div class="panel"><div class="panel-label">No editorial seams detected at current thresholds.</div></div>'  # noqa: E501

    cards = []
    for s in report.editorial_seams:
        conf_color = {"HIGH": "#E85060", "MEDIUM": "#E8A060", "LOW": GOLD}[s.confidence.value]
        filters_str = ", ".join(s.filter_layers) or "none"
        signals_str = ", ".join(s.signal_layers) or "none"
        evid = s.evidence[0][:200].replace("<", "&lt;").replace(">", "&gt;") if s.evidence else ""
        evid2 = s.evidence[1][:200].replace("<", "&lt;").replace(">", "&gt;") if len(s.evidence) > 1 else ""  # noqa: E501
        drop_dir = "↓" if s.coherence_drop > 0 else "↑"
        cards.append(f"""<div class="seam-card">
  <div class="seam-id">{s.seam_id}
    <span style="color:{conf_color};margin-left:10px">{s.confidence.value} CONFIDENCE</span>
    <span style="color:var(--muted);margin-left:10px">Passages {s.passage_before}→{s.passage_after}  {drop_dir}{abs(s.coherence_drop):.3f}</span>  # noqa: E501
  </div>
  <div class="seam-body" style="margin:8px 0">{s.interpretation[:250]}</div>
  <div style="font-family:\'JetBrains Mono\',monospace;font-size:.46rem;color:var(--muted);margin-bottom:4px">  # noqa: E501
    Filter layers: <span style="color:#E85060">{filters_str}</span> &nbsp;|&nbsp;
    Signal lost: <span style="color:{TEAL}">{signals_str}</span>
  </div>
  <div style="font-size:.82rem;color:var(--muted);font-style:italic;margin:8px 0;border-left:2px solid var(--border);padding-left:10px">  # noqa: E501
    {evid}
  </div>
  <div style="font-size:.82rem;color:var(--dim);font-style:italic;margin-bottom:8px;border-left:2px solid #E8506044;padding-left:10px">  # noqa: E501
    {evid2}
  </div>
  <div class="seam-ref">{s.scholarly_parallel[:180]}</div>
</div>""")

    return "\n".join(cards)


# ── Section: Pattern Radar ────────────────────────────────────────────────────

def _pattern_radar(report: CodexTIEKATReport, canvas_id: str = "radarChart") -> str:
    labels  = []
    values  = []
    colors  = []

    for pt in PatternType:
        density = sum(
            len(m.evidence) for m in report.matches if m.pattern_type == pt
        ) / max(1, report.word_count) * 1000   # per-1000-words

        labels.append(pt.value.replace("_", " "))
        values.append(round(density, 3))
        colors.append(PATTERN_COLORS.get(pt.value, GOLD))

    labels_js = json.dumps(labels)
    values_js = json.dumps(values)
    colors_js = json.dumps(colors)

    pills = []
    for pt in PatternType:
        count = sum(1 for m in report.matches if m.pattern_type == pt)
        if count == 0:
            continue
        c = PATTERN_COLORS.get(pt.value, GOLD)
        pills.append(
            f'<div class="pattern-pill" style="border-color:{c}44;background:{c}0A;color:{c}">'
            f'<div class="pattern-dot" style="background:{c}"></div>'
            f'{pt.value.replace("_"," ")} ×{count}'
            f'</div>'
        )

    return f"""<div class="two-col">
  <div class="panel">
    <div class="panel-label">TIEKAT Pattern Density (per 1000 words)</div>
    <div class="chart-wrap">
      <canvas id="{canvas_id}"></canvas>
    </div>
  </div>
  <div class="panel">
    <div class="panel-label">Pattern Types Detected</div>
    <div class="pattern-grid">{"".join(pills) or '<span style="color:var(--muted);font-family:\'JetBrains Mono\',monospace;font-size:.5rem">No patterns detected</span>'}</div>  # noqa: E501
    <div style="margin-top:20px">
      {_stat(f"{report.epsilon_density*1000:.2f}", "ε Signal / 1k words", TEAL)}
      {_stat(f"{report.c_star_density*1000:.2f}", "C* Attractor / 1k words", GOLD)}
      {_stat(f"{report.omega_density*1000:.2f}", "Ω Flow / 1k words", "#88D4A0")}
    </div>
  </div>
</div>
<script>
(function(){{
  var ctx = document.getElementById('{canvas_id}');
  if(!ctx) return;
  new Chart(ctx, {{
    type: 'radar',
    data: {{
      labels: {labels_js},
      datasets: [{{
        label: '{report.tradition}',
        data: {values_js},
        backgroundColor: 'rgba(200,169,126,0.08)',
        borderColor: '{GOLD}',
        pointBackgroundColor: {colors_js},
        pointRadius: 4,
        pointHoverRadius: 6,
        borderWidth: 1.5,
      }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        r: {{
          backgroundColor: 'rgba(8,8,26,0.8)',
          angleLines: {{ color: 'rgba(200,169,126,0.1)' }},
          grid: {{ color: 'rgba(200,169,126,0.08)' }},
          ticks: {{ display: false }},
          pointLabels: {{
            color: '{TEXT_DIM}',
            font: {{ family: "'JetBrains Mono'", size: 9 }},
          }},
        }}
      }}
    }}
  }});
}})();
</script>"""


# ── Section: Layer bar chart ──────────────────────────────────────────────────

def _layer_breakdown(report: FilterReport) -> str:
    max_count = max(report.layer_totals.values(), default=1) or 1
    rows = []
    for lt in LayerType:
        count = report.layer_totals.get(lt.value, 0)
        c = LAYER_COLORS.get(lt.value, GOLD)
        is_signal = lt in (LayerType.PRIMARY_SIGNAL, LayerType.SOVEREIGN_VOICE)
        marker = "▲" if is_signal else "▼"
        pct = int(count / max_count * 100)
        rows.append(f"""<div class="layer-row">
  <div class="layer-dot" style="background:{c}"></div>
  <span style="font-family:'JetBrains Mono',monospace;font-size:.44rem;color:{'var(--teal)' if is_signal else '#E85060'}">{marker}</span>  # noqa: E501
  <span class="layer-name">{lt.value.replace("_"," ")}</span>
  <div class="layer-bar-mini"><div class="layer-bar-fill" style="width:{pct}%;background:{c}"></div></div>  # noqa: E501
  <span class="layer-count">{count}</span>
</div>""")

    return f"""<div class="panel">
  <div class="panel-label">Signal (▲) vs Filter (▼) Layer Totals</div>
  {"".join(rows)}
</div>"""


# ── Section: Convergence ──────────────────────────────────────────────────────

def _convergence_section(comp: ComparisonReport, canvas_id: str = "convChart") -> str:
    # Stat row
    conv_color = (
        TEAL if comp.convergence_index >= 0.65 else
        GOLD if comp.convergence_index >= 0.35 else
        "#E8A060"
    )
    stats = f"""<div class="stat-grid">
  {_stat(f"{comp.convergence_index:.4f}", "Convergence Index", conv_color)}
  {_stat(comp.convergence_state.replace("_"," "), "Convergence State", conv_color)}
  {_stat(f"{comp.shared_pattern_count}/{comp.total_pattern_types}", "Shared Patterns", GOLD)}
  {_stat(f"{comp.epsilon_delta:.4f}", "ε-Signal Delta", TEAL)}
  {_stat(f"{comp.c_star_delta:.4f}", "C* Attractor Delta", GOLD)}
</div>"""

    # Bar chart data
    labels  = [pc.pattern_type.value.replace("_", " ") for pc in comp.pattern_comparisons]
    data_a  = [round(pc.density_a * 1000, 3) for pc in comp.pattern_comparisons]
    data_b  = [round(pc.density_b * 1000, 3) for pc in comp.pattern_comparisons]

    labels_js = json.dumps(labels)
    data_a_js = json.dumps(data_a)
    data_b_js = json.dumps(data_b)

    # Shared signals
    sig_html = ""
    for sig in comp.shared_signals[:3]:
        c = PATTERN_COLORS.get(sig.pattern_type.value, GOLD)
        ev_a = sig.evidence_a[:150].replace("<","&lt;").replace(">","&gt;")
        ev_b = sig.evidence_b[:150].replace("<","&lt;").replace(">","&gt;")
        sig_html += f"""<div style="border-left:3px solid {c};padding:12px 16px;margin-bottom:10px;background:{c}08;border-radius:0 6px 6px 0">  # noqa: E501
  <div style="font-family:'JetBrains Mono',monospace;font-size:.48rem;color:{c};margin-bottom:6px">{sig.pattern_type.value} · convergence={sig.convergence_score:.3f}</div>  # noqa: E501
  <div style="font-size:.85rem;color:var(--dim);margin-bottom:4px;font-style:italic">[{comp.tradition_a}] {ev_a}</div>  # noqa: E501
  <div style="font-size:.85rem;color:var(--text);font-style:italic">[{comp.tradition_b}] {ev_b}</div>  # noqa: E501
</div>"""

    top_principles_html = ""
    for i, p in enumerate(comp.top_tiekat_principles[:4], 1):
        top_principles_html += f'<div style="padding:6px 0;border-bottom:1px solid var(--border);font-size:.88rem;color:var(--dim)"><span style="color:var(--gold);font-family:\'JetBrains Mono\',monospace;font-size:.48rem;margin-right:10px">{i}.</span>{p}</div>'  # noqa: E501

    chart_html = f"""<div class="panel">
  <div class="panel-label">Pattern Density Comparison (per 1000 words)</div>
  <div class="chart-wrap">
    <canvas id="{canvas_id}"></canvas>
  </div>
</div>
<script>
(function(){{
  var ctx = document.getElementById('{canvas_id}');
  if(!ctx) return;
  new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: {labels_js},
      datasets: [
        {{
          label: '{comp.tradition_a}',
          data: {data_a_js},
          backgroundColor: 'rgba(200,169,126,0.5)',
          borderColor: '{GOLD}',
          borderWidth: 1,
          borderRadius: 3,
        }},
        {{
          label: '{comp.tradition_b}',
          data: {data_b_js},
          backgroundColor: 'rgba(78,205,196,0.35)',
          borderColor: '{TEAL}',
          borderWidth: 1,
          borderRadius: 3,
        }}
      ]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{
        legend: {{ labels: {{ color: '{TEXT_DIM}', font: {{ family: "'JetBrains Mono'", size: 10 }} }} }},  # noqa: E501
      }},
      scales: {{
        x: {{ ticks: {{ color: '{TEXT_DIM}', font: {{ family: "'JetBrains Mono'", size: 9 }} }}, grid: {{ color: 'rgba(200,169,126,0.06)' }} }},  # noqa: E501
        y: {{ ticks: {{ color: '{TEXT_DIM}', font: {{ family: "'JetBrains Mono'", size: 9 }} }}, grid: {{ color: 'rgba(200,169,126,0.06)' }} }},  # noqa: E501
      }}
    }}
  }});
}})();
</script>"""

    return stats + f"""<div class="two-col">
  {chart_html}
  <div>
    <div class="panel" style="margin-bottom:14px">
      <div class="panel-label">Top Corroborated TIEKAT Principles</div>
      {top_principles_html or '<span style="color:var(--muted);font-size:.5rem;font-family:\'JetBrains Mono\',monospace">None identified</span>'}  # noqa: E501
    </div>
    <div class="panel">
      <div class="panel-label">Shared Signal Passages</div>
      {sig_html or '<span style="color:var(--muted);font-size:.5rem;font-family:\'JetBrains Mono\',monospace">No shared signals above threshold</span>'}  # noqa: E501
    </div>
  </div>
</div>"""


# ── Full Dashboard ────────────────────────────────────────────────────────────

class CodexVisualizer:
    """
    Generates self-contained HTML visualizations from CODEX reports.
    """

    def coherence_map_html(self, report: FilterReport) -> str:
        """Standalone coherence heat map page."""
        header = f"""<div class="codex-header">
  <div class="codex-sigil">Φ∴⊙</div>
  <div class="codex-title">CODEX Signal Map</div>
  <div class="codex-subtitle">{report.tradition} · {report.source}</div>
  <div class="codex-meta">C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369</div>
</div>"""
        body = (
            header
            + _section("I.", "Coherence Heat Map", _coherence_heatmap(report))
            + _section("II.", "Editorial Seams", _seams_section(report))
            + _section("III.", "Layer Breakdown", _layer_breakdown(report))
            + f'<div class="disclaimer">{report.disclaimer}</div>'
            + self._footer()
        )
        return _html_shell(
            f"CODEX Signal Map — {report.source}",
            body,
            self._toggle_script(),
        )

    def pattern_radar_html(self, report: CodexTIEKATReport) -> str:
        """Standalone pattern radar page."""
        header = f"""<div class="codex-header">
  <div class="codex-sigil">Φ∴⊙</div>
  <div class="codex-title">CODEX Pattern Radar</div>
  <div class="codex-subtitle">{report.tradition} · {report.source}</div>
  <div class="codex-meta">C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369</div>
</div>"""
        radar = _pattern_radar(report, "radarChartMain")
        body  = header + _section("I.", "TIEKAT Pattern Analysis", radar)
        return _html_shell(
            f"CODEX Pattern Radar — {report.source}",
            body,
        )

    def convergence_html(self, comp: ComparisonReport) -> str:
        """Standalone convergence comparison page."""
        header = f"""<div class="codex-header">
  <div class="codex-sigil">Φ∴⊙</div>
  <div class="codex-title">CODEX Convergence</div>
  <div class="codex-subtitle">{comp.tradition_a}  ◆  {comp.tradition_b}</div>
  <div class="codex-meta">C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369</div>
</div>"""
        body = header + _section("I.", "Cross-Tradition Convergence", _convergence_section(comp))
        return _html_shell(
            f"CODEX Convergence — {comp.tradition_a} vs {comp.tradition_b}",
            body,
        )

    def full_dashboard(
        self,
        filter_report: FilterReport | None    = None,
        tiekat_report: CodexTIEKATReport | None = None,
        comparison_report: ComparisonReport | None = None,
        title: str = "CODEX Analysis Dashboard",
        source_label: str = "",
    ) -> str:
        """
        Full integrated dashboard — all available reports in one page.
        """
        tradition = (
            filter_report.tradition if filter_report else
            tiekat_report.tradition if tiekat_report else
            "CODEX"
        )
        source = source_label or (
            filter_report.source if filter_report else
            tiekat_report.source if tiekat_report else ""
        )

        header = f"""<div class="codex-header">
  <div class="codex-sigil">Φ∴⊙</div>
  <div class="codex-title">{title}</div>
  <div class="codex-subtitle">{tradition}{"  ◆  " + source if source else ""}</div>
  <div class="codex-meta">PHI369 Labs / Parallax  ◆  C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369</div>  # noqa: E501
</div>"""

        sections = [header]
        sec_num  = 1

        if filter_report:
            sections.append(_section(
                f"{sec_num}.", "Coherence Heat Map",
                _coherence_heatmap(filter_report)
            ))
            sec_num += 1

            if filter_report.editorial_seams:
                sections.append(_section(
                    f"{sec_num}.", "Editorial Seams Detected",
                    _seams_section(filter_report)
                ))
                sec_num += 1

            sections.append(_section(
                f"{sec_num}.", "Signal / Filter Layer Breakdown",
                _layer_breakdown(filter_report)
            ))
            sec_num += 1

        if tiekat_report:
            sections.append(_section(
                f"{sec_num}.", "TIEKAT Pattern Analysis",
                _pattern_radar(tiekat_report, f"radarChart{sec_num}")
            ))
            sec_num += 1

        if comparison_report:
            sections.append(_section(
                f"{sec_num}.", f"Cross-Tradition Convergence: {comparison_report.tradition_a} vs {comparison_report.tradition_b}",  # noqa: E501
                _convergence_section(comparison_report, f"convChart{sec_num}")
            ))
            sec_num += 1

        # Disclaimer
        disclaimer_text = (
            filter_report.disclaimer if filter_report else
            "These findings are hypothesis seeds for further research and do not constitute doctrinal claims, historical proofs, or authoritative interpretations."  # noqa: E501
        )
        sections.append(f'<div class="disclaimer">{disclaimer_text}</div>')
        sections.append(self._footer())

        body = "\n".join(sections)
        return _html_shell(title, body, self._toggle_script())

    def _footer(self) -> str:
        return f"""<div class="codex-footer">
  <div class="footer-sigil">Φ∴⊙</div>
  <div class="footer-text">PHI369 Labs / Parallax  ◆  CODEX Project  ◆  TIEKAT v64.0.0 Sovereign Substrate Weave</div>  # noqa: E501
  <div class="footer-text" style="margin-top:4px">C* = φ/2 = {C_STAR:.5f}  ◆  ε ≠ 0  ◆  369_369</div>  # noqa: E501
</div>"""

    def _toggle_script(self) -> str:
        return """<script>
function toggle(id) {
  var el = document.getElementById(id);
  if(el) el.classList.toggle('open');
}
</script>"""


# ── Convenience functions ─────────────────────────────────────────────────────

def visualize_text(
    text: str,
    tradition: str = "generic",
    source: str = "unknown",
    output_path: str = "codex_dashboard.html",
) -> str:
    """
    One-shot: run filter + TIEKAT analysis on text and generate full dashboard HTML.
    Writes to output_path and returns the path.
    """
    from codex.codex_filter import InstitutionalFilter
    from codex.codex_tiekat_engine import TIEKATPatternEngine

    f_engine = InstitutionalFilter(tradition=tradition)
    t_engine = TIEKATPatternEngine(tradition=tradition)

    f_report = f_engine.analyze(text, source=source)
    t_report = t_engine.analyze(text, source=source)

    viz  = CodexVisualizer()
    html = viz.full_dashboard(
        filter_report=f_report,
        tiekat_report=t_report,
        source_label=source,
    )
    Path(output_path).write_text(html, encoding="utf-8")
    return output_path


def visualize_comparison(
    text_a: str,
    text_b: str,
    tradition_a: str = "generic",
    tradition_b: str = "generic",
    source_a: str = "Text A",
    source_b: str = "Text B",
    output_path: str = "codex_comparison.html",
) -> str:
    """
    One-shot: run full analysis + comparison on two texts and generate dashboard.
    """
    from codex.codex_comparator import CodexComparator
    from codex.codex_filter import InstitutionalFilter
    from codex.codex_tiekat_engine import TIEKATPatternEngine

    fa = InstitutionalFilter(tradition=tradition_a)
    fb = InstitutionalFilter(tradition=tradition_b)
    ta = TIEKATPatternEngine(tradition=tradition_a)
    tb = TIEKATPatternEngine(tradition=tradition_b)

    fr_a = fa.analyze(text_a, source=source_a)
    fr_b = fb.analyze(text_b, source=source_b)
    tr_a = ta.analyze(text_a, source=source_a)
    tr_b = tb.analyze(text_b, source=source_b)

    comp_report = CodexComparator().compare(tr_a, tr_b)

    viz  = CodexVisualizer()
    html = viz.full_dashboard(
        filter_report=fr_a,
        tiekat_report=tr_a,
        comparison_report=comp_report,
        title=f"CODEX: {source_a} vs {source_b}",
        source_label=source_a,
    )
    Path(output_path).write_text(html, encoding="utf-8")
    return output_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(
        prog="codex_visualizer",
        description=(
            "CODEX Visualization Layer — generate interactive HTML dashboards\n"
            "PHI369 Labs / Parallax  ◆  C* = φ/2  ◆  ε ≠ 0"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Single text
    p1 = sub.add_parser("analyze", help="Analyze one text and generate dashboard")
    p1.add_argument("--input", "-i", required=True)
    p1.add_argument("--tradition", "-t", default="generic")
    p1.add_argument("--output", "-o", default="codex_dashboard.html")

    # Two texts comparison
    p2 = sub.add_parser("compare", help="Compare two texts and generate dashboard")
    p2.add_argument("--input-a", "-a", required=True)
    p2.add_argument("--input-b", "-b", required=True)
    p2.add_argument("--tradition-a", default="generic")
    p2.add_argument("--tradition-b", default="generic")
    p2.add_argument("--output", "-o", default="codex_comparison.html")

    args = parser.parse_args(argv)

    if args.command == "analyze":
        text = Path(args.input).read_text(encoding="utf-8")
        out  = visualize_text(text, tradition=args.tradition,
                              source=args.input, output_path=args.output)
        print(f"Dashboard written to: {out}")

    elif args.command == "compare":
        ta = Path(args.input_a).read_text(encoding="utf-8")
        tb = Path(args.input_b).read_text(encoding="utf-8")
        out = visualize_comparison(
            ta, tb,
            tradition_a=args.tradition_a, tradition_b=args.tradition_b,
            source_a=args.input_a, source_b=args.input_b,
            output_path=args.output,
        )
        print(f"Comparison dashboard written to: {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
