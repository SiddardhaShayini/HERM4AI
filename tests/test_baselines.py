"""
Tests: tests/test_baselines.py
Verifies baseline behaviors.
"""

from src.herm4ai.models import Assertion, MemoryStatus
from src.herm4ai.baselines import StatelessBaseline, NaiveRetrievalBaseline


def test_stateless_baseline():
    base = StatelessBaseline()
    a = Assertion(
        entity="Bob",
        attribute="team",
        value="Alpha",
        timestamp="2024-01-01T00:00:00Z",
        source="HR"
    )
    base.ingest([a])
    res = base.query("Bob", "team", "What team is Bob on?", "2024-01-02T00:00:00Z")
    assert res.value == "UNKNOWN"
    assert res.status == MemoryStatus.UNKNOWN


def test_naive_retrieval_temporal_failure():
    # Demonstrates that naive retrieval fails to prefer newer facts when older ones exist
    base = NaiveRetrievalBaseline()
    a1 = Assertion(
        entity="Bob",
        attribute="team",
        value="Alpha",
        timestamp="2024-01-01T00:00:00Z",
        source="HR"
    )
    a2 = Assertion(
        entity="Bob",
        attribute="team",
        value="Beta",
        timestamp="2024-06-01T00:00:00Z",
        source="HR"
    )
    base.ingest([a1, a2])
    res = base.query("Bob", "team", "What team is Bob on?", "2024-07-01T00:00:00Z")
    # Naive retrieval typically picks the first matching document ("Alpha")
    assert res.value == "Alpha"
