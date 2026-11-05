"""
Module: src/herm4ai/models.py
Data models and typed structures for assertions, memories, associative edges,
procedural routines, provenance traces, and query results.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import uuid


class MemoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    CONFLICTED = "CONFLICTED"
    UNKNOWN = "UNKNOWN"
    DELETED = "DELETED"
    ARCHIVED = "ARCHIVED"


class ConsolidationTier(str, Enum):
    EPISODIC = "EPISODIC"
    CONSOLIDATED_SEMANTIC = "CONSOLIDATED_SEMANTIC"
    ARCHIVED = "ARCHIVED"


class EventType(str, Enum):
    ENCODE = "ENCODE"
    UPDATE = "UPDATE"
    CONFLICT = "CONFLICT"
    DELETE = "DELETE"
    RETRIEVE = "RETRIEVE"
    ABSTAIN = "ABSTAIN"
    CONSOLIDATE = "CONSOLIDATE"
    DECAY = "DECAY"
    RELATE = "RELATE"
    REPLAY = "REPLAY"
    PROCEDURAL = "PROCEDURAL"


@dataclass
class Assertion:
    entity: str
    attribute: str
    value: Optional[str]
    timestamp: str
    source: str
    confidence: float = 1.0
    is_deletion: bool = False


@dataclass
class AssociativeEdge:
    id: str
    source_entity: str
    relation: str
    target_entity: str
    weight: float = 1.0
    valid_from: str = ""
    valid_to: Optional[str] = None
    source: str = "Manual"
    status: MemoryStatus = MemoryStatus.ACTIVE
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_entity": self.source_entity,
            "relation": self.relation,
            "target_entity": self.target_entity,
            "weight": self.weight,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "source": self.source,
            "status": self.status.value,
            "created_at": self.created_at,
        }


@dataclass
class ProceduralRoutine:
    routine_id: str
    task_type: str
    trigger_pattern: str
    action_steps: List[str]
    preconditions: Optional[str] = None
    success_rate: float = 1.0
    usage_count: int = 0
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "routine_id": self.routine_id,
            "task_type": self.task_type,
            "trigger_pattern": self.trigger_pattern,
            "action_steps": self.action_steps,
            "preconditions": self.preconditions,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class ProvenanceRecord:
    event_id: str
    event_type: EventType
    memory_id: Optional[str]
    entity: str
    attribute: str
    timestamp: str
    source: str
    details: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "memory_id": self.memory_id,
            "entity": self.entity,
            "attribute": self.attribute,
            "timestamp": self.timestamp,
            "source": self.source,
            "details": self.details,
        }


@dataclass
class MemoryRecord:
    id: str
    entity: str
    attribute: str
    value: Optional[str]
    valid_from: str
    valid_to: Optional[str]
    source: str
    confidence: float
    status: MemoryStatus
    created_at: str
    updated_at: str
    access_count: int = 0
    last_accessed: str = ""
    activation_strength: float = 1.0
    consolidation_tier: ConsolidationTier = ConsolidationTier.EPISODIC

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity": self.entity,
            "attribute": self.attribute,
            "value": self.value,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "source": self.source,
            "confidence": self.confidence,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "activation_strength": self.activation_strength,
            "consolidation_tier": self.consolidation_tier.value,
        }


@dataclass
class QueryResult:
    entity: str
    attribute: str
    value: Optional[str]
    status: MemoryStatus
    provenance: List[ProvenanceRecord] = field(default_factory=list)
    conflicting_values: Optional[List[str]] = None
    superseded_values: Optional[List[str]] = None
    activation_strength: float = 1.0
    consolidation_tier: str = "EPISODIC"
    associative_context: Optional[List[Dict[str, Any]]] = None
    system_name: str = "HERM4AI"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_name": self.system_name,
            "entity": self.entity,
            "attribute": self.attribute,
            "value": self.value,
            "status": self.status.value,
            "activation_strength": self.activation_strength,
            "consolidation_tier": self.consolidation_tier,
            "conflicting_values": self.conflicting_values,
            "superseded_values": self.superseded_values,
            "associative_context": self.associative_context,
            "provenance": [p.to_dict() for p in self.provenance],
        }
