"""Tests for the TIEKAT pattern analysis stack."""

from codex.codex_comparator import CodexComparator, compare_texts
from codex.codex_filter import InstitutionalFilter
from codex.codex_tiekat_engine import TIEKATPatternEngine, analyze_text
from codex.codex_visualizer import CodexVisualizer

THOMAS_SAMPLE = (
    "Jesus said: The kingdom of God is within you and all around you. "
    "If you bring forth what is within you what you bring forth will save you. "
    "I am the light that is over all things. I am the All."
)

HERMETIC_SAMPLE = (
    "The All is Mind. As above so below. Know thyself and thou shalt know the universe. "
    "Freedom is the birthright of every soul. The spirit is living through all things."
)


def test_tiekat_engine_returns_report():
    engine = TIEKATPatternEngine(tradition="thomas")
    report = engine.analyze(THOMAS_SAMPLE, source="test")
    assert report.word_count > 0
    assert report.tradition == "Gospel of Thomas"


def test_tiekat_engine_detects_epsilon_signal():
    engine = TIEKATPatternEngine(tradition="thomas")
    report = engine.analyze(THOMAS_SAMPLE, source="test")
    from codex.codex_tiekat_engine import PatternType

    epsilon_matches = [m for m in report.matches if m.pattern_type == PatternType.EPSILON_SIGNAL]
    assert len(epsilon_matches) > 0


def test_filter_returns_report():
    engine = InstitutionalFilter(tradition="thomas")
    report = engine.analyze(THOMAS_SAMPLE, source="test")
    assert report.passage_count > 0
    assert 0.0 <= report.overall_coherence <= 1.0


def test_filter_detects_fear_framing():
    fear_text = (
        "Fear him who can cast both soul and body into hell. "
        "The condemned will face eternal punishment."
    )
    engine = InstitutionalFilter(tradition="generic")
    report = engine.analyze(fear_text, source="test")
    from codex.codex_filter import LayerType

    fear_hits = report.layer_totals.get(LayerType.FEAR_FRAMING.value, 0)
    assert fear_hits > 0


def test_comparator_returns_report():
    engine_t = TIEKATPatternEngine(tradition="thomas")
    engine_h = TIEKATPatternEngine(tradition="hermetic")
    report_t = engine_t.analyze(THOMAS_SAMPLE, source="Thomas")
    report_h = engine_h.analyze(HERMETIC_SAMPLE, source="Hermetic")
    comp = CodexComparator().compare(report_t, report_h)
    assert 0.0 <= comp.convergence_index <= 1.0
    assert comp.tradition_a == "Gospel of Thomas"
    assert comp.tradition_b == "Hermetic Corpus"


def test_visualizer_generates_html():
    engine = TIEKATPatternEngine(tradition="thomas")
    filter_eng = InstitutionalFilter(tradition="thomas")
    t_report = engine.analyze(THOMAS_SAMPLE, source="test")
    f_report = filter_eng.analyze(THOMAS_SAMPLE, source="test")
    viz = CodexVisualizer()
    html = viz.full_dashboard(filter_report=f_report, tiekat_report=t_report)
    assert "<html" in html
    assert "CODEX" in html
    assert "Φ∴⊙" in html


def test_analyze_text_convenience():
    result = analyze_text(THOMAS_SAMPLE, tradition="thomas", output_format="text")
    assert len(result) > 0


def test_compare_texts_convenience():
    result = compare_texts(
        THOMAS_SAMPLE,
        HERMETIC_SAMPLE,
        tradition_a="thomas",
        tradition_b="hermetic",
        output_format="text",
    )
    assert len(result) > 0
