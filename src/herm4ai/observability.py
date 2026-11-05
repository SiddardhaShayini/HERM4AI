"""
Module: src/herm4ai/observability.py
Observability and audit trace visualization for HERM4AI.
Renders memory timelines, event graphs, and conflict reports.
"""

from typing import List, Dict, Any
from .models import QueryResult, ProvenanceRecord, EventType


def render_provenance_timeline(query_result: QueryResult) -> str:
    """
    Renders an ASCII timeline of provenance events for a given query result.
    Clarifies memory subsystem events without claiming to interpret hidden neural weights.
    """
    lines = [
        f"==================================================================",
        f" HERM4AI OBSERVABILITY & PROVENANCE REPORT",
        f" Target Entity   : {query_result.entity}",
        f" Target Attribute: {query_result.attribute}",
        f" Current Value   : {query_result.value}",
        f" Lifecycle Status: {query_result.status.value}",
        f"==================================================================",
        f" Event Chronology ({len(query_result.provenance)} events):"
    ]

    for idx, p in enumerate(query_result.provenance, 1):
        icon = {
            EventType.ENCODE: "[+] ENCODE  ",
            EventType.UPDATE: "[~] UPDATE  ",
            EventType.CONFLICT: "[!] CONFLICT",
            EventType.DELETE: "[-] DELETE  ",
            EventType.RETRIEVE: "[?] RETRIEVE",
            EventType.ABSTAIN: "[0] ABSTAIN "
        }.get(p.event_type, "[ ] UNKNOWN ")

        lines.append(
            f"  {idx:02d}. {icon} | {p.timestamp} | Source: {p.source:<20} | {p.details}"
        )

    if query_result.conflicting_values:
        lines.append("------------------------------------------------------------------")
        lines.append(f"  [!] Conflicting Values Detected: {query_result.conflicting_values}")

    if query_result.superseded_values:
        lines.append("------------------------------------------------------------------")
        lines.append(f"  [~] Superseded Historical Values: {query_result.superseded_values}")

    lines.append("==================================================================")
    lines.append(" NOTE: Memory event provenance represents storage subsystem operations.")
    lines.append(" It does not claim to expose neural network activation pathways.")
    lines.append("==================================================================")

    return "\n".join(lines)
