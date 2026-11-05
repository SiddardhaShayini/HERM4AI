"""
Module: src/herm4ai/agent.py
Implementation of HERMConversationalAgent.
Integrates HERMMemoryEngine (long-term semantic & associative memory)
with WorkingMemoryBuffer (bounded 7-slot working memory) for persistent multi-session dialogue.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from .engine import HERMMemoryEngine
from .working_memory import WorkingMemoryBuffer
from .procedural import ProceduralExecutionEngine
from .models import Assertion, QueryResult, MemoryStatus, EventType, ProceduralRoutine


class HERMConversationalAgent:
    """
    A persistent, observable, multi-session conversational agent powered by HERM4AI.
    Combines long-term structured lifecycle memory, associative knowledge graphs,
    bounded working memory buffers, and verifiable provenance tracking.
    """
    def __init__(self, db_path: str = ":memory:", working_memory_capacity: int = 7):
        self.engine = HERMMemoryEngine(db_path)
        self.working_memory = WorkingMemoryBuffer(self.engine, capacity=working_memory_capacity)
        self.procedural_engine = ProceduralExecutionEngine(self.engine, self.working_memory)
        self.session_history: List[Dict[str, Any]] = []

    def observe_fact(
        self,
        entity: str,
        attribute: str,
        value: str,
        timestamp: Optional[str] = None,
        source: str = "User_Conversation"
    ) -> Dict[str, Any]:
        """
        Observes a factual assertion in dialogue and commits it to memory.
        """
        now_iso = timestamp or datetime.now().isoformat()
        assertion = Assertion(
            entity=entity,
            attribute=attribute,
            value=value,
            timestamp=now_iso,
            source=source,
            confidence=1.0,
            is_deletion=False
        )
        self.engine.ingest([assertion])
        # Load into working memory
        slot = self.working_memory.load(entity, attribute, query_time=now_iso, initial_salience=1.0)
        return {
            "action": "OBSERVE_FACT",
            "entity": entity,
            "attribute": attribute,
            "value": value,
            "timestamp": now_iso,
            "working_memory_slot": slot.slot_id if slot else None
        }

    def observe_relation(
        self,
        source_entity: str,
        relation: str,
        target_entity: str,
        weight: float = 1.0,
        timestamp: Optional[str] = None,
        source: str = "User_Conversation"
    ) -> Dict[str, Any]:
        """
        Observes an associative relationship between entities.
        """
        edge = self.engine.relate(
            source_entity=source_entity,
            relation=relation,
            target_entity=target_entity,
            weight=weight,
            source=source,
            timestamp=timestamp
        )
        return {
            "action": "OBSERVE_RELATION",
            "edge_id": edge.id,
            "source_entity": source_entity,
            "relation": relation,
            "target_entity": target_entity,
            "weight": weight
        }

    def request_deletion(
        self,
        entity: str,
        attribute: str,
        timestamp: Optional[str] = None,
        source: str = "User_Purge_Request"
    ) -> Dict[str, Any]:
        """
        Handles an explicit right-to-be-forgotten / deletion request.
        Purges the value, evicts from working memory, and logs an auditable tombstone.
        """
        now_iso = timestamp or datetime.now().isoformat()
        assertion = Assertion(
            entity=entity,
            attribute=attribute,
            value=None,
            timestamp=now_iso,
            source=source,
            is_deletion=True
        )
        self.engine.ingest([assertion])
        # Evict from working memory if present
        slot_key = f"{entity}:{attribute}"
        if slot_key in self.working_memory.slots:
            del self.working_memory.slots[slot_key]

        return {
            "action": "DELETE_TOMBSTONE",
            "entity": entity,
            "attribute": attribute,
            "status": "DELETED",
            "timestamp": now_iso
        }

    def query(
        self,
        entity: str,
        attribute: str,
        query_text: str = "",
        query_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answers a user query using working memory first, falling back to long-term memory.
        Returns the answer, cognitive status, and complete provenance audit trail.
        """
        now_iso = query_time or datetime.now().isoformat()
        slot_key = f"{entity}:{attribute}"

        # 1. Check active working memory
        if slot_key in self.working_memory.slots:
            slot = self.working_memory.slots[slot_key]
            self.working_memory.touch(entity, attribute)
            return {
                "answer": slot.value,
                "status": "ACTIVE",
                "retrieved_from": "WORKING_MEMORY",
                "salience": slot.salience,
                "provenance": [],
                "explanation": f"Retrieved directly from active working memory slot {slot.slot_id}."
            }

        # 2. Query Long-Term Memory Engine
        res: QueryResult = self.engine.query(entity, attribute, query_text, now_iso)

        if res.status == MemoryStatus.UNKNOWN:
            return {
                "answer": "UNKNOWN",
                "status": "UNKNOWN",
                "retrieved_from": "LONG_TERM_MEMORY",
                "provenance": [p.to_dict() for p in res.provenance],
                "explanation": f"No memory record exists for {entity}.{attribute}. Cleanly abstaining."
            }

        if res.status == MemoryStatus.DELETED:
            return {
                "answer": "DELETED",
                "status": "DELETED",
                "retrieved_from": "LONG_TERM_MEMORY",
                "provenance": [p.to_dict() for p in res.provenance],
                "explanation": f"The record for {entity}.{attribute} was explicitly expunged under a tombstone purge request."
            }

        if res.status == MemoryStatus.CONFLICTED:
            # Check if procedural memory has an automated conflict resolution routine
            proc_res = self.procedural_engine.match_and_execute(
                "CONFLICT_RESOLUTION",
                context={"entity": entity, "attribute": attribute}
            )
            if proc_res and proc_res["overall_success"] and "resolved_value" in proc_res["context_state"]:
                resolved_val = proc_res["context_state"]["resolved_value"]
                # Update working memory
                self.working_memory.load(entity, attribute, query_time=now_iso, initial_salience=1.0)
                return {
                    "answer": resolved_val,
                    "status": "ACTIVE",
                    "retrieved_from": "PROCEDURAL_CONFLICT_RESOLUTION",
                    "resolved_by_routine": proc_res["routine_id"],
                    "provenance": [p.to_dict() for p in res.provenance],
                    "explanation": f"Conflict automatically resolved by procedural routine '{proc_res['routine_id']}': selected '{resolved_val}'."
                }

            return {
                "answer": "CONFLICTED",
                "status": "CONFLICTED",
                "conflicting_values": res.conflicting_values,
                "retrieved_from": "LONG_TERM_MEMORY",
                "provenance": [p.to_dict() for p in res.provenance],
                "explanation": f"Conflicting information detected from multiple sources: {res.conflicting_values}."
            }

        if res.status == MemoryStatus.ARCHIVED:
            return {
                "answer": res.value,
                "status": "ARCHIVED",
                "activation_strength": res.activation_strength,
                "retrieved_from": "ARCHIVAL_COLD_STORAGE",
                "provenance": [p.to_dict() for p in res.provenance],
                "explanation": f"Retrieved from cold archive; activation decayed to {res.activation_strength:.2f}."
            }

        # Status == ACTIVE -> promote into working memory
        self.working_memory.load(entity, attribute, query_time=now_iso, initial_salience=1.0)

        # Include 1-hop associative context
        associative_summary = []
        if res.associative_context:
            for edge in res.associative_context:
                target = edge["target_entity"] if edge["source_entity"] == entity else edge["source_entity"]
                associative_summary.append(f"{edge['relation']} -> {target}")

        return {
            "answer": res.value,
            "status": "ACTIVE",
            "superseded_history": res.superseded_values,
            "retrieved_from": "LONG_TERM_MEMORY",
            "consolidation_tier": res.consolidation_tier,
            "associative_links": associative_summary,
            "provenance": [p.to_dict() for p in res.provenance],
            "explanation": f"Verified current value: '{res.value}'. Superseded values: {res.superseded_values}."
        }

    def multi_hop_query(
        self,
        start_entity: str,
        target_entity: str,
        max_hops: int = 3
    ) -> Dict[str, Any]:
        """
        Executes spreading activation associative path query between two entities.
        """
        scores = self.engine.associative_spread(start_entity, max_hops=max_hops)
        is_reachable = target_entity in scores
        score = scores.get(target_entity, 0.0)

        return {
            "start_entity": start_entity,
            "target_entity": target_entity,
            "is_reachable": is_reachable,
            "association_score": round(score, 4),
            "network_size_evaluated": len(scores)
        }

    def end_session(self, session_id: str, elapsed_days: float = 0.0):
        """
        Ends current conversational session: applies working memory decay and logs session closure.
        """
        if elapsed_days > 0.0:
            future_iso = datetime.now().isoformat()
            self.engine.apply_temporal_decay(future_iso)
            self.working_memory.decay_working_memory(decay_rate=0.2 * elapsed_days)

        self.session_history.append({
            "session_id": session_id,
            "ended_at": datetime.now().isoformat(),
            "active_working_slots": len(self.working_memory.slots)
        })

    def learn_procedure(
        self,
        task_type: str,
        trigger_pattern: str,
        action_steps: List[str],
        preconditions: Optional[str] = None
    ) -> ProceduralRoutine:
        """
        Stores a new procedural routine into procedural memory.
        """
        return self.engine.register_routine(
            task_type=task_type,
            trigger_pattern=trigger_pattern,
            action_steps=action_steps,
            preconditions=preconditions
        )

    def execute_procedure(
        self,
        task_or_trigger: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves matching procedural routine and executes it via ProceduralExecutionEngine.
        """
        return self.procedural_engine.match_and_execute(task_or_trigger, context)

