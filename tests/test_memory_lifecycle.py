"""
Tests: tests/test_memory_lifecycle.py
Verifies the core deterministic lifecycle transitions of HERMMemoryEngine.
"""

import pytest
from src.herm4ai.models import Assertion, MemoryStatus, EventType
from src.herm4ai.engine import HERMMemoryEngine


@pytest.fixture
def engine():
    eng = HERMMemoryEngine(":memory:")
    yield eng
    eng.conn.close()


def test_initial_encoding(engine):
    assertion = Assertion(
        entity="Agent-Zero",
        attribute="role",
        value="Orchestrator",
        timestamp="2024-01-01T00:00:00Z",
        source="System_Init"
    )
    engine.ingest([assertion])

    res = engine.query("Agent-Zero", "role", "What is the role?", "2024-01-02T00:00:00Z")
    assert res.value == "Orchestrator"
    assert res.status == MemoryStatus.ACTIVE
    assert len(res.provenance) >= 1
    assert res.provenance[0].event_type == EventType.ENCODE


def test_temporal_revision_superseding(engine):
    # Step 1: Initial state
    a1 = Assertion(
        entity="Alice",
        attribute="city",
        value="London",
        timestamp="2024-01-01T00:00:00Z",
        source="HR_Registry"
    )
    # Step 2: Temporal update
    a2 = Assertion(
        entity="Alice",
        attribute="city",
        value="Tokyo",
        timestamp="2024-06-01T00:00:00Z",
        source="HR_Registry"
    )
    engine.ingest([a1, a2])

    res = engine.query("Alice", "city", "Where is Alice?", "2024-07-01T00:00:00Z")
    assert res.value == "Tokyo"
    assert res.status == MemoryStatus.ACTIVE
    assert res.superseded_values == ["London"]
    # Check that provenance records both encode and update
    events = [p.event_type for p in res.provenance]
    assert EventType.ENCODE in events
    assert EventType.UPDATE in events


def test_conflict_detection(engine):
    # Simultaneous divergent assertions from conflicting sources
    a1 = Assertion(
        entity="Server-Alpha",
        attribute="power_state",
        value="ONLINE",
        timestamp="2024-03-01T12:00:00Z",
        source="Telemetry_Feed_A"
    )
    a2 = Assertion(
        entity="Server-Alpha",
        attribute="power_state",
        value="OFFLINE",
        timestamp="2024-03-01T12:00:00Z",
        source="Telemetry_Feed_B"
    )
    engine.ingest([a1, a2])

    res = engine.query("Server-Alpha", "power_state", "What is the power state?", "2024-03-02T00:00:00Z")
    assert res.status == MemoryStatus.CONFLICTED
    assert res.value == "CONFLICTED"
    assert set(res.conflicting_values) == {"ONLINE", "OFFLINE"}
    events = [p.event_type for p in res.provenance]
    assert EventType.CONFLICT in events


def test_tombstone_deletion(engine):
    a1 = Assertion(
        entity="User-99",
        attribute="phone_number",
        value="+1-555-0199",
        timestamp="2024-01-01T00:00:00Z",
        source="User_Profile"
    )
    a_del = Assertion(
        entity="User-99",
        attribute="phone_number",
        value=None,
        timestamp="2024-02-01T00:00:00Z",
        source="Privacy_Purge_Service",
        is_deletion=True
    )
    engine.ingest([a1, a_del])

    res = engine.query("User-99", "phone_number", "Get phone number", "2024-03-01T00:00:00Z")
    assert res.status == MemoryStatus.DELETED
    assert res.value == "DELETED"
    events = [p.event_type for p in res.provenance]
    assert EventType.DELETE in events


def test_out_of_domain_abstention(engine):
    res = engine.query("UnknownEntity", "unknown_attr", "Query?", "2024-01-01T00:00:00Z")
    assert res.status == MemoryStatus.UNKNOWN
    assert res.value == "UNKNOWN"


def test_observability_rendering(engine):
    from src.herm4ai.observability import render_provenance_timeline
    a1 = Assertion(
        entity="ObservabilityTarget",
        attribute="tier",
        value="Alpha",
        timestamp="2024-01-01T00:00:00Z",
        source="System_A"
    )
    a2 = Assertion(
        entity="ObservabilityTarget",
        attribute="tier",
        value="Beta",
        timestamp="2024-06-01T00:00:00Z",
        source="System_A"
    )
    engine.ingest([a1, a2])
    res = engine.query("ObservabilityTarget", "tier", "Query tier", "2024-07-01T00:00:00Z")
    timeline = render_provenance_timeline(res)
    assert "HERM4AI OBSERVABILITY & PROVENANCE REPORT" in timeline
    assert "ENCODE" in timeline
    assert "UPDATE" in timeline
    assert "Superseded Historical Values" in timeline
