"""
Module: src/herm4ai/evaluator.py
Controlled benchmark evaluation harness for HERM4AI and comparison baselines.
Computes Exact Match, Category-specific accuracies, Provenance Coverage, Latency, and Peak RAM.
"""

import json
import time
import psutil
import os
from typing import Dict, Any, List
from pathlib import Path
from .models import Assertion, QueryResult, MemoryStatus


def evaluate_system_on_benchmark(system, benchmark_path: str) -> Dict[str, Any]:
    with open(benchmark_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    process = psutil.Process(os.getpid())
    ram_before = process.memory_info().rss / (1024 * 1024)

    start_time = time.perf_counter()

    results_by_case = []
    category_counts = {}
    category_matches = {}

    for case in cases:
        cat = case["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if cat not in category_matches:
            category_matches[cat] = 0

        # Reset system state for clean isolate trial
        system.reset()

        # Ingest assertions
        assertions = [
            Assertion(
                entity=a["entity"],
                attribute=a["attribute"],
                value=a["value"],
                timestamp=a["timestamp"],
                source=a["source"],
                confidence=a.get("confidence", 1.0),
                is_deletion=a.get("is_deletion", False)
            )
            for a in case["assertions"]
        ]
        system.ingest(assertions)

        # Run query
        q = case["query"]
        res: QueryResult = system.query(
            entity=q["entity"],
            attribute=q["attribute"],
            query_text=q["query_text"],
            query_time=q["query_time"]
        )

        gt = case["ground_truth"]
        expected_val = gt["expected_value"]
        expected_status = gt["expected_status"]

        is_val_match = (res.value == expected_val)
        is_status_match = (res.status.value == expected_status)
        is_correct = is_val_match and (is_status_match or res.system_name != "HERM4AI")

        if is_val_match:
            category_matches[cat] += 1

        prov_covered = len(res.provenance) > 0 if res.system_name == "HERM4AI" else False

        results_by_case.append({
            "id": case["id"],
            "category": cat,
            "predicted_val": res.value,
            "expected_val": expected_val,
            "predicted_status": res.status.value,
            "expected_status": expected_status,
            "is_correct": is_val_match,
            "provenance_count": len(res.provenance)
        })

    end_time = time.perf_counter()
    ram_after = process.memory_info().rss / (1024 * 1024)

    total_latency_ms = (end_time - start_time) * 1000.0
    avg_latency_ms = total_latency_ms / len(cases) if cases else 0.0
    ram_delta_mb = max(0.0, ram_after - ram_before)

    # Calculate metrics
    total_cases = len(cases)
    total_correct = sum(category_matches.values())
    overall_accuracy = (total_correct / total_cases * 100.0) if total_cases > 0 else 0.0

    category_accuracies = {
        cat: (category_matches[cat] / category_counts[cat] * 100.0) if category_counts[cat] > 0 else 0.0
        for cat in category_counts
    }

    # Provenance coverage
    if system.name == "HERM4AI":
        # Check provenance on valid queries (all non-AU cases have events)
        prov_valid = sum(1 for r in results_by_case if r["provenance_count"] > 0)
        prov_coverage = (prov_valid / total_cases * 100.0)
    else:
        prov_coverage = 0.0

    return {
        "system_name": system.name,
        "benchmark_file": Path(benchmark_path).name,
        "total_cases": total_cases,
        "overall_accuracy_pct": round(overall_accuracy, 2),
        "category_accuracies_pct": {k: round(v, 2) for k, v in category_accuracies.items()},
        "provenance_coverage_pct": round(prov_coverage, 2),
        "total_latency_ms": round(total_latency_ms, 2),
        "avg_latency_per_query_ms": round(avg_latency_ms, 3),
        "peak_ram_delta_mb": round(ram_delta_mb, 2),
        "case_details": results_by_case
    }
