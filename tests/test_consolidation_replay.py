"""
Module: tests/test_consolidation_replay.py
Unit tests for offline sleep replay and memory consolidation engine.
"""

import pytest
import sqlite3
from src.herm4ai.models import Assertion, MemoryStatus, ConsolidationTier, EventType
from src.herm4ai.engine import HERMMemoryEngine
from src.herm4ai.consolidation import MemoryConsolidationEngine


@pytest.fixture
def memory_engine():
    engine = HERMMemoryEngine(":memory:")
    yield engine
    engine.conn.close()


def test_episodic_to_semantic_promotion(memory_engine):
    consolidation = MemoryConsolidationEngine(memory_engine)

    # Ingest assertion
    memory_engine.ingest([
        Assertion("User_Alpha", "role", "Lead Architect", "2026-01-01T10:00:00", "source_hr")
    ])

    # Initial state should be EPISODIC
    rec = memory_engine.query("User_Alpha", "role", "role?", "2026-01-02T10:00:00")
    assert rec.consolidation_tier == ConsolidationTier.EPISODIC.value

    # Query a second time (access_count becomes 2, still EPISODIC because engine threshold is 3)
    rec2 = memory_engine.query("User_Alpha", "role", "role?", "2026-01-03T10:00:00")
    assert rec2.consolidation_tier == ConsolidationTier.EPISODIC.value

    # Run sleep replay cycle with min_accesses_for_semantic=2
    result = consolidation.simulate_sleep_cycle(
        cycle_timestamp_iso="2026-01-05T02:00:00",
        min_accesses_for_semantic=2,
        min_activation_for_semantic=0.5
    )

    assert result["promoted_to_semantic_count"] >= 1

    # Check updated record
    updated_rec = memory_engine.query("User_Alpha", "role", "role?", "2026-01-05T10:00:00")
    assert updated_rec.consolidation_tier == ConsolidationTier.CONSOLIDATED_SEMANTIC.value


def test_superseded_history_archiving(memory_engine):
    consolidation = MemoryConsolidationEngine(memory_engine)

    # Ingest initial state and later update
    memory_engine.ingest([
        Assertion("Server_01", "ip", "10.0.0.1", "2026-01-01T00:00:00", "net_scan"),
        Assertion("Server_01", "ip", "10.0.0.2", "2026-01-10T00:00:00", "net_scan"),
    ])

    # The first record is now SUPERSEDED with valid_to = 2026-01-10T00:00:00
    # Simulate sleep cycle 40 days later (2026-02-25)
    result = consolidation.simulate_sleep_cycle(
        cycle_timestamp_iso="2026-02-25T03:00:00",
        prune_superseded_older_than_days=30.0
    )

    assert result["superseded_archived_count"] == 1

    # Check database status of old record
    cursor = memory_engine.conn.cursor()
    cursor.execute("SELECT status, consolidation_tier FROM memories WHERE value = '10.0.0.1'")
    row = cursor.fetchone()
    assert row["status"] == "ARCHIVED"
    assert row["consolidation_tier"] == "ARCHIVED"


def test_synaptic_plasticity_and_pruning(memory_engine):
    consolidation = MemoryConsolidationEngine(memory_engine)

    # Ingest entities and access them
    memory_engine.ingest([
        Assertion("Alice", "dept", "Security", "2026-01-01T00:00:00", "hr"),
        Assertion("Bob", "dept", "Security", "2026-01-01T00:00:00", "hr"),
    ])
    # Create associative edge using relate()
    memory_engine.relate("Alice", "collaborates_with", "Bob", weight=0.6)
    # Create dormant weak edge
    memory_engine.relate("Alice", "visited_location", "Old_Office", weight=0.04)

    # Access both Alice and Bob to trigger co-activation
    memory_engine.query("Alice", "dept", "dept?", "2026-01-01T12:00:00")
    memory_engine.query("Bob", "dept", "dept?", "2026-01-01T12:00:00")

    # Run sleep cycle
    res = consolidation.simulate_sleep_cycle(
        cycle_timestamp_iso="2026-01-02T04:00:00",
        edge_strengthen_factor=0.15,
        edge_prune_threshold=0.05
    )

    assert res["edges_strengthened_count"] >= 1
    assert res["edges_pruned_count"] >= 1

    # Check strengthened edge
    edges = memory_engine.get_associations("Alice", "collaborates_with")
    assert len(edges) == 1
    assert edges[0].weight == 0.75  # 0.6 + 0.15

    # Check pruned edge
    dormant_edges = memory_engine.get_associations("Alice", "visited_location")
    assert len(dormant_edges) == 0  # pruned/archived


def test_conflict_triage_in_sleep_cycle(memory_engine):
    consolidation = MemoryConsolidationEngine(memory_engine)

    # Ingest conflicting assertions within 24h from different sources
    memory_engine.ingest([
        Assertion("Device_X", "firmware", "v1.0", "2026-01-01T10:00:00", "source_A"),
        Assertion("Device_X", "firmware", "v1.1", "2026-01-01T12:00:00", "source_B"),
    ])

    res = consolidation.simulate_sleep_cycle(cycle_timestamp_iso="2026-01-02T02:00:00")
    assert res["unresolved_conflicts_flagged"] >= 1
    assert res["unresolved_conflicts"][0]["entity"] == "Device_X"
