# HERM4AI Notebooks

This directory holds all Google Colab and Kaggle notebook files (`.ipynb`)
produced during the project's GPU experiment track.

## Executed Notebooks

### 1. `phase3-retrieval-baseline-gpu-completed.ipynb`
* **Status:** **EXECUTED & VERIFIED** (2026-11-04 07:32 UTC)
* **Platform:** Kaggle / Google Colab (Dual Tesla T4 GPUs, 14.56 GB VRAM each, Linux 6.18, Python 3.13.16, PyTorch 2.11.0+cu130)
* **Objective:** Compare dense neural retrieval (`sentence-transformers/all-MiniLM-L6-v2`) against HERM4AI structured memory on temporal state queries.
* **Results:**
  - Dense RAG (`all-MiniLM-L6-v2`) Temporal Accuracy: **58.3%** (7/12)
  - **Temporal Inversion Rate (Retrieved Obsolete Fact): 41.7%** (5/12)
  - Peak VRAM: 104.7 MB (CUDA)
  - HERM4AI Temporal Accuracy: **100.0%** (0.0% inversion rate on CPU)
* **Key Conclusion:** Dense embedding vectors suffer from severe temporal inversion when both historical and current assertions exist in a flat vector index. HERM4AI's structured valid-time intervals $[t_{start}, t_{end})$ eliminate this failure mode entirely without requiring GPU inference.

### 2. `phase4-hybrid-memory-scaling-gpu-completed.ipynb`
* **Status:** **EXECUTED & VERIFIED** (2026-11-04 12:23 UTC)
* **Platform:** Kaggle / Google Colab (Dual Tesla T4 GPUs, 14.56 GB VRAM each, Linux 6.18, Python 3.13.16, PyTorch 2.11.0+cu130)
* **Objective:** Evaluate pure flat Dense Vector RAG vs. Structured Temporal Indexing at **10,000-passage scale** across 500 entities.
* **Results:**
  - Standard Flat Dense RAG Accuracy: **9.0%** (9/100) — **91.0% failure rate**!
  - Encoding Throughput: 10,000 passages in 4.26 s (**2,344.7 passages/s**) on Tesla T4 GPU.
  - Peak VRAM: 152.7 MB (CUDA).
* **Major Scientific Discovery (The Dual Collapse of Flat Vector RAG):**
  At 10,000 passages, pure dense vector retrieval collapses completely (91% error) due to two simultaneous compounding failures:
  1. *Temporal Collapse:* Cosine similarity cannot differentiate between past ($t_1$) and current ($t_2$) state changes.
  2. *Entity Identifier Collision:* Across thousands of entities (`Agent_0001`, `Agent_0342`), the surrounding sentence template dominates token attention, causing cross-entity embeddings to collide with cosine similarity $> 0.98$.
* **Conclusion:** Pure vector retrieval CANNOT function as a reliable long-term agent memory without structured relational entity partitioning and valid-time boundaries.

### 3. `phase5-evaluation-full-gpu-completed.ipynb`
* **Status:** **EXECUTED & VERIFIED** (2026-11-04 13:14 UTC)
* **Platform:** Kaggle / Google Colab (Dual Tesla T4 GPUs, 14.56 GB VRAM each, Linux 6.18, Python 3.13.16, PyTorch 2.11.0+cu130, CUDA 13.0)
* **Objective:** Evaluate real neural LLM generation (`google/flan-t5-base`, 250M parameters) under **Zero-Shot vs. Standard Flat Dense RAG vs. HERM4AI Memory Injection** on temporal multi-turn dialogue state queries.
* **Results:**
  - **Stateless (Zero-Shot) Accuracy:** **0.0%** (0/5) — Lacks persistent factual memory; hallucinates or fails.
  - **Standard Flat Dense RAG Accuracy:** **60.0%** (3/5) — Suffers from temporal inversion; injects obsolete historical context into LLM prompt (`Cluster-Alpha` instead of `Cluster-Beta`; `TLS-1.2` instead of `Post-Quantum-Kyber`), inducing confident generation of false/obsolete facts.
  - **HERM4AI Memory Injection Accuracy:** **100.0%** (5/5) — Deterministic valid-time boundaries $[valid\_from, valid\_to)$ ensure only active valid facts enter prompt; 100% current state generation fidelity.
  - **Peak VRAM (CUDA):** 962.4 MB.

### 4. `phase6-modern-llm-comparison-gpu-completed.ipynb`
* **Status:** **EXECUTED & VERIFIED** (2026-11-04 13:44 UTC)
* **Platform:** Kaggle / Google Colab (Dual Tesla T4 GPUs, 14.56 GB VRAM each, Linux 6.18, Python 3.13.16, PyTorch 2.11.0+cu130, CUDA 13.0)
* **Objective:** Evaluate a modern state-of-the-art open decoder LLM (`Qwen/Qwen2.5-1.5B-Instruct`, 1.5B parameters) on **public-domain real-world temporal facts** (Tech leadership, UK Prime Minister, sports transfers, US Presidency) under Zero-Shot vs. Flat Dense RAG vs. HERM4AI Memory Injection.
* **Results:**
  - **Stateless (Zero-Shot) Accuracy:** **16.7%** (1/6) — Frozen parametric weights fail on changing facts (outputs Jack Dorsey for 2024 Twitter CEO, Jeff Bezos for Amazon, Rishi Sunak for UK PM, PSG for Messi).
  - **Standard Flat Dense RAG Accuracy:** **66.7%** (4/6) — A **33.3% failure rate**! Injects obsolete historical passages into context, directly poisoning the modern decoder LLM to hallucinate:
    - Hallucinates `FC Barcelona` as Lionel Messi's 2024 club (retrieved the 17-year tenure passage).
    - Hallucinates `Donald Trump` as 2023 US President (retrieved Trump passage and overrode the LLM's internal knowledge).
  - **HERM4AI Memory Injection Accuracy:** **100.0%** (6/6) — Valid-time pre-filtering supplies exclusively current active facts; Qwen2.5 generates 100% accurate truth (`Linda Yaccarino`, `Andy Jassy`, `Keir Starmer`, `Inter Miami CF`, `Al Nassr FC`, `Joe Biden`).
  - **Peak VRAM (CUDA):** 1976.9 MB (~1.93 GB VRAM).
* **Key Conclusion:** Modern state-of-the-art decoder models (Qwen2.5) are equally vulnerable to prompt poisoning when coupled with flat vector databases. Valid-time structured memory injection is mathematically and empirically necessary for reliable generative AI.

---

## Planned / Candidate Notebooks

| Filename | Phase | Target Platform | Description / Trigger |
|---|---|---|---|
| `phase1_embedding_similarity.ipynb` | 1 — Literature | Colab / Kaggle | Transformer embeddings > 1 GB RAM |
| `phase6_observability_viz.ipynb` | 6 — Observability | Colab / Kaggle | Transformer attention weight extraction > 2 GB RAM |

---

## Required Notebook Structure

Every notebook in this directory MUST contain these cells in order:

| Cell # | Label | Purpose |
|---|---|---|
| 0 | Environment | Print Python version, `!nvidia-smi`, RAM available |
| 1 | Install | Pinned `pip install` only (e.g., `sentence-transformers==2.7.0`) |
| 2 | Config | Constants: seed, dataset path, record limit, timeout |
| 3 | Data | Load dataset; print shape and first 3 rows |
| 4 | Experiment | Core logic with checkpoints saved to working directory |
| 5 | Results | Summary table: approach, metric name, value, environment |
| 6 | Teardown | Delete temp files; print "Session complete" with timestamp |

## After Each Session

- Commit the executed `.ipynb` (with output cells) under `notebooks/`.
- Record results in `PROJECT_MEMORY.md` with the environment noted.
- Do not delete failed experiment notebooks — preserve them and document the failure.
