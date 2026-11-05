"""
Tests: tests/test_agent.py
Verifies HERMConversationalAgent: multi-session observation, working memory synchronization,
temporal state revision, tombstone expungement, and multi-hop associative queries.
"""

import pytest
from src.herm4ai.agent import HERMConversationalAgent


@pytest.fixture
def agent():
    ag = HERMConversationalAgent(":memory:", working_memory_capacity=5)
    yield ag
    ag.engine.conn.close()


def test_agent_observe_and_query(agent):
    res_obs = agent.observe_fact("User_Elena", "role", "Lead Scientist", source="Chat")
    assert res_obs["action"] == "OBSERVE_FACT"

    res_q = agent.query("User_Elena", "role")
    assert res_q["answer"] == "Lead Scientist"
    assert res_q["status"] == "ACTIVE"
    assert res_q["retrieved_from"] == "WORKING_MEMORY"


def test_agent_temporal_update_and_synchronization(agent):
    # Day 1: User reports residence in Austin
    agent.observe_fact("User_Carlos", "residence", "Austin", timestamp="2024-01-01T00:00:00Z")
    q1 = agent.query("User_Carlos", "residence")
    assert q1["answer"] == "Austin"

    # Day 30: User moves to Seattle
    agent.observe_fact("User_Carlos", "residence", "Seattle", timestamp="2024-01-30T00:00:00Z")

    # Working memory must synchronize and return Seattle, not stale Austin
    q2 = agent.query("User_Carlos", "residence")
    assert q2["answer"] == "Seattle"
    assert q2["status"] == "ACTIVE"


def test_agent_right_to_be_forgotten(agent):
    agent.observe_fact("User_Carlos", "phone", "+1-555-0100")
    assert agent.query("User_Carlos", "phone")["answer"] == "+1-555-0100"

    # Execute deletion request
    del_res = agent.request_deletion("User_Carlos", "phone")
    assert del_res["action"] == "DELETE_TOMBSTONE"

    # Querying after deletion should return DELETED and never leak the phone number
    q_post = agent.query("User_Carlos", "phone")
    assert q_post["answer"] == "DELETED"
    assert q_post["status"] == "DELETED"


def test_agent_multi_hop_query(agent):
    agent.observe_relation("Project_Alpha", "USES_DB", "DB_Cluster_1", weight=1.0)
    agent.observe_relation("DB_Cluster_1", "HOSTED_ON", "Physical_Rack_4", weight=0.9)

    res = agent.multi_hop_query("Project_Alpha", "Physical_Rack_4", max_hops=3)
    assert res["is_reachable"] is True
    assert res["association_score"] > 0.0

    res_unreach = agent.multi_hop_query("Project_Alpha", "Unrelated_Node", max_hops=3)
    assert res_unreach["is_reachable"] is False


def test_agent_session_lifecycle(agent):
    agent.observe_fact("User_Elena", "tool", "Docker")
    agent.end_session("session_001", elapsed_days=5.0)

    assert len(agent.session_history) == 1
    assert agent.session_history[0]["session_id"] == "session_001"
