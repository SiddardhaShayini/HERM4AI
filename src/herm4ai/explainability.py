"""
Module: src/herm4ai/explainability.py
Implementation of the HERM4AI Explainability & Observability Framework (Research Pillar II).
Answers the 7 fundamental explainability questions:
1. Which memories contributed?
2. Where did the knowledge originate (provenance)?
3. Which associative concepts were activated?
4. Which memories conflicted?
5. Which memories were revised / superseded?
6. Which information was ignored / suppressed?
7. What is the counterfactual necessity score of each memory?
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from .engine import HERMMemoryEngine
from .models import QueryResult, MemoryStatus, EventType


@dataclass
class MemoryAttribution:
    memory_id: str
    entity: str
    attribute: str
    value: str
    status: str
    counterfactual_influence: float  # 1.0 = strictly necessary, 0.0 = irrelevant
    is_causal_necessity: bool
    provenance_source: str
    valid_from: str
    valid_to: Optional[str] = None


@dataclass
class ExplainabilityAuditReport:
    query_entity: str
    query_attribute: str
    produced_answer: str
    lifecycle_status: str
    contributing_memories: List[MemoryAttribution]
    originating_sources: List[str]
    activated_associative_concepts: List[str]
    conflicted_memories: List[str]
    revised_memories: List[str]
    suppressed_memories: List[str]
    counterfactual_summary: str
    audit_timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_entity": self.query_entity,
            "query_attribute": self.query_attribute,
            "produced_answer": self.produced_answer,
            "lifecycle_status": self.lifecycle_status,
            "originating_sources": self.originating_sources,
            "activated_associative_concepts": self.activated_associative_concepts,
            "conflicted_memories": self.conflicted_memories,
            "revised_memories": self.revised_memories,
            "suppressed_memories": self.suppressed_memories,
            "contributing_memories": [
                {
                    "memory_id": m.memory_id,
                    "entity": m.entity,
                    "attribute": m.attribute,
                    "value": m.value,
                    "influence_score": m.counterfactual_influence,
                    "is_causal_necessity": m.is_causal_necessity,
                    "source": m.provenance_source,
                }
                for m in self.contributing_memories
            ],
            "counterfactual_summary": self.counterfactual_summary,
            "audit_timestamp": self.audit_timestamp,
        }

    def format_text_report(self) -> str:
        lines = [
            "==================================================================",
            " HERM4AI EXPLAINABILITY & COGNITIVE OBSERVATION REPORT",
            f" Target: {self.query_entity}.{self.query_attribute}",
            f" Answer Produced : '{self.produced_answer}' [Status: {self.lifecycle_status}]",
            f" Audit Timestamp : {self.audit_timestamp}",
            "==================================================================",
            " 1. KNOWLEDGE ORIGIN & PROVENANCE:",
            f"    Sources: {', '.join(self.originating_sources) if self.originating_sources else 'None'}",
            "",
            " 2. MEMORY ATTRIBUTION & COUNTERFACTUAL INFLUENCE:",
        ]
        for m in self.contributing_memories:
            nec_badge = "[CAUSAL NECESSITY]" if m.is_causal_necessity else "[SUPPORTING]"
            lines.append(
                f"    * ID: {m.memory_id} | Val: '{m.value}' | Influence: {m.counterfactual_influence:.2f} {nec_badge}"
            )
            lines.append(f"      Source: {m.provenance_source} (Valid from: {m.valid_from})")

        lines.extend([
            "",
            " 3. KNOWLEDGE REVISIONS & SUPPRESSIONS:",
            f"    * Revised (Superseded) Values : {self.revised_memories if self.revised_memories else 'None'}",
            f"    * Conflicting Claims Detected : {self.conflicted_memories if self.conflicted_memories else 'None'}",
            f"    * Suppressed Past Memories    : {self.suppressed_memories if self.suppressed_memories else 'None'}",
            "",
            " 4. ASSOCIATIVE CONCEPTS ACTIVATED:",
            f"    * Reached Network Nodes       : {self.activated_associative_concepts if self.activated_associative_concepts else 'None'}",
            "",
            " 5. COUNTERFACTUAL AUDIT SUMMARY:",
            f"    {self.counterfactual_summary}",
            "==================================================================",
            " SCIENTIFIC DISCLAIMER: This audit report traces verified memory store",
            " events and counterfactual perturbations. It does not claim to expose",
            " deep internal transformer attention heads or hidden biological states.",
            "=================================================================="
        ])
        return "\n".join(lines)


class ExplainabilityAuditEngine:
    """
    Cognitive Explainability and Counterfactual Attribution Engine.
    Evaluates memory operations, perturbation influence, and causal necessity.
    """
    def __init__(self, engine: HERMMemoryEngine):
        self.engine = engine

    def audit_query(
        self,
        entity: str,
        attribute: str,
        query_time: Optional[str] = None
    ) -> ExplainabilityAuditReport:
        now_iso = query_time or datetime.now().isoformat()

        # Step 1: Baseline query execution
        baseline_res: QueryResult = self.engine.query(entity, attribute, "ExplainabilityAudit", now_iso)

        # Step 2: Fetch all stored records for entity and attribute
        cursor = self.engine.conn.cursor()
        cursor.execute(
            "SELECT * FROM memories WHERE entity = ? AND attribute = ? ORDER BY valid_from DESC",
            (entity, attribute)
        )
        records = cursor.fetchall()

        # Step 3: Identify active, superseded, conflicted, and suppressed
        contributing_attributions: List[MemoryAttribution] = []
        originating_sources = list({r["source"] for r in records})
        conflicted_values = [r["value"] for r in records if r["status"] == "CONFLICTED"]
        superseded_values = [r["value"] for r in records if r["status"] == "SUPERSEDED"]
        suppressed_ids = [r["id"] for r in records if r["status"] in ("SUPERSEDED", "DELETED", "ARCHIVED")]

        # Step 4: Counterfactual Influence Analysis
        # For each record, simulate what happens if this record were withheld
        counterfactual_notes = []

        for r in records:
            mem_id = r["id"]
            orig_status = r["status"]

            # Perturbation: temporarily mark as WITHHELD
            with self.engine.conn:
                self.engine.conn.execute(
                    "UPDATE memories SET status = 'WITHHELD' WHERE id = ?",
                    (mem_id,)
                )

            # Re-evaluate query without this memory
            perturbed_res: QueryResult = self.engine.query(entity, attribute, "PerturbedAudit", now_iso)

            # Restore original status
            with self.engine.conn:
                self.engine.conn.execute(
                    "UPDATE memories SET status = ? WHERE id = ?",
                    (orig_status, mem_id)
                )

            # Quantify counterfactual divergence
            if baseline_res.value != perturbed_res.value:
                # Answer completely changed without this memory -> 1.0 (causal necessity)
                influence = 1.0
                is_causal = True
                counterfactual_notes.append(
                    f"Withholding {mem_id} causes answer to flip from '{baseline_res.value}' to '{perturbed_res.value}'."
                )
            elif baseline_res.status != perturbed_res.status:
                # Status changed (e.g. from ACTIVE to CONFLICTED or UNKNOWN)
                influence = 0.8
                is_causal = True
                counterfactual_notes.append(
                    f"Withholding {mem_id} alters lifecycle status from {baseline_res.status.value} to {perturbed_res.status.value}."
                )
            else:
                # Answer and status unchanged (e.g. an already superseded historical record)
                influence = 0.1 if orig_status == "SUPERSEDED" else 0.0
                is_causal = False

            if orig_status in ("ACTIVE", "CONFLICTED") or is_causal:
                contributing_attributions.append(
                    MemoryAttribution(
                        memory_id=mem_id,
                        entity=entity,
                        attribute=attribute,
                        value=r["value"],
                        status=orig_status,
                        counterfactual_influence=influence,
                        is_causal_necessity=is_causal,
                        provenance_source=r["source"],
                        valid_from=r["valid_from"],
                        valid_to=r["valid_to"]
                    )
                )

        # Step 5: Associative network activation
        associative_nodes = []
        if baseline_res.associative_context:
            for edge in baseline_res.associative_context:
                target = edge["target_entity"] if edge["source_entity"] == entity else edge["source_entity"]
                associative_nodes.append(f"{target} ({edge['relation']})")

        cf_summary = " ".join(counterfactual_notes) if counterfactual_notes else "Answer is stable under individual perturbations."

        return ExplainabilityAuditReport(
            query_entity=entity,
            query_attribute=attribute,
            produced_answer=baseline_res.value if baseline_res.value is not None else "UNKNOWN",
            lifecycle_status=baseline_res.status.value,
            contributing_memories=contributing_attributions,
            originating_sources=originating_sources,
            activated_associative_concepts=associative_nodes,
            conflicted_memories=list(set(conflicted_values)),
            revised_memories=list(set(superseded_values)),
            suppressed_memories=suppressed_ids,
            counterfactual_summary=cf_summary,
            audit_timestamp=now_iso
        )
