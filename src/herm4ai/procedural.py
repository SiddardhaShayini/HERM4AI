"""
Module: src/herm4ai/procedural.py
Procedural Memory Workflow Execution Engine for HERM4AI.
Implements ACT-R / Soar inspired production rules, dynamic workflow execution,
precondition checking, step-by-step cognitive actions, and reinforcement plasticity.
"""

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import json
import time
import uuid

from src.herm4ai.models import ProceduralRoutine, MemoryStatus, EventType
from src.herm4ai.engine import HERMMemoryEngine
from src.herm4ai.working_memory import WorkingMemoryBuffer


class ProceduralExecutionEngine:
    """
    Executes and reinforces procedural workflows stored in procedural memory.
    Enables autonomous problem-solving, contradiction resolution workflows,
    multi-hop graph traversals, and standard cognitive procedures.
    """

    def __init__(
        self,
        engine: HERMMemoryEngine,
        working_memory: Optional[WorkingMemoryBuffer] = None
    ):
        self.engine = engine
        self.working_memory = working_memory
        self.action_registry: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self._register_default_actions()

    def _register_default_actions(self):
        """
        Registers core cognitive action primitives executable by procedural routines.
        """
        self.action_registry["CHECK_PRECONDITION"] = self._action_check_precondition
        self.action_registry["QUERY_AUTHORITATIVE_SOURCE"] = self._action_query_authoritative_source
        self.action_registry["RESOLVE_CONFLICT_BY_TIMESTAMP"] = self._action_resolve_conflict_by_timestamp
        self.action_registry["RESOLVE_CONFLICT_BY_CONFIDENCE"] = self._action_resolve_conflict_by_confidence
        self.action_registry["MULTI_HOP_ASSOCIATIVE_EXPANSION"] = self._action_multi_hop_expansion
        self.action_registry["UPDATE_WORKING_MEMORY"] = self._action_update_working_memory
        self.action_registry["LOG_AUDIT_PROVENANCE"] = self._action_log_audit_provenance
        self.action_registry["FALLBACK_ABSTAIN"] = self._action_fallback_abstain

    def register_custom_action(self, action_name: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """
        Allows external callers to extend the procedural cognitive action set.
        """
        self.action_registry[action_name] = handler

    # -------------------------------------------------------------------------
    # Core Cognitive Actions
    # -------------------------------------------------------------------------

    def _action_check_precondition(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        req_status = ctx.get("expected_status")
        entity = ctx.get("entity")
        attr = ctx.get("attribute")
        if entity and attr and req_status:
            cursor = self.engine.conn.cursor()
            cursor.execute(
                "SELECT status FROM memories WHERE entity = ? AND attribute = ? ORDER BY valid_from DESC LIMIT 1",
                (entity, attr)
            )
            row = cursor.fetchone()
            if not row or row["status"] != req_status:
                return {"success": False, "reason": f"Expected status {req_status}, found {row['status'] if row else 'None'}"}
        return {"success": True, "detail": "Preconditions satisfied."}

    def _action_query_authoritative_source(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        entity = ctx.get("entity")
        attr = ctx.get("attribute")
        preferred_source = ctx.get("preferred_source", "HR_Official")
        cursor = self.engine.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM memories 
            WHERE entity = ? AND attribute = ? AND source LIKE ?
            ORDER BY valid_from DESC LIMIT 1
            """,
            (entity, attr, f"%{preferred_source}%")
        )
        row = cursor.fetchone()
        if row:
            ctx["resolved_value"] = row["value"]
            ctx["resolved_source"] = row["source"]
            ctx["resolved_confidence"] = row["confidence"]
            return {"success": True, "selected_value": row["value"], "source": row["source"]}
        return {"success": False, "reason": f"No record found from authoritative source {preferred_source}"}

    def _action_resolve_conflict_by_timestamp(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        entity = ctx.get("entity")
        attr = ctx.get("attribute")
        cursor = self.engine.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM memories 
            WHERE entity = ? AND attribute = ? AND status = 'CONFLICTED'
            ORDER BY valid_from DESC
            """,
            (entity, attr)
        )
        conflicts = cursor.fetchall()
        if not conflicts:
            return {"success": False, "reason": "No conflicted records found"}

        winner = conflicts[0]  # Latest timestamp
        now_iso = datetime.now().isoformat()

        # Update winner to ACTIVE, others to SUPERSEDED
        with self.engine.conn:
            self.engine.conn.execute(
                "UPDATE memories SET status = 'ACTIVE', updated_at = ? WHERE id = ?",
                (now_iso, winner["id"])
            )
            for c in conflicts[1:]:
                self.engine.conn.execute(
                    "UPDATE memories SET status = 'SUPERSEDED', valid_to = ?, updated_at = ? WHERE id = ?",
                    (winner["valid_from"], now_iso, c["id"])
                )

        ctx["resolved_value"] = winner["value"]
        ctx["resolved_source"] = winner["source"]

        self.engine._log_provenance(
            EventType.PROCEDURAL,
            entity,
            attr,
            now_iso,
            "ProceduralEngine_ConflictResolver",
            f"Resolved conflict: selected latest assertion '{winner['value']}' from {winner['source']}",
            memory_id=winner["id"]
        )

        return {"success": True, "winner_id": winner["id"], "winner_value": winner["value"]}

    def _action_resolve_conflict_by_confidence(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        entity = ctx.get("entity")
        attr = ctx.get("attribute")
        cursor = self.engine.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM memories 
            WHERE entity = ? AND attribute = ? AND status = 'CONFLICTED'
            ORDER BY confidence DESC, valid_from DESC
            """,
            (entity, attr)
        )
        conflicts = cursor.fetchall()
        if not conflicts:
            return {"success": False, "reason": "No conflicted records found"}

        winner = conflicts[0]
        now_iso = datetime.now().isoformat()

        with self.engine.conn:
            self.engine.conn.execute(
                "UPDATE memories SET status = 'ACTIVE', updated_at = ? WHERE id = ?",
                (now_iso, winner["id"])
            )
            for c in conflicts[1:]:
                self.engine.conn.execute(
                    "UPDATE memories SET status = 'SUPERSEDED', valid_to = ?, updated_at = ? WHERE id = ?",
                    (winner["valid_from"], now_iso, c["id"])
                )

        ctx["resolved_value"] = winner["value"]
        ctx["resolved_source"] = winner["source"]

        self.engine._log_provenance(
            EventType.PROCEDURAL,
            entity,
            attr,
            now_iso,
            "ProceduralEngine_ConfidenceResolver",
            f"Resolved conflict: selected highest confidence ({winner['confidence']:.2f}) assertion '{winner['value']}' from {winner['source']}",
            memory_id=winner["id"]
        )

        return {"success": True, "winner_id": winner["id"], "winner_value": winner["value"]}

    def _action_multi_hop_expansion(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        start_entity = ctx.get("start_entity", ctx.get("entity"))
        max_hops = ctx.get("max_hops", 2)
        spread = self.engine.associative_spread(start_entity, max_hops=max_hops)
        ctx["associative_spread"] = spread
        return {"success": True, "nodes_reached": len(spread), "scores": spread}

    def _action_update_working_memory(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        entity = ctx.get("entity")
        attr = ctx.get("attribute")
        resolved_val = ctx.get("resolved_value")
        if self.working_memory and entity and attr and resolved_val:
            slot = self.working_memory.load(entity, attr, initial_salience=1.0)
            if slot:
                slot.value = resolved_val
            return {"success": True, "slot_id": slot.slot_id if slot else None, "value": resolved_val}
        return {"success": False, "reason": "Working memory buffer unavailable or missing values"}

    def _action_log_audit_provenance(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        entity = ctx.get("entity", "SYSTEM")
        attr = ctx.get("attribute", "PROCEDURE")
        detail = ctx.get("audit_detail", "Procedural workflow executed successfully.")
        now_iso = datetime.now().isoformat()
        evt = self.engine._log_provenance(
            EventType.PROCEDURAL,
            entity,
            attr,
            now_iso,
            "ProceduralExecutionEngine",
            detail
        )
        return {"success": True, "event_id": evt.event_id}

    def _action_fallback_abstain(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        entity = ctx.get("entity", "UNKNOWN")
        attr = ctx.get("attribute", "UNKNOWN")
        now_iso = datetime.now().isoformat()
        self.engine._log_provenance(
            EventType.ABSTAIN,
            entity,
            attr,
            now_iso,
            "ProceduralExecutionEngine",
            "Routine reached fallback abstention step."
        )
        return {"success": True, "action": "ABSTAINED"}

    # -------------------------------------------------------------------------
    # Execution & Reinforcement
    # -------------------------------------------------------------------------

    def execute_routine(
        self,
        routine: ProceduralRoutine,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes a procedural routine step-by-step, evaluating conditions,
        dispatching cognitive actions, and updating routine success rate plasticity.
        """
        ctx = context.copy() if context else {}
        ctx["routine_id"] = routine.routine_id
        ctx["task_type"] = routine.task_type

        step_logs: List[Dict[str, Any]] = []
        overall_success = True
        t0 = time.perf_counter()

        for step_idx, step_name in enumerate(routine.action_steps):
            step_start = time.perf_counter()
            action_fn = self.action_registry.get(step_name)

            if not action_fn:
                step_logs.append({
                    "step_index": step_idx,
                    "action_name": step_name,
                    "success": False,
                    "error": f"Unknown cognitive action primitive: '{step_name}'",
                    "duration_ms": 0.0
                })
                overall_success = False
                break

            try:
                res = action_fn(ctx)
                dur_ms = (time.perf_counter() - step_start) * 1000.0
                step_success = res.get("success", True)
                step_logs.append({
                    "step_index": step_idx,
                    "action_name": step_name,
                    "success": step_success,
                    "result": res,
                    "duration_ms": round(dur_ms, 3)
                })
                if not step_success:
                    overall_success = False
                    break
            except Exception as e:
                dur_ms = (time.perf_counter() - step_start) * 1000.0
                step_logs.append({
                    "step_index": step_idx,
                    "action_name": step_name,
                    "success": False,
                    "error": str(e),
                    "duration_ms": round(dur_ms, 3)
                })
                overall_success = False
                break

        total_dur_ms = (time.perf_counter() - t0) * 1000.0

        # Reinforcement update: Exponential Moving Average
        old_rate = routine.success_rate
        alpha = 0.15
        reward = 1.0 if overall_success else 0.0
        new_rate = round(float((1.0 - alpha) * old_rate + alpha * reward), 3)
        new_count = routine.usage_count + 1
        now_iso = datetime.now().isoformat()

        # Update database
        with self.engine.conn:
            self.engine.conn.execute(
                """
                UPDATE procedural_routines 
                SET success_rate = ?, usage_count = ?, updated_at = ?
                WHERE routine_id = ?
                """,
                (new_rate, new_count, now_iso, routine.routine_id)
            )

        routine.success_rate = new_rate
        routine.usage_count = new_count
        routine.updated_at = now_iso

        return {
            "routine_id": routine.routine_id,
            "task_type": routine.task_type,
            "overall_success": overall_success,
            "steps_executed": len(step_logs),
            "step_logs": step_logs,
            "total_duration_ms": round(total_dur_ms, 3),
            "prior_success_rate": old_rate,
            "updated_success_rate": new_rate,
            "usage_count": new_count,
            "context_state": ctx
        }

    def match_and_execute(
        self,
        task_or_trigger: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves matching procedural routine from storage and executes it.
        """
        routine = self.engine.retrieve_routine(task_or_trigger)
        if not routine:
            return None
        return self.execute_routine(routine, context)
