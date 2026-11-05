# HERM4AI Phase 5 Controlled Evaluation Report
*Benchmark: TFSR-Bench (Temporal Fact & State Revision)*
*Date: 2026-11-04*

## 1. Executive Summary

This controlled experiment evaluates three systems on 90 total test instances (30 pilot, 60 held-out) across 5 core evaluation axes:
- **DR**: Direct Recall
- **TR**: Temporal Revision (superseded facts)
- **CA**: Conflict Attribution (contradictory sources)
- **AU**: Abstention on Unknown (out-of-domain queries)
- **TD**: Tombstone Deletion ('right to be forgotten')

## 2. Held-Out Evaluation Results (60 Cases)

| System | Overall Acc (%) | DR (%) | TR (%) | CA (%) | AU (%) | TD (%) | Provenance Coverage (%) | Total Latency (ms) | Peak RAM Delta (MB) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **StatelessBaseline** | 20.0% | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% | 0.1 ms | 0.02 MB |
| **NaiveRetrievalBaseline** | 20.0% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.6 ms | 0.02 MB |
| **HERM4AI** | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 5.1 ms | 0.02 MB |

## 3. Pilot Evaluation Results (30 Cases)

| System | Overall Acc (%) | DR (%) | TR (%) | CA (%) | AU (%) | TD (%) | Provenance Coverage (%) | Total Latency (ms) | Peak RAM Delta (MB) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **StatelessBaseline** | 20.0% | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% | 0.1 ms | 0.01 MB |
| **NaiveRetrievalBaseline** | 20.0% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.5 ms | 0.01 MB |
| **HERM4AI** | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 2.8 ms | 0.08 MB |

## 4. Key Experimental Findings

1. **Temporal Revision Failure in Naive Retrieval:** Naive Retrieval achieved 0.0% on TR because it blindly retrieves the first lexical hit (the obsolete, superseded fact). HERM4AI achieved **100.0%** by actively managing valid-time intervals.
2. **Conflict Resolution:** Naive Retrieval achieved 0.0% on CA because it has no representation of conflict. HERM4AI achieved **100.0%** Conflict Detection Rate, flagging contradictory sources rather than hallucinating an answer.
3. **Tombstone Deletion Integrity:** When deletion was requested, Naive Retrieval continued leaking the deleted string (0.0% TD score). HERM4AI cleanly purged the value, achieved **100.0%** deletion audit, and retained an auditable tombstone event.
4. **Full Provenance Without Model Overhead:** HERM4AI provided **100.0%** verifiable provenance coverage with an average query latency under **1.0 millisecond** and near-zero memory footprint (< 1 MB RAM delta), well below the 1 GB laptop guardrail.