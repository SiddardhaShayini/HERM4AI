"""
Module: src/herm4ai/engine.py
Core implementation of HERM4AI (Human-inspired, Explainable, Reconfigurable Memory).
Operates as a lightweight, auditable, model-free structured engine using SQLite.
Includes:
1. Semantic memory with deterministic temporal validity intervals and conflict detection.
2. Associative memory graph with spreading activation and dependency impact analysis.
3. Procedural memory store for reusable cognitive and workflow routines.
4. Cognitive lifecycle dynamics: access strengthening, consolidation, and temporal decay.
"""

import sqlite3
import uuid
import json
import math
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any, Set
from .models import (
    Assertion,
    MemoryRecord,
    AssociativeEdge,
    ProceduralRoutine,
    ProvenanceRecord,
    QueryResult,
    MemoryStatus,
    ConsolidationTier,
    EventType
)


class HERMMemoryEngine:
    """
    HERM4AI Structured Cognitive Memory Engine.
    Enforces deterministic temporal validity, conflict detection, associative graph reasoning,
    procedural workflows, cognitive consolidation/decay, and immutable provenance auditing.
    """
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.name = "HERM4AI"
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        with self.conn:
            # 1. Core Semantic / Episodic Memories Table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    entity TEXT NOT NULL,
                    attribute TEXT NOT NULL,
                    value TEXT,
                    valid_from TEXT NOT NULL,
                    valid_to TEXT,
                    source TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    status TEXT NOT NULL,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    last_accessed TEXT NOT NULL,
                    activation_strength REAL NOT NULL DEFAULT 1.0,
                    consolidation_tier TEXT NOT NULL DEFAULT 'EPISODIC',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_entity_attr ON memories (entity, attribute)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON memories (status)")

            # 2. Immutable Provenance Audit Log
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS provenance_log (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    memory_id TEXT,
                    entity TEXT NOT NULL,
                    attribute TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    details TEXT NOT NULL
                )
            """)
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_prov_entity ON provenance_log (entity, attribute)")

            # 3. Associative Memory Graph Table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS associative_edges (
                    id TEXT PRIMARY KEY,
                    source_entity TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    target_entity TEXT NOT NULL,
                    weight REAL NOT NULL DEFAULT 1.0,
                    valid_from TEXT NOT NULL,
                    valid_to TEXT,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'ACTIVE',
                    created_at TEXT NOT NULL
                )
            """)
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edge_source ON associative_edges (source_entity)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edge_target ON associative_edges (target_entity)")

            # 4. Procedural Memory Routines Table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS procedural_routines (
                    routine_id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    trigger_pattern TEXT NOT NULL,
                    action_steps TEXT NOT NULL,
                    preconditions TEXT,
                    success_rate REAL NOT NULL DEFAULT 1.0,
                    usage_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_proc_task ON procedural_routines (task_type)")

    def reset(self):
        with self.conn:
            self.conn.execute("DELETE FROM memories")
            self.conn.execute("DELETE FROM provenance_log")
            self.conn.execute("DELETE FROM associative_edges")
            self.conn.execute("DELETE FROM procedural_routines")

    def _log_provenance(
        self,
        event_type: EventType,
        entity: str,
        attribute: str,
        timestamp: str,
        source: str,
        details: str,
        memory_id: Optional[str] = None,
    ) -> ProvenanceRecord:
        event_id = f"evt_{uuid.uuid4().hex[:10]}"
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO provenance_log (event_id, event_type, memory_id, entity, attribute, timestamp, source, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (event_id, event_type.value, memory_id, entity, attribute, timestamp, source, details)
            )
        return ProvenanceRecord(
            event_id=event_id,
            event_type=event_type,
            memory_id=memory_id,
            entity=entity,
            attribute=attribute,
            timestamp=timestamp,
            source=source,
            details=details
        )

    # =========================================================================
    # 1. SEMANTIC MEMORY INGESTION & LIFECYCLE
    # =========================================================================

    def ingest(self, assertions: List[Assertion]):
        """
        Process an incoming stream of assertions and apply deterministic lifecycle transitions.
        """
        for a in assertions:
            now_iso = a.timestamp

            # Case 1: Explicit deletion (tombstone)
            if a.is_deletion or a.value is None:
                self._handle_deletion(a)
                continue

            # Check existing records for this entity + attribute
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM memories 
                WHERE entity = ? AND attribute = ? AND status IN ('ACTIVE', 'CONFLICTED')
                ORDER BY valid_from DESC
                """,
                (a.entity, a.attribute)
            )
            existing_records = cursor.fetchall()

            if not existing_records:
                # Case 2: Fresh assertion -> Encode new ACTIVE memory
                mem_id = f"mem_{uuid.uuid4().hex[:10]}"
                with self.conn:
                    self.conn.execute(
                        """
                        INSERT INTO memories (
                            id, entity, attribute, value, valid_from, valid_to,
                            source, confidence, status, access_count, last_accessed,
                            activation_strength, consolidation_tier, created_at, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, NULL, ?, ?, 'ACTIVE', 0, ?, 1.0, 'EPISODIC', ?, ?)
                        """,
                        (mem_id, a.entity, a.attribute, a.value, a.timestamp, a.source, a.confidence, now_iso, now_iso, now_iso)
                    )
                self._log_provenance(
                    EventType.ENCODE,
                    a.entity,
                    a.attribute,
                    a.timestamp,
                    a.source,
                    f"Encoded initial fact: {a.attribute}={a.value}",
                    memory_id=mem_id
                )
            else:
                top_record = existing_records[0]
                prev_val = top_record["value"]
                prev_from = top_record["valid_from"]
                prev_id = top_record["id"]

                if a.value == prev_val:
                    # Same value: Reinforce existing memory
                    with self.conn:
                        self.conn.execute(
                            """
                            UPDATE memories 
                            SET confidence = max(confidence, ?), 
                                updated_at = ?,
                                activation_strength = min(1.0, activation_strength + 0.1)
                            WHERE id = ?
                            """,
                            (a.confidence, now_iso, prev_id)
                        )
                    self._log_provenance(
                        EventType.UPDATE,
                        a.entity,
                        a.attribute,
                        a.timestamp,
                        a.source,
                        f"Reinforced memory {prev_id} with consistent value={a.value}",
                        memory_id=prev_id
                    )
                else:
                    # Different value: Determine whether this is a temporal revision or a contradiction
                    try:
                        t_new = datetime.fromisoformat(a.timestamp.replace("Z", "+00:00"))
                        t_prev = datetime.fromisoformat(prev_from.replace("Z", "+00:00"))
                        time_delta_sec = (t_new - t_prev).total_seconds()
                    except Exception:
                        time_delta_sec = 0.0

                    is_conflict = (time_delta_sec <= 0) or (a.source != top_record["source"] and time_delta_sec < 86400)

                    if not is_conflict:
                        # State Revision: Supersede old memory
                        with self.conn:
                            self.conn.execute(
                                "UPDATE memories SET status = 'SUPERSEDED', valid_to = ?, updated_at = ? WHERE id = ?",
                                (a.timestamp, now_iso, prev_id)
                            )
                        new_id = f"mem_{uuid.uuid4().hex[:10]}"
                        with self.conn:
                            self.conn.execute(
                                """
                                INSERT INTO memories (
                                    id, entity, attribute, value, valid_from, valid_to,
                                    source, confidence, status, access_count, last_accessed,
                                    activation_strength, consolidation_tier, created_at, updated_at
                                )
                                VALUES (?, ?, ?, ?, ?, NULL, ?, ?, 'ACTIVE', 0, ?, 1.0, 'EPISODIC', ?, ?)
                                """,
                                (new_id, a.entity, a.attribute, a.value, a.timestamp, a.source, a.confidence, now_iso, now_iso, now_iso)
                            )
                        self._log_provenance(
                            EventType.UPDATE,
                            a.entity,
                            a.attribute,
                            a.timestamp,
                            a.source,
                            f"Superseded memory {prev_id} (value='{prev_val}') with new value='{a.value}'",
                            memory_id=new_id
                        )
                    else:
                        # Contradiction: Multiple conflicting claims
                        self._handle_conflict(a, existing_records)

    def _handle_conflict(self, assertion: Assertion, existing_records: List[sqlite3.Row]):
        now_iso = assertion.timestamp
        with self.conn:
            for rec in existing_records:
                self.conn.execute(
                    "UPDATE memories SET status = 'CONFLICTED', updated_at = ? WHERE id = ?",
                    (now_iso, rec["id"])
                )
            new_id = f"mem_{uuid.uuid4().hex[:10]}"
            self.conn.execute(
                """
                INSERT INTO memories (
                    id, entity, attribute, value, valid_from, valid_to,
                    source, confidence, status, access_count, last_accessed,
                    activation_strength, consolidation_tier, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, NULL, ?, ?, 'CONFLICTED', 0, ?, 1.0, 'EPISODIC', ?, ?)
                """,
                (new_id, assertion.entity, assertion.attribute, assertion.value, assertion.timestamp, assertion.source, assertion.confidence, now_iso, now_iso, now_iso)
            )
        self._log_provenance(
            EventType.CONFLICT,
            assertion.entity,
            assertion.attribute,
            assertion.timestamp,
            assertion.source,
            f"Detected direct contradiction between sources. Marked as CONFLICTED.",
            memory_id=new_id
        )

    def _handle_deletion(self, assertion: Assertion):
        now_iso = assertion.timestamp
        with self.conn:
            self.conn.execute(
                """
                UPDATE memories 
                SET status = 'DELETED', valid_to = ?, updated_at = ?
                WHERE entity = ? AND attribute = ? AND status != 'DELETED'
                """,
                (assertion.timestamp, now_iso, assertion.entity, assertion.attribute)
            )
        self._log_provenance(
            EventType.DELETE,
            assertion.entity,
            assertion.attribute,
            assertion.timestamp,
            assertion.source,
            f"Expunged records under tombstone request from {assertion.source}"
        )

    # =========================================================================
    # 2. QUERY & COGNITIVE ACCESS STRENGTHENING
    # =========================================================================

    def query(self, entity: str, attribute: str, query_text: str, query_time: str) -> QueryResult:
        """
        Query memory state with full provenance trace, access strengthening, and associative context.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM memories 
            WHERE entity = ? AND attribute = ?
            ORDER BY valid_from DESC
            """,
            (entity, attribute)
        )
        records = cursor.fetchall()

        # Fetch provenance records for this entity & attribute
        cursor.execute(
            """
            SELECT * FROM provenance_log
            WHERE entity = ? AND attribute = ?
            ORDER BY timestamp ASC
            """,
            (entity, attribute)
        )
        prov_rows = cursor.fetchall()
        provenance = [
            ProvenanceRecord(
                event_id=row["event_id"],
                event_type=EventType(row["event_type"]),
                memory_id=row["memory_id"],
                entity=row["entity"],
                attribute=row["attribute"],
                timestamp=row["timestamp"],
                source=row["source"],
                details=row["details"]
            )
            for row in prov_rows
        ]

        # Fetch 1-hop associative context
        assoc_edges = self.get_associations(entity)
        assoc_context = [e.to_dict() for e in assoc_edges] if assoc_edges else None

        if not records:
            abstain_evt = self._log_provenance(
                EventType.ABSTAIN,
                entity,
                attribute,
                query_time,
                "HERM4AI_Engine",
                "Explicit abstention: no matching records found in storage."
            )
            return QueryResult(
                entity=entity,
                attribute=attribute,
                value="UNKNOWN",
                status=MemoryStatus.UNKNOWN,
                provenance=[abstain_evt],
                associative_context=assoc_context,
                system_name=self.name
            )

        latest = records[0]

        if latest["status"] == "DELETED":
            return QueryResult(
                entity=entity,
                attribute=attribute,
                value="DELETED",
                status=MemoryStatus.DELETED,
                provenance=provenance,
                associative_context=assoc_context,
                system_name=self.name
            )

        if latest["status"] == "ARCHIVED":
            return QueryResult(
                entity=entity,
                attribute=attribute,
                value=latest["value"],
                status=MemoryStatus.ARCHIVED,
                activation_strength=latest["activation_strength"],
                consolidation_tier=latest["consolidation_tier"],
                provenance=provenance,
                associative_context=assoc_context,
                system_name=self.name
            )

        if latest["status"] == "CONFLICTED":
            conflicting_values = list({r["value"] for r in records if r["status"] == "CONFLICTED"})
            return QueryResult(
                entity=entity,
                attribute=attribute,
                value="CONFLICTED",
                status=MemoryStatus.CONFLICTED,
                conflicting_values=conflicting_values,
                provenance=provenance,
                associative_context=assoc_context,
                system_name=self.name
            )

        if latest["status"] == "ACTIVE":
            # Cognitive Access Strengthening & Consolidation Check
            new_access_count = latest["access_count"] + 1
            new_tier = latest["consolidation_tier"]
            if new_access_count >= 3 and latest["consolidation_tier"] == "EPISODIC":
                new_tier = "CONSOLIDATED_SEMANTIC"
                consolidate_evt = self._log_provenance(
                    EventType.CONSOLIDATE,
                    entity,
                    attribute,
                    query_time,
                    "CognitiveEngine",
                    f"Consolidated memory {latest['id']} into long-term semantic memory (access count: {new_access_count})",
                    memory_id=latest["id"]
                )
                provenance.append(consolidate_evt)

            with self.conn:
                self.conn.execute(
                    """
                    UPDATE memories 
                    SET access_count = ?, 
                        last_accessed = ?, 
                        consolidation_tier = ?,
                        activation_strength = min(1.0, activation_strength + 0.05)
                    WHERE id = ?
                    """,
                    (new_access_count, query_time, new_tier, latest["id"])
                )

            superseded_values = [r["value"] for r in records if r["status"] == "SUPERSEDED"]
            return QueryResult(
                entity=entity,
                attribute=attribute,
                value=latest["value"],
                status=MemoryStatus.ACTIVE,
                superseded_values=superseded_values if superseded_values else None,
                activation_strength=min(1.0, latest["activation_strength"] + 0.05),
                consolidation_tier=new_tier,
                provenance=provenance,
                associative_context=assoc_context,
                system_name=self.name
            )

        return QueryResult(
            entity=entity,
            attribute=attribute,
            value="UNKNOWN",
            status=MemoryStatus.UNKNOWN,
            provenance=provenance,
            associative_context=assoc_context,
            system_name=self.name
        )

    # =========================================================================
    # 3. ASSOCIATIVE MEMORY & KNOWLEDGE GRAPH
    # =========================================================================

    def relate(
        self,
        source_entity: str,
        relation: str,
        target_entity: str,
        weight: float = 1.0,
        source: str = "System",
        timestamp: Optional[str] = None
    ) -> AssociativeEdge:
        """
        Create a directed associative connection between two memory entities.
        """
        edge_id = f"edge_{uuid.uuid4().hex[:10]}"
        now_iso = timestamp or datetime.now().isoformat()

        with self.conn:
            self.conn.execute(
                """
                INSERT INTO associative_edges (
                    id, source_entity, relation, target_entity, weight, valid_from, valid_to, source, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, NULL, ?, 'ACTIVE', ?)
                """,
                (edge_id, source_entity, relation, target_entity, weight, now_iso, source, now_iso)
            )

        self._log_provenance(
            EventType.RELATE,
            source_entity,
            relation,
            now_iso,
            source,
            f"Linked {source_entity} --[{relation}]--> {target_entity} (weight={weight})"
        )

        return AssociativeEdge(
            id=edge_id,
            source_entity=source_entity,
            relation=relation,
            target_entity=target_entity,
            weight=weight,
            valid_from=now_iso,
            source=source,
            status=MemoryStatus.ACTIVE,
            created_at=now_iso
        )

    def get_associations(self, entity: str, relation: Optional[str] = None, min_weight: float = 0.1) -> List[AssociativeEdge]:
        """
        Retrieve 1-hop associations directed from or to an entity.
        """
        cursor = self.conn.cursor()
        if relation:
            cursor.execute(
                """
                SELECT * FROM associative_edges 
                WHERE (source_entity = ? OR target_entity = ?) 
                  AND relation = ? AND weight >= ? AND status = 'ACTIVE'
                ORDER BY weight DESC
                """,
                (entity, entity, relation, min_weight)
            )
        else:
            cursor.execute(
                """
                SELECT * FROM associative_edges 
                WHERE (source_entity = ? OR target_entity = ?) 
                  AND weight >= ? AND status = 'ACTIVE'
                ORDER BY weight DESC
                """,
                (entity, entity, min_weight)
            )

        rows = cursor.fetchall()
        return [
            AssociativeEdge(
                id=r["id"],
                source_entity=r["source_entity"],
                relation=r["relation"],
                target_entity=r["target_entity"],
                weight=r["weight"],
                valid_from=r["valid_from"],
                valid_to=r["valid_to"],
                source=r["source"],
                status=MemoryStatus(r["status"]),
                created_at=r["created_at"]
            )
            for r in rows
        ]

    def associative_spread(
        self,
        start_entity: str,
        max_hops: int = 2,
        decay_factor: float = 0.5
    ) -> Dict[str, float]:
        """
        Spreading activation algorithm across associative memory graph.
        Returns a dictionary of {entity: activation_score}.
        """
        activation_scores: Dict[str, float] = {start_entity: 1.0}
        frontier: Dict[str, float] = {start_entity: 1.0}

        for hop in range(max_hops):
            next_frontier: Dict[str, float] = {}
            for current_node, current_act in frontier.items():
                edges = self.get_associations(current_node)
                for edge in edges:
                    neighbor = edge.target_entity if edge.source_entity == current_node else edge.source_entity
                    spread_val = current_act * edge.weight * decay_factor
                    if neighbor not in activation_scores or spread_val > activation_scores[neighbor]:
                        activation_scores[neighbor] = spread_val
                        next_frontier[neighbor] = spread_val
            frontier = next_frontier
            if not frontier:
                break

        return activation_scores

    def impact_analysis(self, entity: str) -> Dict[str, Any]:
        """
        Analyzes the downstream impact of an entity state change across associative connections.
        """
        downstream = self.get_associations(entity)
        dependent_entities = []
        for e in downstream:
            target = e.target_entity if e.source_entity == entity else e.source_entity
            dependent_entities.append({
                "entity": target,
                "relation": e.relation,
                "weight": e.weight,
                "direction": "outbound" if e.source_entity == entity else "inbound"
            })
        return {
            "source_entity": entity,
            "dependency_count": len(dependent_entities),
            "dependencies": dependent_entities
        }

    # =========================================================================
    # 4. PROCEDURAL MEMORY ROUTINES
    # =========================================================================

    def register_routine(
        self,
        task_type: str,
        trigger_pattern: str,
        action_steps: List[str],
        preconditions: Optional[str] = None
    ) -> ProceduralRoutine:
        """
        Registers a procedural workflow routine into procedural memory.
        """
        routine_id = f"proc_{uuid.uuid4().hex[:10]}"
        now_iso = datetime.now().isoformat()
        steps_json = json.dumps(action_steps)

        with self.conn:
            self.conn.execute(
                """
                INSERT INTO procedural_routines (
                    routine_id, task_type, trigger_pattern, action_steps, preconditions,
                    success_rate, usage_count, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, 1.0, 0, ?, ?)
                """,
                (routine_id, task_type, trigger_pattern, steps_json, preconditions, now_iso, now_iso)
            )

        return ProceduralRoutine(
            routine_id=routine_id,
            task_type=task_type,
            trigger_pattern=trigger_pattern,
            action_steps=action_steps,
            preconditions=preconditions,
            success_rate=1.0,
            usage_count=0,
            created_at=now_iso,
            updated_at=now_iso
        )

    def retrieve_routine(self, task_type_or_trigger: str) -> Optional[ProceduralRoutine]:
        """
        Retrieves matching procedural routine for a task type or trigger keyword.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM procedural_routines 
            WHERE task_type = ? OR trigger_pattern LIKE ?
            ORDER BY success_rate DESC, usage_count DESC
            LIMIT 1
            """,
            (task_type_or_trigger, f"%{task_type_or_trigger}%")
        )
        row = cursor.fetchone()
        if not row:
            return None

        # Increment usage count
        now_iso = datetime.now().isoformat()
        with self.conn:
            self.conn.execute(
                "UPDATE procedural_routines SET usage_count = usage_count + 1, updated_at = ? WHERE routine_id = ?",
                (now_iso, row["routine_id"])
            )

        return ProceduralRoutine(
            routine_id=row["routine_id"],
            task_type=row["task_type"],
            trigger_pattern=row["trigger_pattern"],
            action_steps=json.loads(row["action_steps"]),
            preconditions=row["preconditions"],
            success_rate=row["success_rate"],
            usage_count=row["usage_count"] + 1,
            created_at=row["created_at"],
            updated_at=now_iso
        )

    # =========================================================================
    # 5. COGNITIVE DECAY & ARCHIVAL DYNAMICS
    # =========================================================================

    def apply_temporal_decay(
        self,
        current_time_iso: str,
        archive_threshold: float = 0.15
    ) -> Dict[str, Any]:
        """
        Applies cognitive forgetting curve to memories based on time elapsed since last access.
        Dormant memories falling below archive_threshold are transitioned to ARCHIVED.
        """
        try:
            t_now = datetime.fromisoformat(current_time_iso.replace("Z", "+00:00"))
        except Exception:
            t_now = datetime.now()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE status = 'ACTIVE'")
        active_memories = cursor.fetchall()

        decayed_count = 0
        archived_count = 0

        for mem in active_memories:
            try:
                t_last = datetime.fromisoformat(mem["last_accessed"].replace("Z", "+00:00"))
                delta_days = max(0.0, (t_now - t_last).total_seconds() / 86400.0)
            except Exception:
                delta_days = 0.0

            # Consolidated memories decay much slower (lambda = 0.01) vs episodic (lambda = 0.05)
            decay_rate = 0.01 if mem["consolidation_tier"] == "CONSOLIDATED_SEMANTIC" else 0.05
            base_activation = mem["confidence"] * math.exp(-decay_rate * delta_days)
            boost = 0.2 * math.log(1.0 + mem["access_count"])
            new_activation = round(max(0.0, min(1.0, base_activation + boost)), 4)

            new_status = "ACTIVE"
            if new_activation < archive_threshold:
                new_status = "ARCHIVED"
                archived_count += 1
                self._log_provenance(
                    EventType.DECAY,
                    mem["entity"],
                    mem["attribute"],
                    current_time_iso,
                    "CognitiveDecayEngine",
                    f"Activation dropped to {new_activation} (< {archive_threshold}); memory moved to ARCHIVED tier.",
                    memory_id=mem["id"]
                )

            with self.conn:
                self.conn.execute(
                    """
                    UPDATE memories 
                    SET activation_strength = ?, status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (new_activation, new_status, current_time_iso, mem["id"])
                )
            decayed_count += 1

        return {
            "current_time": current_time_iso,
            "memories_evaluated": decayed_count,
            "memories_archived": archived_count,
            "archive_threshold": archive_threshold
        }
