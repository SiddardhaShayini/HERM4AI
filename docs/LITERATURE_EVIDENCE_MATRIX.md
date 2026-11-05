# HERM4AI Literature Evidence Matrix
*Phase 1 Deliverable — Scientific Literature Review & Prior Art Positioning*
*Date: 2026-11-04*

---

## 1. Executive Summary & Research Gap

Modern Artificial Intelligence systems struggle with three interlocking challenges:
1. **Long-term knowledge persistence and temporal revision** (facts in the real world change, e.g., job titles, addresses, software APIs).
2. **Deterministic conflict resolution and deletion** ("right to be forgotten", contradictory claims from unverified sources).
3. **Observability and provenance** (verifying *why* and *when* an item entered memory, and distinguishing memory traces from neural model hallucination).

Prior approaches generally fall into three paradigms:
- **Parametric Model Editing (e.g., ROME, MEMIT):** Alters internal weights directly. Highly fragile, risks catastrophic forgetting, computationally expensive, and offers no provenance trail or reversible deletion.
- **Unstructured / Vector Retrieval-Augmented Generation (RAG):** Embeds all documents into flat vector or lexical indices. Fails on temporal updates because both old ("Bob works at Google in 2020") and new ("Bob moved to OpenAI in 2024") documents remain in the index, frequently retrieving outdated facts due to lexical or semantic similarity.
- **LLM Agent Memory Streams (e.g., Generative Agents, MemGPT):** Uses LLM-driven summaries or paging. Powerful but nondeterministic, opaque in conflict resolution, computationally heavy, and prone to context drift and hallucination.

**The HERM4AI Scientific Contribution:**
HERM4AI provides an explicit, auditable, lifecycle-aware structured memory engine with deterministic state transitions (`ACTIVE`, `SUPERSEDED`, `CONFLICTED`, `DELETED`), zero model dependency for the memory management layer, complete provenance logging, and verifiable abstention when information is unknown.

---

## 2. Structured Evidence Matrix

| Citation | Core Method | Memory Type Modeled | Update & Deletion Mechanism | Provenance & Observability | Measured Limitations | HERM4AI Distinction |
|---|---|---|---|---|---|---|
| **Park et al. (2023)**<br>*Generative Agents: Interactive Simulacra of Human Behavior*<br>arXiv:2304.03442 | Memory Stream with recency, importance, and relevance scores; periodic LLM reflection | Episodic, Working | Appends all events to stream; periodic reflections compress memory; no explicit deletion or contradiction detection | Natural language reflections provide partial reasoning traces; no machine-readable provenance graph | Heavy token cost; prone to hallucinated reflections; contradictory observations remain in stream | HERM4AI uses deterministic structured states and explicit conflict detection without requiring costly LLM reflection calls |
| **Packer et al. (2023)**<br>*MemGPT: Towards LLMs as Operating Systems*<br>arXiv:2310.08560 | OS-inspired hierarchical memory (main context vs. external disk) with function-calling paging | Working, Archival, Recall | LLM invokes tool calls (`archival_memory_insert`, `edit`); manual paging | Function call logs record paging events | Non-deterministic; relies on LLM prompt discipline; no automated temporal validity intervals | HERM4AI enforces deterministic temporal validity intervals ($[t_{start}, t_{end})$) at the storage engine level |
| **Lewis et al. (2020)**<br>*Retrieval-Augmented Generation for Knowledge-Intensive Tasks*<br>arXiv:2005.11401 | Dense passage retrieval (DPR) coupled with seq2seq generator | Semantic | Index rebuild required for updates; no native notion of fact supersession | Retrieved document IDs provided as input context | Retrieves obsolete documents if semantic overlap is high; cannot detect source contradiction | HERM4AI marks superseded records and suppresses them during current-state queries while retaining historical auditability |
| **Dhingra et al. (2022)**<br>*Time-Aware Language Models as Temporal Knowledge Bases (TempLAMA)*<br>TACL 2022 / arXiv:2106.15110 | Benchmark for probing models on time-varying factual tuples $(s, r, o, [t_1, t_2])$ | Semantic, Temporal | Diagnostic probing; evaluates degradation of factual accuracy over time | N/A (Diagnostic benchmark) | Evaluates parametric knowledge degradation; confirms LLMs fail temporal fact tracking without external time awareness | HERM4AI adopts the temporal tuple formalism $(entity, attribute, value, [t_{start}, t_{end}])$ as a core architectural primitive |
| **Vu et al. (2023)**<br>*FreshLLMs: Refreshing Large Language Models with Search Engine Augmentation (FreshQA)*<br>arXiv:2310.03214 | Evaluates LLMs on fast-changing, slow-changing, and false-premise temporal questions | Semantic, Episodic | Search-engine augmentation at prompt time | Search URLs returned in search results | Standard search often surfaces conflicting or outdated news articles; no stateful reconciliation | HERM4AI maintains an explicit local reconciliation layer that resolves or flags conflicting reports |
| **Meng et al. (2022)**<br>*Locating and Editing Factual Associations in GPT (ROME)*<br>NeurIPS 2022 / arXiv:2202.05262 | Direct rank-one editing of feedforward MLP layers | Parametric Semantic | Overwrites weight matrices for targeted $(s, r, o)$ tuples | Activation tracing locates candidate edit layers | Degrades with sequential edits; non-reversible without checkpoints; no provenance log; GPU intensive | HERM4AI separates memory from weights: memory is external, auditable, and instantly reversible without model retraining |
| **Weston et al. (2015)**<br>*Towards AI-Complete Question Answering: A Set of Prerequisite Toy Tasks (bAbI)*<br>arXiv:1502.05698 | 20 synthetic tasks testing deduction, temporal tracking, path finding, and state changes | Episodic, Working | Step-by-step state changes in synthetic world | Supporting facts tagged in ground truth | Synthetic world state is isolated; lacks real-world source reliability or contradiction handling | HERM4AI adopts synthetic controlled sequences to verify core memory capabilities before deploying complex models |
| **Bohnet et al. (2022)**<br>*Attributed Question Answering: Evaluation and Modeling for Attributed LLMs*<br>arXiv:2212.08037 | Framework requiring models to produce answers alongside verifiable source attributions | Semantic, Provenance | External passage retrieval | Sentence-level attribution to supporting passages | Evaluates post-hoc attribution; models often cite passages that do not strictly entail the answer | HERM4AI produces mechanical, deterministic provenance linking each answer to exact event IDs and timestamped records |

---

## 3. Key Findings & Theoretical Grounding for HERM4AI

1. **Decoupling Memory from Weights is Essential for Auditing and Cost:**
   Parametric editing (ROME/MEMIT) is computationally prohibitive on low-resource hardware (requiring multi-GB GPU VRAM) and lacks transactional safety. Structured external memory can run on a lightweight CPU with zero weight corruption.
2. **Naive RAG Fails Temporal Revision:**
   Without temporal validity intervals, dense and BM25 retrievers treat "Alice lives in London (2021)" and "Alice lives in Tokyo (2024)" as equally relevant to "Where does Alice live?", causing 50% or higher error rates on temporal updates.
3. **Contradiction Must Be an Explicit State, Not an LLM Guess:**
   When Source A and Source B disagree at the same timestamp, standard agents hallucinate one answer or arbitrarily select the top token. An explainable memory system must transition the memory record to `CONFLICTED` and alert the caller.
4. **Provenance Must Be Granular and Append-Only:**
   Explainability requires recording the exact operation (`ENCODE`, `UPDATE`, `CONFLICT`, `DELETE`), the actor/source, the timestamp, and the referenced memory ID in a permanent audit log.
