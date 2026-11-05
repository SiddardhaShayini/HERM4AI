"""
Module: src/herm4ai/working_memory.py
Implementation of Working Memory (Research Pillar I, Component 5).
Maintains active cognitive context with bounded capacity (7 ± 2 slots),
dynamic salience scoring, scratchpad reasoning, and automated page-out eviction.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from .engine import HERMMemoryEngine
from .models import QueryResult, MemoryStatus


@dataclass
class WorkingSlot:
    slot_id: str
    entity: str
    attribute: str
    value: Any
    salience: float = 1.0
    loaded_at: str = ""
    last_touched: str = ""
    pinned: bool = False
    source_memory_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot_id": self.slot_id,
            "entity": self.entity,
            "attribute": self.attribute,
            "value": self.value,
            "salience": round(self.salience, 3),
            "loaded_at": self.loaded_at,
            "last_touched": self.last_touched,
            "pinned": self.pinned,
            "source_memory_id": self.source_memory_id,
        }


class WorkingMemoryBuffer:
    """
    Cognitive Working Memory Buffer.
    Maintains a bounded capacity of high-salience items currently active for reasoning.
    Adheres to Cowan / Miller cognitive limits (default capacity: 7 slots).
    """
    def __init__(self, long_term_engine: HERMMemoryEngine, capacity: int = 7):
        self.engine = long_term_engine
        self.capacity = capacity
        self.slots: Dict[str, WorkingSlot] = {}  # key: f"{entity}:{attribute}"
        self.scratchpad: Dict[str, Any] = {}     # temporary intermediate reasoning keys

    def clear(self):
        self.slots.clear()
        self.scratchpad.clear()

    def get_slot_count(self) -> int:
        return len(self.slots)

    def load(
        self,
        entity: str,
        attribute: str,
        query_time: Optional[str] = None,
        initial_salience: float = 1.0,
        pinned: bool = False
    ) -> Optional[WorkingSlot]:
        """
        Loads an item from long-term memory into working memory.
        If capacity is reached, evicts the lowest-salience unpinned slot.
        """
        now_iso = query_time or datetime.now().isoformat()
        slot_key = f"{entity}:{attribute}"

        # Query long-term memory engine
        res: QueryResult = self.engine.query(entity, attribute, "WorkingMemoryLoad", now_iso)
        if res.status in (MemoryStatus.UNKNOWN, MemoryStatus.DELETED):
            if slot_key in self.slots:
                del self.slots[slot_key]
            return None

        # If already in working memory, synchronize with latest engine state, refresh salience and touch
        if slot_key in self.slots:
            slot = self.slots[slot_key]
            slot.value = res.value
            slot.salience = min(2.0, slot.salience + 0.5)
            slot.last_touched = now_iso
            return slot

        # Check capacity and evict if full
        if len(self.slots) >= self.capacity:
            self._evict_lowest_salience()

        # Create new slot
        slot = WorkingSlot(
            slot_id=f"ws_{len(self.slots)+1:02d}",
            entity=entity,
            attribute=attribute,
            value=res.value,
            salience=initial_salience,
            loaded_at=now_iso,
            last_touched=now_iso,
            pinned=pinned
        )
        self.slots[slot_key] = slot
        return slot

    def _evict_lowest_salience(self):
        """
        Evicts the unpinned slot with the lowest salience score.
        """
        unpinned = [s for s in self.slots.values() if not s.pinned]
        if not unpinned:
            # All slots are pinned; evict oldest
            oldest_key = min(self.slots.keys(), key=lambda k: self.slots[k].last_touched)
            del self.slots[oldest_key]
            return

        lowest_slot = min(unpinned, key=lambda s: s.salience)
        lowest_key = f"{lowest_slot.entity}:{lowest_slot.attribute}"
        del self.slots[lowest_key]

    def touch(self, entity: str, attribute: str, boost: float = 0.2):
        """
        Boosts salience of a slot currently being referenced in reasoning.
        """
        slot_key = f"{entity}:{attribute}"
        if slot_key in self.slots:
            now_iso = datetime.now().isoformat()
            self.slots[slot_key].salience += boost
            self.slots[slot_key].last_touched = now_iso

    def write_scratchpad(self, key: str, value: Any):
        """
        Stores intermediate scratchpad variables during multi-step reasoning.
        """
        self.scratchpad[key] = value

    def read_scratchpad(self, key: str) -> Optional[Any]:
        return self.scratchpad.get(key)

    def decay_working_memory(self, decay_rate: float = 0.1):
        """
        Applies cognitive decay to working memory salience across cognitive turns.
        """
        for slot in self.slots.values():
            if not slot.pinned:
                slot.salience = max(0.1, slot.salience - decay_rate)

    def format_context_block(self) -> str:
        """
        Formats active working memory slots into a structured context block for prompt synthesis.
        """
        if not self.slots and not self.scratchpad:
            return "[Working Memory: Empty]"

        lines = [
            "=== ACTIVE WORKING MEMORY (Bounded Cognitive Context) ===",
            f"Slots Occupied: {len(self.slots)} / {self.capacity}"
        ]

        # Sort slots by salience descending
        sorted_slots = sorted(self.slots.values(), key=lambda s: s.salience, reverse=True)
        for s in sorted_slots:
            pin_badge = "[PINNED] " if s.pinned else ""
            lines.append(f"  * {pin_badge}{s.entity}.{s.attribute} = '{s.value}' (Salience: {s.salience:.2f})")

        if self.scratchpad:
            lines.append("--- Scratchpad (Intermediate Reasoning) ---")
            for k, v in self.scratchpad.items():
                lines.append(f"  * {k} : {v}")

        lines.append("==========================================================")
        return "\n".join(lines)
