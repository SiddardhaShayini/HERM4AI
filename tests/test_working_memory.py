"""
Tests: tests/test_working_memory.py
Verifies bounded capacity, salience eviction, pinning, scratchpad reasoning,
and context block formatting for WorkingMemoryBuffer.
"""

import pytest
from src.herm4ai.models import Assertion
from src.herm4ai.engine import HERMMemoryEngine
from src.herm4ai.working_memory import WorkingMemoryBuffer


@pytest.fixture
def engine():
    eng = HERMMemoryEngine(":memory:")
    # Seed long term memories
    assertions = [
        Assertion("Alice", "role", "Lead", "2024-01-01T00:00:00Z", "HR"),
        Assertion("Bob", "role", "Engineer", "2024-01-01T00:00:00Z", "HR"),
        Assertion("Charlie", "role", "Architect", "2024-01-01T00:00:00Z", "HR"),
        Assertion("Diana", "role", "Director", "2024-01-01T00:00:00Z", "HR"),
    ]
    eng.ingest(assertions)
    yield eng
    eng.conn.close()


def test_working_memory_capacity_and_eviction(engine):
    wm = WorkingMemoryBuffer(engine, capacity=3)

    # Load 3 items
    wm.load("Alice", "role", initial_salience=0.9)
    wm.load("Bob", "role", initial_salience=0.3)  # Lowest salience
    wm.load("Charlie", "role", initial_salience=0.7)
    assert wm.get_slot_count() == 3

    # Load 4th item -> Bob (lowest salience) should be evicted
    wm.load("Diana", "role", initial_salience=0.8)
    assert wm.get_slot_count() == 3

    assert "Alice:role" in wm.slots
    assert "Charlie:role" in wm.slots
    assert "Diana:role" in wm.slots
    assert "Bob:role" not in wm.slots  # Evicted


def test_pinned_slots_survive_eviction(engine):
    wm = WorkingMemoryBuffer(engine, capacity=2)

    # Load Bob with low salience but PINNED
    wm.load("Bob", "role", initial_salience=0.1, pinned=True)
    wm.load("Alice", "role", initial_salience=0.9, pinned=False)
    assert wm.get_slot_count() == 2

    # Load Charlie -> Alice should be evicted because Bob is pinned
    wm.load("Charlie", "role", initial_salience=0.5, pinned=False)
    assert wm.get_slot_count() == 2
    assert "Bob:role" in wm.slots
    assert "Charlie:role" in wm.slots
    assert "Alice:role" not in wm.slots


def test_scratchpad_reasoning(engine):
    wm = WorkingMemoryBuffer(engine, capacity=5)
    wm.write_scratchpad("subgoal_1", "verify_cluster_state")
    wm.write_scratchpad("intermediate_count", 42)

    assert wm.read_scratchpad("subgoal_1") == "verify_cluster_state"
    assert wm.read_scratchpad("intermediate_count") == 42
    assert wm.read_scratchpad("nonexistent") is None


def test_context_block_formatting(engine):
    wm = WorkingMemoryBuffer(engine, capacity=5)
    wm.load("Alice", "role", initial_salience=1.0)
    wm.write_scratchpad("active_task", "incident_remediation")

    ctx = wm.format_context_block()
    assert "ACTIVE WORKING MEMORY" in ctx
    assert "Alice.role = 'Lead'" in ctx
    assert "incident_remediation" in ctx
