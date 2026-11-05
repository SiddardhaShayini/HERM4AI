"""
Module: src/herm4ai/consolidation.py
Offline memory consolidation and sleep-phase replay engine for HERM4AI.
Implements episodic-to-semantic abstraction, Hebbian synaptic edge strengthening,
historical superseded state pruning, and conflict triage during simulated sleep cycles.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import math
import uuid

from src.herm4ai.models import MemoryStatus, ConsolidationTier, EventType
from src.herm4ai.engine import HERMMemoryEngine


class MemoryConsolidationEngine:
    """
    Simulates offline sleep-phase memory consolidation inspired by Complementary
    Learning Systems (CLS) theory and biological sleep replay.
    """

    def __init__(self, engine: HERMMemoryEngine):
        self.engine = engine

    def simulate_sleep_cycle(
        self,
        cycle_timestamp_iso: Optional[str] = None,
        min_accesses_for_semantic: int = 2,
        min_activation_for_semantic: float = 0.65,
        prune_superseded_older_than_days: float = 30.0,
        edge_strengthen_factor: float = 0.15,
        edge_prune_threshold: float = 0.05
    ) -> Dict[str, Any]:
        """
        Executes an offline sleep replay and memory consolidation cycle.

        Phases:
        1. Episodic-to-Semantic Promotion: Identifies stable, frequently accessed
           episodic memories without conflicts and elevates them to consolidated semantic tier.
        2. Superseded History Compaction: Archives old superseded historical states
           beyond the retention window to reduce active indexing overhead while preserving provenance.
        3. Synaptic Plasticity & Graph Replay: Strengthens associative connections between
           frequently co-active concepts and prunes dormant, low-weight edges.
        4. Conflict Triage: Identifies unresolved contradictory assertions and queues
           them for verification.
        """
        now_iso = cycle_timestamp_iso or datetime.now().isoformat()
        try:
            t_now = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
        except Exception:
            t_now = datetime.now()

        promoted_count = 0
        archived_superseded_count = 0
        edges_strengthened_count = 0
        edges_pruned_count = 0
        unresolved_conflicts: List[Dict[str, Any]] = []

        cursor = self.engine.conn.cursor()

        # ---------------------------------------------------------------------
        # 1. EPISODIC-TO-SEMANTIC PROMOTION
        # ---------------------------------------------------------------------
        cursor.execute(
            """
            SELECT * FROM memories 
            WHERE consolidation_tier = 'EPISODIC' 
              AND status = 'ACTIVE'
            """
        )
        episodic_memories = cursor.fetchall()

        for mem in episodic_memories:
            access_count = mem["access_count"]
            activation = mem["activation_strength"]
            # Eligible if frequently accessed, sufficiently active, and high confidence
            if (
                access_count >= min_accesses_for_semantic
                and activation >= min_activation_for_semantic
                and mem["confidence"] >= 0.8
            ):
                with self.engine.conn:
                    self.engine.conn.execute(
                        """
                        UPDATE memories 
                        SET consolidation_tier = 'CONSOLIDATED_SEMANTIC',
                            confidence = MIN(1.0, confidence + 0.05),
                            updated_at = ?
                        WHERE id = ?
                        """,
                        (now_iso, mem["id"])
                    )
                self.engine._log_provenance(
                    EventType.CONSOLIDATE,
                    mem["entity"],
                    mem["attribute"],
                    now_iso,
                    "SleepConsolidationEngine",
                    f"Promoted to CONSOLIDATED_SEMANTIC (accesses={access_count}, activation={activation:.2f})",
                    memory_id=mem["id"]
                )
                promoted_count += 1

        # ---------------------------------------------------------------------
        # 2. SUPERSEDED HISTORY COMPACTION & ARCHIVING
        # ---------------------------------------------------------------------
        cursor.execute(
            """
            SELECT * FROM memories 
            WHERE status = 'SUPERSEDED' AND valid_to IS NOT NULL
            """
        )
        superseded_memories = cursor.fetchall()

        for mem in superseded_memories:
            try:
                t_valid_to = datetime.fromisoformat(mem["valid_to"].replace("Z", "+00:00"))
                days_elapsed = max(0.0, (t_now - t_valid_to).total_seconds() / 86400.0)
            except Exception:
                days_elapsed = 0.0

            if days_elapsed >= prune_superseded_older_than_days:
                with self.engine.conn:
                    self.engine.conn.execute(
                        """
                        UPDATE memories 
                        SET status = 'ARCHIVED',
                            consolidation_tier = 'ARCHIVED',
                            updated_at = ?
                        WHERE id = ?
                        """,
                        (now_iso, mem["id"])
                    )
                self.engine._log_provenance(
                    EventType.DECAY,
                    mem["entity"],
                    mem["attribute"],
                    now_iso,
                    "SleepConsolidationEngine",
                    f"Historical superseded record archived after {days_elapsed:.1f} days dormancy.",
                    memory_id=mem["id"]
                )
                archived_superseded_count += 1

        # ---------------------------------------------------------------------
        # 3. SYNAPTIC PLASTICITY & ASSOCIATIVE GRAPH CONSOLIDATION
        # ---------------------------------------------------------------------
        cursor.execute("SELECT * FROM associative_edges WHERE status = 'ACTIVE'")
        active_edges = cursor.fetchall()

        for edge in active_edges:
            src = edge["source_entity"]
            tgt = edge["target_entity"]
            current_weight = edge["weight"]

            # Check if both endpoints are consolidated or actively accessed
            cursor.execute(
                "SELECT COUNT(*) as active_cnt FROM memories WHERE entity IN (?, ?) AND access_count > 0 AND status = 'ACTIVE'",
                (src, tgt)
            )
            activity = cursor.fetchone()["active_cnt"]

            if activity >= 2:
                # Both endpoints active: strengthen edge (Hebbian co-activation)
                new_weight = round(min(1.0, current_weight + edge_strengthen_factor), 3)
                with self.engine.conn:
                    self.engine.conn.execute(
                        "UPDATE associative_edges SET weight = ? WHERE id = ?",
                        (new_weight, edge["id"])
                    )
                edges_strengthened_count += 1
            elif current_weight < edge_prune_threshold:
                # Dormant weak edge: prune/archive
                with self.engine.conn:
                    self.engine.conn.execute(
                        "UPDATE associative_edges SET status = 'ARCHIVED' WHERE id = ?",
                        (edge["id"],)
                    )
                edges_pruned_count += 1

        # ---------------------------------------------------------------------
        # 4. CONFLICT TRIAGE
        # ---------------------------------------------------------------------
        cursor.execute("SELECT * FROM memories WHERE status = 'CONFLICTED'")
        conflicted_records = cursor.fetchall()
        for c in conflicted_records:
            unresolved_conflicts.append({
                "memory_id": c["id"],
                "entity": c["entity"],
                "attribute": c["attribute"],
                "value": c["value"],
                "source": c["source"],
                "valid_from": c["valid_from"],
                "confidence": c["confidence"]
            })

        # Log overarching sleep replay cycle event
        self.engine._log_provenance(
            EventType.REPLAY,
            "SYSTEM",
            "SLEEP_CYCLE",
            now_iso,
            "SleepConsolidationEngine",
            f"Consolidation cycle completed: {promoted_count} promoted, {archived_superseded_count} archived, "
            f"{edges_strengthened_count} edges strengthened, {edges_pruned_count} pruned, "
            f"{len(unresolved_conflicts)} conflicts queued."
        )

        return {
            "cycle_timestamp": now_iso,
            "promoted_to_semantic_count": promoted_count,
            "superseded_archived_count": archived_superseded_count,
            "edges_strengthened_count": edges_strengthened_count,
            "edges_pruned_count": edges_pruned_count,
            "unresolved_conflicts_flagged": len(unresolved_conflicts),
            "unresolved_conflicts": unresolved_conflicts,
            "summary_narrative": (
                f"Sleep Replay Cycle at {now_iso}: Successfully consolidated {promoted_count} episodic memories "
                f"into semantic store; compacted {archived_superseded_count} superseded records; strengthened "
                f"{edges_strengthened_count} associative connections; pruned {edges_pruned_count} dormant edges; "
                f"triaged {len(unresolved_conflicts)} pending conflicts."
            )
        }

    def get_consolidation_metrics(self) -> Dict[str, Any]:
        """
        Returns snapshot metrics on memory consolidation distribution across tiers.
        """
        cursor = self.engine.conn.cursor()
        cursor.execute(
            """
            SELECT consolidation_tier, status, COUNT(*) as count, AVG(activation_strength) as avg_act, AVG(confidence) as avg_conf
            FROM memories
            GROUP BY consolidation_tier, status
            """
        )
        rows = cursor.fetchall()

        cursor.execute("SELECT COUNT(*), AVG(weight) FROM associative_edges WHERE status = 'ACTIVE'")
        edge_stats = cursor.fetchone()

        tier_breakdown = {}
        for r in rows:
            key = f"{r['consolidation_tier']}_{r['status']}"
            tier_breakdown[key] = {
                "count": r["count"],
                "avg_activation": round(r["avg_act"] or 0.0, 3),
                "avg_confidence": round(r["avg_conf"] or 0.0, 3)
            }

        return {
            "tier_breakdown": tier_breakdown,
            "active_edges_count": edge_stats[0] if edge_stats else 0,
            "mean_edge_weight": round(edge_stats[1] or 0.0, 3) if edge_stats and edge_stats[1] else 0.0
        }
