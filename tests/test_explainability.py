"""
Tests: tests/test_explainability.py
Verifies ExplainabilityAuditEngine: counterfactual memory influence,
causal necessity scoring, suppression tracking, and explainability report generation.
"""

import pytest
from src.herm4ai.models import Assertion
from src.herm4ai.engine import HERMMemoryEngine
from src.herm4ai.explainability import ExplainabilityAuditEngine


@pytest.fixture
def engine():
    eng = HERMMemoryEngine(":memory:")
    yield eng
    eng.conn.close()


def test_causal_necessity_direct_recall(engine):
    a = Assertion("Alice", "role", "Architect", "2024-01-01T00:00:00Z", "HR")
    engine.ingest([a])

    auditor = ExplainabilityAuditEngine(engine)
    report = auditor.audit_query("Alice", "role", "2024-01-02T00:00:00Z")

    assert report.produced_answer == "Architect"
    assert report.lifecycle_status == "ACTIVE"
    assert len(report.contributing_memories) == 1

    attr = report.contributing_memories[0]
    assert attr.value == "Architect"
    assert attr.is_causal_necessity is True
    assert attr.counterfactual_influence == 1.0
    assert "Withholding" in report.counterfactual_summary


def test_temporal_revision_attribution(engine):
    a1 = Assertion("Bob", "city", "London", "2024-01-01T00:00:00Z", "HR")
    a2 = Assertion("Bob", "city", "Tokyo", "2024-06-01T00:00:00Z", "HR")
    engine.ingest([a1, a2])

    auditor = ExplainabilityAuditEngine(engine)
    report = auditor.audit_query("Bob", "city", "2024-07-01T00:00:00Z")

    assert report.produced_answer == "Tokyo"
    assert "London" in report.revised_memories
    assert len(report.suppressed_memories) >= 1

    # Active memory for Tokyo should have causal influence 1.0
    tokyo_attr = next(m for m in report.contributing_memories if m.value == "Tokyo")
    assert tokyo_attr.is_causal_necessity is True
    assert tokyo_attr.counterfactual_influence == 1.0


def test_conflict_attribution(engine):
    a1 = Assertion("Server-Alpha", "state", "ONLINE", "2024-03-01T10:00:00Z", "Sensor_A")
    a2 = Assertion("Server-Alpha", "state", "OFFLINE", "2024-03-01T10:05:00Z", "Sensor_B")
    engine.ingest([a1, a2])

    auditor = ExplainabilityAuditEngine(engine)
    report = auditor.audit_query("Server-Alpha", "state", "2024-03-02T00:00:00Z")

    assert report.lifecycle_status == "CONFLICTED"
    assert "ONLINE" in report.conflicted_memories
    assert "OFFLINE" in report.conflicted_memories
    assert "Sensor_A" in report.originating_sources
    assert "Sensor_B" in report.originating_sources


def test_format_text_report(engine):
    a = Assertion("Charlie", "clearance", "Top-Secret", "2024-01-01T00:00:00Z", "Admin")
    engine.ingest([a])

    auditor = ExplainabilityAuditEngine(engine)
    report = auditor.audit_query("Charlie", "clearance")
    text_out = report.format_text_report()

    assert "HERM4AI EXPLAINABILITY & COGNITIVE OBSERVATION REPORT" in text_out
    assert "KNOWLEDGE ORIGIN & PROVENANCE" in text_out
    assert "COUNTERFACTUAL INFLUENCE" in text_out
    assert "SCIENTIFIC DISCLAIMER" in text_out
