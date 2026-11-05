"""
Tests: tests/test_associative_memory.py
Verifies associative memory graphs, procedural routines, access strengthening,
consolidation tiers, and cognitive decay.
"""

import pytest
from src.herm4ai.models import Assertion, MemoryStatus, ConsolidationTier, EventType
from src.herm4ai.engine import HERMMemoryEngine


@pytest.fixture
def engine():
    eng = HERMMemoryEngine(":memory:")
    yield eng
    eng.conn.close()


def test_associative_linking_and_retrieval(engine):
    edge = engine.relate(
        source_entity="Dr. Aris Thorne",
        relation="LEADS_PROJECT",
        target_entity="Project-Vanguard",
        weight=0.9,
        source="Admin_Registry"
    )
    assert edge.source_entity == "Dr. Aris Thorne"
    assert edge.target_entity == "Project-Vanguard"
    assert edge.weight == 0.9

    assocs = engine.get_associations("Dr. Aris Thorne")
    assert len(assocs) == 1
    assert assocs[0].relation == "LEADS_PROJECT"


def test_spreading_activation(engine):
    # Setup chain: Aris --[LEADS]--> Vanguard --[DEPENDS_ON]--> Auth-Service
    engine.relate("Dr. Aris Thorne", "LEADS", "Project-Vanguard", weight=1.0)
    engine.relate("Project-Vanguard", "DEPENDS_ON", "Auth-Service", weight=0.8)

    scores = engine.associative_spread("Dr. Aris Thorne", max_hops=2, decay_factor=0.5)
    assert "Dr. Aris Thorne" in scores
    assert scores["Dr. Aris Thorne"] == 1.0
    assert "Project-Vanguard" in scores
    assert scores["Project-Vanguard"] == 0.5  # 1.0 * 1.0 * 0.5
    assert "Auth-Service" in scores
    assert scores["Auth-Service"] == 0.2  # 0.5 * 0.8 * 0.5


def test_impact_analysis(engine):
    engine.relate("Server-Alpha", "HOSTS", "Database-Cluster-9")
    engine.relate("Server-Alpha", "HOSTS", "Auth-Service")

    impact = engine.impact_analysis("Server-Alpha")
    assert impact["source_entity"] == "Server-Alpha"
    assert impact["dependency_count"] == 2
    entities = [d["entity"] for d in impact["dependencies"]]
    assert "Database-Cluster-9" in entities
    assert "Auth-Service" in entities


def test_procedural_memory_registration_and_retrieval(engine):
    routine = engine.register_routine(
        task_type="failover_recovery",
        trigger_pattern="server_offline_telemetry",
        action_steps=[
            "1. Isolate degraded node",
            "2. Reroute traffic to secondary cluster",
            "3. Notify infrastructure team"
        ],
        preconditions="Secondary cluster active"
    )
    assert routine.task_type == "failover_recovery"

    # Retrieve by trigger keyword
    retrieved = engine.retrieve_routine("server_offline")
    assert retrieved is not None
    assert retrieved.routine_id == routine.routine_id
    assert len(retrieved.action_steps) == 3
    assert retrieved.usage_count == 1


def test_access_strengthening_and_consolidation(engine):
    a = Assertion(
        entity="Marcus Vance",
        attribute="clearance",
        value="Level-3",
        timestamp="2024-01-01T00:00:00Z",
        source="Security_Admin"
    )
    engine.ingest([a])

    # Query 1
    res1 = engine.query("Marcus Vance", "clearance", "Query", "2024-01-02T00:00:00Z")
    assert res1.consolidation_tier == ConsolidationTier.EPISODIC.value

    # Query 2
    res2 = engine.query("Marcus Vance", "clearance", "Query", "2024-01-03T00:00:00Z")
    assert res2.consolidation_tier == ConsolidationTier.EPISODIC.value

    # Query 3 -> Should trigger consolidation to CONSOLIDATED_SEMANTIC
    res3 = engine.query("Marcus Vance", "clearance", "Query", "2024-01-04T00:00:00Z")
    assert res3.consolidation_tier == ConsolidationTier.CONSOLIDATED_SEMANTIC.value
    prov_events = [p.event_type for p in res3.provenance]
    assert EventType.CONSOLIDATE in prov_events


def test_temporal_decay_and_archival(engine):
    a = Assertion(
        entity="OldDevice-404",
        attribute="calibration_val",
        value="0.9942",
        timestamp="2024-01-01T00:00:00Z",
        source="Sensor"
    )
    engine.ingest([a])

    # Simulate 90 days of dormancy without queries
    report = engine.apply_temporal_decay("2024-04-01T00:00:00Z", archive_threshold=0.20)
    assert report["memories_archived"] == 1

    # Querying the dormant record should now reflect ARCHIVED status
    res = engine.query("OldDevice-404", "calibration_val", "Query", "2024-04-02T00:00:00Z")
    assert res.status == MemoryStatus.ARCHIVED
    assert res.value == "0.9942"
