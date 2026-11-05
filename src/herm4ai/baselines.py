"""
Module: src/herm4ai/baselines.py
Implementation of comparison baselines:
1. StatelessBaseline: Retains zero memory across turns.
2. NaiveRetrievalBaseline: Unstructured lexical retrieval without lifecycle, timestamp, or conflict modeling.
"""

from typing import List, Optional
import re
from .models import Assertion, QueryResult, MemoryStatus, ProvenanceRecord


class StatelessBaseline:
    """
    Stateless baseline: Does not maintain persistent state.
    Evaluates what happens when an agent operates solely on zero-shot inference without memory.
    """
    def __init__(self):
        self.name = "StatelessBaseline"

    def reset(self):
        pass

    def ingest(self, assertions: List[Assertion]):
        # No-op: stateless system retains nothing
        pass

    def query(self, entity: str, attribute: str, query_text: str, query_time: str) -> QueryResult:
        return QueryResult(
            entity=entity,
            attribute=attribute,
            value="UNKNOWN",
            status=MemoryStatus.UNKNOWN,
            provenance=[],
            system_name=self.name
        )


class NaiveRetrievalBaseline:
    """
    Naive Retrieval baseline (Lexical / Bag-of-Words similarity over raw string logs).
    Simulates naive RAG without lifecycle tracking, timestamps, or conflict resolution.
    Known failure mode: Cannot distinguish between obsolete superseded facts and current facts.
    """
    def __init__(self):
        self.name = "NaiveRetrievalBaseline"
        self.store: List[Assertion] = []

    def reset(self):
        self.store.clear()

    def ingest(self, assertions: List[Assertion]):
        for a in assertions:
            # Naive retrieval stores the assertion verbatim
            self.store.append(a)

    def query(self, entity: str, attribute: str, query_text: str, query_time: str) -> QueryResult:
        if not self.store:
            return QueryResult(
                entity=entity,
                attribute=attribute,
                value="UNKNOWN",
                status=MemoryStatus.UNKNOWN,
                provenance=[],
                system_name=self.name
            )

        # Keyword matching against entity and attribute
        entity_tokens = set(re.findall(r"\w+", entity.lower()))
        attr_tokens = set(re.findall(r"\w+", attribute.lower()))

        best_score = -1
        best_candidate: Optional[Assertion] = None

        # Naive retrieval iterates through store and scores overlap
        # In case of tie, it typically returns the first match encountered (or whatever index hit first)
        for assertion in self.store:
            stored_text = f"{assertion.entity} {assertion.attribute} {assertion.value}".lower()
            stored_tokens = set(re.findall(r"\w+", stored_text))

            score = 0
            if entity_tokens.issubset(stored_tokens):
                score += 2
            if attr_tokens.issubset(stored_tokens):
                score += 2

            # Lexical tie-break: earlier stored facts or arbitrary order
            if score > best_score and score >= 2:
                best_score = score
                best_candidate = assertion

        if best_candidate is None:
            return QueryResult(
                entity=entity,
                attribute=attribute,
                value="UNKNOWN",
                status=MemoryStatus.UNKNOWN,
                provenance=[],
                system_name=self.name
            )

        # Naive RAG has no concept of deletion or status: if string was stored, it returns the string
        val = best_candidate.value if best_candidate.value is not None else "UNKNOWN"
        return QueryResult(
            entity=entity,
            attribute=attribute,
            value=val,
            status=MemoryStatus.ACTIVE if val != "UNKNOWN" else MemoryStatus.UNKNOWN,
            provenance=[],  # No structured provenance
            system_name=self.name
        )
