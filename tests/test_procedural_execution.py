"""
Module: tests/test_procedural_execution.py
Unit tests for Procedural Memory Workflow Execution Engine (Phase 13).
"""

import pytest
from src.herm4ai.models import Assertion, MemoryStatus
from src.herm4ai.engine import HERMMemoryEngine
from src.herm4ai.working_memory import WorkingMemoryBuffer
from src.herm4ai.procedural import ProceduralExecutionEngine
from src.herm4ai.agent import HERMConversationalAgent


@pytest.fixture
def memory_setup():
    engine = HERMMemoryEngine(":memory:")
    wm = WorkingMemoryBuffer(engine, capacity=5)
    proc_engine = ProceduralExecutionEngine(engine, wm)
    yield engine, wm, proc_engine
    engine.conn.close()


def test_procedural_conflict_resolution_workflow(memory_setup):
    engine, wm, proc_engine = memory_setup

    # Register conflict resolution routine
    routine = engine.register_routine(
        task_type="CONFLICT_RESOLUTION",
        trigger_pattern="contradiction|conflict|dispute",
        action_steps=[
            "CHECK_PRECONDITION",
            "RESOLVE_CONFLICT_BY_TIMESTAMP",
            "UPDATE_WORKING_MEMORY",
            "LOG_AUDIT_PROVENANCE"
        ]
    )

    # Ingest 2 conflicting assertions within 24h
    engine.ingest([
        Assertion("Server_Primary", "gateway", "192.168.1.1", "2026-01-01T10:00:00", "Sensor_A"),
        Assertion("Server_Primary", "gateway", "192.168.1.254", "2026-01-01T11:00:00", "Sensor_B"),
    ])

    # Check that status is CONFLICTED
    q_res = engine.query("Server_Primary", "gateway", "gateway?", "2026-01-01T12:00:00")
    assert q_res.status == MemoryStatus.CONFLICTED

    # Execute routine
    exec_res = proc_engine.execute_routine(
        routine,
        context={"entity": "Server_Primary", "attribute": "gateway", "expected_status": "CONFLICTED"}
    )

    assert exec_res["overall_success"] is True
    assert exec_res["steps_executed"] == 4
    assert exec_res["context_state"]["resolved_value"] == "192.168.1.254"  # latest timestamp
    assert exec_res["usage_count"] == 1
    assert exec_res["updated_success_rate"] == 1.0

    # Verify that memory is now resolved to ACTIVE
    q_resolved = engine.query("Server_Primary", "gateway", "gateway?", "2026-01-01T13:00:00")
    assert q_resolved.status == MemoryStatus.ACTIVE
    assert q_resolved.value == "192.168.1.254"


def test_procedural_confidence_resolution(memory_setup):
    engine, wm, proc_engine = memory_setup

    routine = engine.register_routine(
        task_type="CONFIDENCE_RESOLUTION",
        trigger_pattern="confidence",
        action_steps=[
            "RESOLVE_CONFLICT_BY_CONFIDENCE",
            "LOG_AUDIT_PROVENANCE"
        ]
    )

    # Ingest conflicting assertions with different confidence
    engine.ingest([
        Assertion("Model_Alpha", "version", "v1.0", "2026-01-01T10:00:00", "Source_Low", confidence=0.7),
        Assertion("Model_Alpha", "version", "v2.0", "2026-01-01T11:00:00", "Source_High", confidence=0.98),
    ])

    res = proc_engine.execute_routine(
        routine,
        context={"entity": "Model_Alpha", "attribute": "version"}
    )

    assert res["overall_success"] is True
    assert res["context_state"]["resolved_value"] == "v2.0"

    q_resolved = engine.query("Model_Alpha", "version", "version?", "2026-01-01T12:00:00")
    assert q_resolved.status == MemoryStatus.ACTIVE
    assert q_resolved.value == "v2.0"


def test_procedural_reinforcement_on_failure(memory_setup):
    engine, wm, proc_engine = memory_setup

    # Register routine with a failing step
    routine = engine.register_routine(
        task_type="FAILING_TASK",
        trigger_pattern="fail",
        action_steps=["NON_EXISTENT_STEP"]
    )

    initial_rate = routine.success_rate
    res = proc_engine.execute_routine(routine, context={})

    assert res["overall_success"] is False
    assert res["updated_success_rate"] < initial_rate
    assert res["usage_count"] == 1


def test_agent_automated_procedural_integration():
    agent = HERMConversationalAgent(":memory:")

    # Agent learns a conflict resolution procedure
    agent.learn_procedure(
        task_type="CONFLICT_RESOLUTION",
        trigger_pattern="conflict|contradiction",
        action_steps=[
            "RESOLVE_CONFLICT_BY_TIMESTAMP",
            "UPDATE_WORKING_MEMORY",
            "LOG_AUDIT_PROVENANCE"
        ]
    )

    # Ingest 2 conflicting assertions
    agent.engine.ingest([
        Assertion("Device_99", "ip", "172.16.0.1", "2026-01-01T00:00:00", "DHCP_Old"),
        Assertion("Device_99", "ip", "172.16.0.254", "2026-01-01T01:00:00", "DHCP_New"),
    ])

    # Query agent: agent should detect conflict, trigger procedural workflow, and resolve it
    answer = agent.query("Device_99", "ip", "What is IP?", "2026-01-01T02:00:00")

    assert answer["status"] == "ACTIVE"
    assert answer["answer"] == "172.16.0.254"
    assert answer["retrieved_from"] == "PROCEDURAL_CONFLICT_RESOLUTION"
