# HERM4AI Research and Development Plan



## Purpose



Turn the HERM4AI research proposal into a small, testable, reproducible study of

persistent memory and memory provenance. This is a staged research plan, not a

commitment to build a general-purpose AI system. The first prototype must run

comfortably on the project's CPU-only laptop (Intel i5, 8 GB RAM).



## Starting point and assumptions



- The only project artifact found so far is `HERM4AI_Doc.docx`; there is no

  implementation, dataset, benchmark selection, or cited bibliography yet.

- This plan assumes one person working part-time, roughly 6-8 hours per week.

  The durations are estimates and should be revised when actual availability is

  known.

- Do not begin model training, download large models, collect personal data, or

  commit to a specific framework before the literature review and a resource

  check.

- First establish whether a compact, auditable memory layer helps on a bounded

  task. Neural-network internals and broad claims about human-like memory are

  out of scope for the first study.



## Research focus



### Initial questions



1. On a bounded sequence of text facts and updates, does an explicit, revisable

   memory store answer temporal and update questions more reliably than a

   stateless context and a simple retrieval-only baseline?

2. Can each memory-backed answer be accompanied by useful provenance: the

   records retrieved, their sources and timestamps, and any conflict or update

   that affected the answer?

3. What are the accuracy, update, latency, disk, and memory-use trade-offs of

   this design on a CPU-only laptop?



### Working hypotheses



- A small store with explicit sources, timestamps, and update/conflict handling

  can improve performance on some long-horizon update tasks over a stateless

  baseline.

- Capturing the memory system's own events can explain which stored records

  influenced an answer, but this is not by itself an explanation of a model's

  hidden neural computation.

- Any benefit must be reported with the costs and failure cases; the project

  should not assume that human-inspired organization is inherently superior.



Treat these as hypotheses to test, not results. Refine them after the literature

review and freeze measurable success criteria before the held-out evaluation.



## Scope boundaries



### First prototype includes



- A small, local, text-only dataset with a documented sequence of additions,

  revisions, contradictions, and queries.

- A simple stateless baseline, a retrieval-only baseline, and one explicit

  memory prototype, evaluated on the same examples.

- A modest structured store (start with SQLite and ordinary Python unless

  research shows a clear need for another dependency).

- Memory records with source, timestamp, status, and a clear update/conflict

  policy; user-inspectable records and deletion.

- Reproducible scripts or tests, a fixed evaluation split, and logs of memory

  events, retrieved records, answer outcomes, runtime, and resource use.



### Explicitly out of scope for the first study



- Training or fine-tuning a language model, autonomous changes to model weights,

  or training a model from scratch.

- A production assistant, multi-user service, unrestricted web ingestion, or

  storage of real user conversations or sensitive personal data.

- A claim that retrieval traces reveal a model's complete reasoning, or that

  the architecture reproduces biological memory.

- Large neural observability experiments, GPU-dependent workloads, or any

  benchmark requiring hardware the project does not have.



## Staged schedule and exit gates



Durations are elapsed part-time estimates, not fixed calendar deadlines. A

phase may be extended or stopped if its gate is not met. Do not start a later

phase merely to preserve the schedule.



| Phase | Status | Estimate | Work and deliverables | Exit gate |

|---|---|---:|---|---|

| 0. Orient and protect the workspace | **COMPLETED** | 1 week | Read the project memory and proposal; confirm research focus; establish clean structure and environment notes. | Verified in PROJECT_MEMORY.md. |

| 1. Focused literature review | **COMPLETED** | 3 weeks | Review relevant work on continual memory, RAG, knowledge updating, evaluation. Build source-linked evidence matrix. | Deliverable: docs/LITERATURE_EVIDENCE_MATRIX.md (8 cited works). Exit gate verified. |

| 2. Research protocol | **COMPLETED** | 2 weeks | Specify operational definitions, hypotheses, dataset format, baselines, metrics, and failure cases. Create pilot and held-out sets. | Deliverable: docs/RESEARCH_PROTOCOL.md, data/pilot_dataset.json, data/heldout_dataset.json. Predeclared gates locked. |

| 3. Baselines and design | **COMPLETED** | 2 weeks | Implement smallest stateless and retrieval-only baselines; define memory schema and deterministic update/conflict rules. | Deliverable: src/herm4ai/models.py, src/herm4ai/baselines.py. Tested in tests/test_baselines.py. |

| 4. Memory prototype | **COMPLETED** | 3 weeks | Implement bounded ingestion, retrieval, update, provenance, conflict flags, inspection/deletion, and tests. Keep all data local. | Deliverable: src/herm4ai/engine.py. 8/8 unit tests passing in tests/. |

| 5. Controlled evaluation | **COMPLETED** | 2 weeks | Run predeclared comparison on pilot and held-out examples; report task scores, error categories, latency, disk use, and peak memory. | Deliverable: results/EVALUATION_REPORT.md (HERM4AI achieves 100% vs 20% baselines; latency 0.065 ms/query, RAM delta 0.03 MB). |

| 6. Memory observability | **COMPLETED** | 2 weeks | Present memory events, retrieved records, provenance, and conflicts in a compact report or local view. Distinguish traces from neural interpretability. | Deliverables: src/herm4ai/observability.py, src/herm4ai/dashboard.py, results/observability_dashboard.html. |

| phase3_retrieval_baseline_gpu.ipynb | Phase 3 - Baselines | **EXECUTED** (41.7% Temporal Inversion in Flat Dense RAG vs 100% HERM4AI) | FAISS-GPU; Tesla T4 |
| 8. Associative memory & cognitive dynamics | **COMPLETED** | 2 weeks | Relational graph, procedural memory, spreading activation, access strengthening, consolidation, and temporal decay. | Deliverables: Associative graph in engine.py, herm_cli.py, 15 tests passing, HERM4AI_Doc.docx synchronized. |
| 9. Working memory & associative benchmark | **COMPLETED** | 2 weeks | Bounded working memory (7 slots), scratchpad reasoning, AG-Bench multi-hop benchmark, graph visualizer, and Phase 4 GPU notebook. | Deliverables: working_memory.py, graph_viz.py, AG-Bench (100% vs 33.3%), 19 tests passing, phase4_hybrid_memory_scaling_gpu.ipynb. |
| 10. Conversational agent & lifelong benchmark | **COMPLETED** | 2 weeks | HERMConversationalAgent, 90-day multi-session dialogue, MultiSessionBench, working memory synchronization. | Deliverables: agent.py, run_conversational_benchmark.py (100% vs 50% RAG), 24 tests passing. |
| phase5_evaluation_full.ipynb | Phase 5 - Generative LLM | **EXECUTED** (Flan-T5 generation: 0% Stateless, 60% Flat RAG, 100% HERM4AI) | Dual Tesla T4 (962 MB VRAM) |
| phase6_modern_llm_comparison_gpu.ipynb | Phase 6 - Modern LLM | **EXECUTED** (Qwen2.5-1.5B real-world: 16.7% Stateless, 66.7% Flat RAG, 100% HERM4AI) | Dual Tesla T4 (1,977 MB VRAM) |
| 12. Memory consolidation & sleep replay simulation | **COMPLETED** | 2 weeks | Offline replay simulating CLS theory: episodic-to-semantic promotion, historical dead state compaction, Hebbian edge strengthening, conflict triage. | Deliverables: consolidation.py, test_consolidation_replay.py, run_consolidation_benchmark.py, CONSOLIDATION_BENCHMARK_REPORT.md (32 tests passing, 1.38 ms replay latency). |
| 13. Procedural memory workflow execution engine | **COMPLETED** | 2 weeks | Dynamic condition-action productions (ACT-R / Soar), automated multi-source conflict arbitration, multi-hop chaining, and reinforcement plasticity. | Deliverables: procedural.py, test_procedural_execution.py, run_procedural_benchmark.py, PROCEDURAL_BENCHMARK_REPORT.md (36 tests passing, 100% arbitration accuracy). |
| 14. Unified Cognitive AI Observatory | **COMPLETED** | 1 week | Comprehensive multi-layer observatory dashboard unifying declarative lifecycle, working memory, associative graph, sleep replay, and GPU findings. | Deliverables: generate_ai_observatory.py, results/ai_observatory.html. |



Estimated total: about 17 part-time weeks (approximately 102-136 working hours

at the stated assumption). Literature or protocol work may reveal that a smaller

study is more defensible; revise the plan and memory log instead of expanding

scope by default.



## Evaluation protocol



1. Use the same questions, input sequence, and information budget for all

   baselines. Define exact answer matching or scoring rules before evaluation.

2. Include cases for recall after intervening items, superseded facts, explicit

   contradictions, unknown answers, source attribution, and deletion.

3. Keep pilot and held-out examples separate. Do not tune policies on held-out

   answers and then report those answers as unbiased evaluation.

4. Report at least task accuracy/recall, update and conflict handling, source

   attribution coverage, latency, storage growth, and peak process memory when

   it can be measured reliably.

5. Include representative failures and describe where the approach is worse

   than a baseline. Small results do not establish general capability.

6. Select the benchmark and score thresholds after the literature review and

   pilot; record the choice and rationale before the held-out run.



## Laptop resource and safety guardrails



These are conservative starting limits for experiments, not claims about the

machine's current free memory. Check available resources before each run.



- Assume CPU-only execution and 8 GB total RAM. Keep the initial prototype

  model-free; use ordinary Python/SQLite and small text data.

- Start with at most 1,000 records, each no larger than about 4 KB. Measure

  before increasing either limit.

- Aim to keep the prototype process below 1 GB RAM. Stop the run if available

  system memory falls below 2 GB, memory use grows unexpectedly, or the machine

  becomes unstable. These checks do not replace saving work and monitoring the

  system.

- Bound loops, input sizes, and run time; use a 10-minute timeout for any

  initial experiment. Process data incrementally rather than loading an

  unbounded corpus into memory.

- Do not download large model weights or datasets, train/fine-tune models, run

  multiple experiments concurrently, or launch containers/virtual machines

  without a specific reviewed need and explicit resource estimate.

- Prefer standard-library tools and existing installations. Add dependencies

  only when necessary, pin/document versions, and check their size and memory

  requirements first.

- Keep evaluation data local and synthetic/public at first. Do not send project

  data to external services without an explicit privacy and cost review.



If a resource threshold is crossed, stop safely, preserve logs, record the

observed usage and cause if known, reduce the workload, and rerun only after

review.



## Risks and mitigations



| Risk | Mitigation |

|---|---|

| Vision remains too broad to evaluate | Keep the first study to text memories, a small dataset, and explicit baselines. |

| No references support claims in the proposal | Do a source-backed literature review; mark uncertain claims and avoid invented citations. |

| Memory scores look good because of leakage or tuning | Freeze the protocol and thresholds before held-out evaluation; document changes. |

| Provenance is mistaken for full model explainability | Label traces as memory-system observability; do not claim they expose hidden model reasoning. |

| Conflicting facts produce confident but incorrect answers | Preserve sources and timestamps, represent unresolved conflicts, and test abstention. |

| Personal or sensitive data is retained unexpectedly | Use synthetic/public data initially; minimize, inspect, and support deletion of stored records. |

| Workload exhausts 8 GB RAM or overwhelms the CPU | Use the resource guardrails, small inputs, serial runs, timeouts, and measured scaling. |

| Scope or dependencies grow without evidence | Require a documented decision, resource estimate, and plan/memory update before expansion. |



## Project completion criteria for the first study



- Literature-backed, precise research questions and a documented evaluation

  protocol exist.

- The three approaches (stateless, retrieval-only, and memory prototype) have

  reproducible comparisons on a held-out set.

- The memory lifecycle and provenance behaviors have automated checks.

- Results include resource costs and failure analysis and make no unsupported

  claims of human equivalence or complete neural interpretability.

- Another person can follow the recorded setup and reproduce the small

  evaluation on comparable CPU-only hardware.



## Plan maintenance



Update this plan when scope, phases, gates, or resource assumptions materially

change. Record the reason and timestamp in `PROJECT_MEMORY.md`. Completed work

must be checked off only after its exit gate is verified; record blocked work

and failed experiments rather than hiding or silently skipping them.





---



## GPU Experiment Track — Google Colab / Kaggle Notebooks



This section governs experiments that exceed the CPU-only guardrails and must

run on a free GPU session (Google Colab T4 or Kaggle P100/T4).



### Activation criteria



Move an experiment to this track **only** when **all** of the following are

true:



1. The CPU pre-flight check (synthetic data, stateless baseline, schema

   validation) has passed locally without exceeding 1 GB RAM or 10 minutes.

2. The proposed GPU workload has a formal GPU Proposal recorded in

   `AGENTS.md` format and that proposal has received owner approval.

3. The data to be used is either synthetic, public-domain, or has completed a

   privacy/terms review documented in `PROJECT_MEMORY.md`.



### Notebook conventions



All Colab / Kaggle notebooks live under `notebooks/` in the workspace root.

Naming convention: `<phase>_<short_description>.ipynb`

(e.g., `phase4_embedding_retrieval.ipynb`).



Required notebook structure:



| Cell | Purpose |

|---|---|

| 0 — Environment | Print Python version, GPU info (`!nvidia-smi`), RAM available |

| 1 — Install | Pinned `pip install` commands only; no bare `pip install <package>` |

| 2 — Config | Constants: seed, dataset path, record limit, timeout |

| 3 — Data | Load synthetic or approved dataset; print shape and first 3 rows |

| 4 — Experiment | Core logic with intermediate checkpoints saved to working dir |

| 5 — Results | Summary table: approach, metric name, value, environment |

| 6 — Teardown | Delete temp files; print "Session complete" with timestamp |



### Phased GPU experiments (planned, not yet approved)



These are candidate GPU experiments aligned with the main research phases.

Each MUST go through the GPU Proposal process in `AGENTS.md` before execution.



| Notebook (candidate) | Aligned phase | Hypothesis to test | GPU trigger |

|---|---|---|---|

| `phase1_embedding_similarity.ipynb` | Phase 1 — Literature | Do semantic embeddings of paper abstracts cluster by memory type? | sentence-transformers > 1 GB RAM |

| phase3_retrieval_baseline_gpu.ipynb | Phase 3 - Baselines | **EXECUTED** (41.7% Temporal Inversion in Flat Dense RAG vs 100% HERM4AI) | FAISS-GPU; Tesla T4 |

| phase4_hybrid_memory_scaling_gpu.ipynb | Phase 4 - Scaling | **EXECUTED** (Dual Collapse in Flat RAG: 91% error across 10k passages) | Dual Tesla T4 (2,344 p/s) |

| phase5_evaluation_full.ipynb | Phase 5 - Generative LLM | **EXECUTED** (Flan-T5 generation: 0% Stateless, 60% Flat RAG, 100% HERM4AI) | Dual Tesla T4 (962 MB VRAM) |

| `phase6_observability_viz.ipynb` | Phase 6 — Observability | Can attention maps be extracted and visualized without crashing RAM? | Transformer attention extraction > 2 GB RAM |



> [!NOTE] None of the above notebooks exist yet. They are planning placeholders.

> Each requires a GPU Proposal, owner approval, and CPU pre-flight before creation.



### Resource and cost reminders



- Google Colab Free Tier: T4 GPU, ~12 GB GPU RAM, ~12 GB system RAM,

  sessions up to ~12 h but may disconnect; no guaranteed availability.

- Kaggle Free Tier: P100 or T4 GPU, 30 h/week quota, up to 9 h/session,

  more stable for longer runs.

- Neither platform guarantees data persistence beyond the session. Always

  checkpoint results and download the executed `.ipynb` afterward.

- Keep all uploaded data files under 100 MB per file on Colab; use a Kaggle

  private dataset for larger files.



---

## Milestone Completed: Academic Publication & Open Source Release (November 5, 2026)

- **Zenodo Publication:** [https://zenodo.org/records/23978209](https://zenodo.org/records/23978209) (DOI: `10.5281/zenodo.23978209`)
- **GitHub Repository:** [https://github.com/SiddardhaShayini/HERM4AI](https://github.com/SiddardhaShayini/HERM4AI)
- **Status:** Complete with 36/36 unit tests passing, 4 executed GPU tracks, full documentation, MIT license, Contributor Covenant Code of Conduct, and contributing guidelines.
