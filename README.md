# HERM4AI: Human-like Evolving & Reasoning Memory for Artificial Intelligence

[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23978209.svg)](https://zenodo.org/records/23978209)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/tests-36%20passed%20%280.11s%29-brightgreen.svg)]()
[![Hardware: CPU-first](https://img.shields.io/badge/hardware-CPU--friendly%20%28%3C6MB%20RAM%29-orange.svg)]()

> **Published Research Paper:**  
> **"Beyond Flat Vector Retrieval: Mitigating the Dual Collapse and In-Context Prompt Poisoning of RAG via Structured Valid-Time Cognitive Architectures"**  
> Read on Zenodo: [https://zenodo.org/records/23978209](https://zenodo.org/records/23978209)  
> DOI: [10.5281/zenodo.23978209](https://doi.org/10.5281/zenodo.23978209)

---

## 📌 Executive Overview

Retrieval-Augmented Generation (RAG) is the dominant architecture for grounding Large Language Models (LLMs) in non-parametric knowledge bases. However, standard flat vector retrieval operates on a flawed assumption: **that spatial semantic proximity is a reliable proxy for factual validity in time.**

**HERM4AI** (*Human-like Evolving & Reasoning Memory for Artificial Intelligence*) is an open-source, model-free cognitive architecture designed to solve the temporal and scale limitations of flat vector RAG. Grounded in principles from cognitive science, HERM4AI provides deterministic valid-time state tracking, bounded working memory, associative multi-hop graph reasoning, offline sleep consolidation, and procedural self-healing without requiring continuous neural fine-tuning.

---

## 🔬 Systemic Failure Modes of Flat Vector RAG

Our research identifies and empirically proves three critical failure modes in standard dense vector retrieval:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        RAG DUAL COLLAPSE PIPELINE                      │
│                                                                        │
│  [ Mutable World State ]                                               │
│       │                                                                │
│       ▼                                                                │
│  [ Temporal Inversion ] ──► Encoder ignores time tokens (Δcos < 0.012) │
│       │                     41.7% obsolete retrievals on state shifts  │
│       ▼                                                                │
│  [ Dual Collapse ]     ──► Boilerplate attention mass > 95%            │
│       │                     Cos-sim > 0.98 across unrelated entities   │
│       │                     Top-1 precision collapses to 9.0% at 10k   │
│       ▼                                                                │
│  [ Prompt Poisoning ]  ──► LLM conditioned on stale in-context fact    │
│                             Overrides parametric priors (33.3% - 40%)  │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Temporal Inversion (41.7% Error Rate):**  
   Bi-encoders (e.g., `all-MiniLM-L6-v2`) pool representations across whole sequences. When an entity undergoes state changes (e.g., leadership or team transfers), historical ($t_1$) and current ($t_2$) assertions share nearly identical vocabulary. Consequently, cosine similarities are indistinguishable ($\Delta \simcos < 0.012$), causing retrievers to return obsolete facts in 41.7% of state transitions.
2. **The Dual Collapse Phenomenon (9.0% Accuracy at 10k Scale):**  
   At enterprise scale (10,000 passages across 500 entities sharing repetitive syntax templates), entity identifier tokens attract less than 5% of self-attention weight ($\alpha_{\text{entity}} < 0.05$). The embeddings collide ($\simcos > 0.98$), degrading top-1 retrieval to 9.0% (a 91.0% failure rate).
3. **In-Context Prompt Poisoning (33.3% – 40.0% Downstream LLM Hallucination):**  
   Modern instruction-tuned decoders (such as `Qwen2.5-1.5B-Instruct` or `flan-t5-base`) are aligned via RLHF to prioritize in-context evidence over parametric knowledge. When flat RAG surfaces an obsolete record, the model actively suppresses its own correct internal knowledge and hallucinated outdated claims (e.g., stating Donald Trump is the 2023 US President or FC Barcelona is Messi's 2024 club).

---

## 🧠 The HERM4AI Architecture

HERM4AI replaces unstructured dense retrieval with a multi-tier cognitive memory architecture:

```
               ┌──────────────────────────────┐
               │     Agent Query / Update     │
               └──────────────┬───────────────┘
                              ▼
        ┌───────────────────────────────────────────┐
        │       Valid-Time Declarative Store        │
        │ [t_from, t_to)  σ ∈ {ACTIVE, SUPERSEDED}  │
        └─────────────────────┬─────────────────────┘
                              ▼
        ┌───────────────────────────────────────────┐
        │       7-Slot Working Memory Buffer        │
        │    Salience Eviction: argmin S_i(t)       │
        └─────────────────────┬─────────────────────┘
                              ▼
        ┌───────────────────────────────────────────┐
        │        Associative Knowledge Graph        │
        │       Spreading Activation (γ = 0.5)      │
        └───────┬───────────────────────────┬───────┘
                │ (async)                   │ (async)
                ▼                           ▼
  ┌───────────────────────────┐   ┌───────────────────────────┐
  │   Sleep-Phase Synaptic    │   │     ACT-R Procedural      │
  │       Consolidation       │   │    Conflict Arbitration   │
  └─────────────┬─────────────┘   └─────────────┬─────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
        ┌───────────────────────────────────────────┐
        │      Answer + Q-MIA Provenance Trace      │
        └───────────────────────────────────────────┘
```

- **Deterministic Valid-Time Intervals:**  
  Every assertion is stored as an immutable tuple $\mathcal{M}_i = \langle \text{id}_i, e_i, a_i, v_i, t_{\text{from}}, t_{\text{to}}, s_i, c_i, \sigma_i \rangle$. Queries at $t_q$ strictly evaluate active records where $t_{\text{from}} \le t_q < t_{\text{to}}$, eliminating temporal ambiguity in $O(1)$ time.
- **7-Slot Working Memory Buffer (Miller's Law):**  
  Maintains active context with exponential salience decay $S_i(t) = S_0 e^{-\lambda \Delta t} + \beta \log(1 + c_{\text{access}})$. Least salient inactive items are evicted to long-term storage when capacity is reached.
- **Associative Knowledge Graph:**  
  Models entities and directed relations with synaptic weights. Multi-hop relational queries resolve via spreading activation ($A_v^{(h+1)} = \max_u [A_u^{(h)} \cdot w_{uv} \cdot \gamma]$) in **0.046 ms** on CPU.
- **Sleep-Phase Synaptic Consolidation (CLS Theory):**  
  Background idle replay promotes stable episodic facts to durable semantic tiers ($\lambda = 0.01$), compacts superseded records older than 30 days, strengthens co-activated graph edges via Hebbian plasticity, and prunes weak associations.
- **ACT-R Procedural Arbitration:**  
  Condition-action rules resolve contradictory multi-source claims with utility tracked via Exponential Moving Average (EMA).
- **Counterfactual Attribution (Q-MIA):**  
  Computes exact causal influence $\mathcal{I}(m_i \mid q) = \mathbb{I}[\mathcal{F}(\mathcal{M} \setminus \{m_i\}, q) \ne \mathcal{F}(\mathcal{M}, q)]$, providing audit-grade event provenance for every decision.

---

## 📊 Empirical Evaluation & Benchmark Results

### 1. Comprehensive Benchmark Suite (Local CPU Execution)

All benchmarks run locally on an Intel Core i5 CPU (8 GB RAM):

| Benchmark Suite | Focus Area | Stateless | BM25 RAG | Dense RAG (T4 GPU) | HERM4AI | Latency (CPU) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **TFSR-Bench (Held-Out)** | 60 cases: Recall, Revision, Conflict, Unknown, Deletion | 20.0% | 20.0% | 58.3% | **100.0%** | **0.065 ms** | ✅ PASS |
| **AG-Bench** | Multi-hop graph relational reasoning (1-, 2-, 3-hop) | 0.0% | 33.3% | 33.3% | **100.0%** | **0.046 ms** | ✅ PASS |
| **MultiSessionBench** | 90-day multi-session conversational recall & revision | 0.0% | 50.0% | 50.0% | **100.0%** | **0.110 ms** | ✅ PASS |
| **ExplainBench** | Causal attribution & Q-MIA counterfactual audit | 0.0% | 0.0% | 0.0% | **100.0%** | **0.190 ms** | ✅ PASS |
| **ReplayBench** | Offline sleep consolidation & historical compaction | — | — | — | **100.0%** | **1.380 ms** | ✅ PASS |
| **ProcBench** | ACT-R procedural conflict resolution & self-healing | 0.0% | 0.0% | 0.0% | **100.0%** | **0.261 ms** | ✅ PASS |
| **Real-World Benchmark** | 12 real-world temporal entities (TempLAMA/FreshQA tasks) | 8.3% | 8.3% | 66.7% | **100.0%** | **1.850 ms** | ✅ PASS |

---

### 2. Enterprise Scaling Experiment (10,000 Passages, Dual Tesla T4 GPUs)

| Architecture | Scale | Top-1 Query Precision | Throughput | Peak VRAM |
| :--- | :---: | :---: | :---: | :---: |
| **Flat Dense RAG** (`all-MiniLM-L6-v2` + FAISS) | 10,000 passages | **9.0%** (*Dual Collapse*) | 2,344.7 passages/s | 152.7 MB |
| **HERM4AI Structured Store** | 10,000 records | **100.0%** (*Stable*) | 233.9 ops/s (CPU) | **0.0 MB** |

---

### 3. Downstream Generative LLM Evaluation (Dual Tesla T4 GPUs)

Evaluating the impact of retrieval on downstream LLM generation:

| Generator Model | Memory Mode | Accuracy | Peak VRAM | Downstream Behavior Observed |
| :--- | :--- | :---: | :---: | :--- |
| **`flan-t5-base`** (250M) | Stateless (Zero-Shot) | 0.0% | 962 MB | Hallucinations; zero factual retention |
| | Flat Dense RAG | 60.0% | 962 MB | **40% Hallucination**: outputs superseded state |
| | **HERM4AI Injection** | **100.0%** | 962 MB | **Zero Hallucination**: 100% current state fidelity |
| **`Qwen2.5-1.5B-Instruct`** (1.5B) | Stateless (Zero-Shot) | 16.7% | 1,977 MB | Pre-training cutoff: outputs Dorsey, Bezos, Sunak |
| | Flat Dense RAG | 66.7% | 1,977 MB | **33.3% Prompt Poisoning**: outputs Trump, FC Barcelona |
| | **HERM4AI Injection** | **100.0%** | 1,977 MB | **100% Ground Truth**: outputs Yaccarino, Jassy, Starmer, Biden |

---

## 🚀 Quickstart & Usage

### 1. Installation

HERM4AI has **zero external neural dependencies** for its core engine. It runs on pure Python 3.10+ standard library and SQLite:

```bash
git clone https://github.com/SiddardhaShayini/HERM4AI.git
cd HERM4AI

# Install development requirements
pip install -r requirements.txt
pip install -e .
```

### 2. Basic Example: Valid-Time Memory & Agent Interaction

```python
from datetime import datetime
from src.herm4ai.engine import HERMMemoryEngine
from src.herm4ai.agent import HERMConversationalAgent

# Initialize engine (in-memory or persistent SQLite)
engine = HERMMemoryEngine(":memory:")

# Store initial historical state (2021)
engine.store(
    entity="twitter_ceo",
    attribute="current_holder",
    value="Parag Agrawal",
    source="corporate_sec_filing",
    confidence=1.0,
    valid_from=datetime(2021, 11, 29)
)

# Ingest an update (2023) — automatically supersedes older record
engine.store(
    entity="twitter_ceo",
    attribute="current_holder",
    value="Linda Yaccarino",
    source="official_press_release",
    confidence=1.0,
    valid_from=datetime(2023, 6, 5)
)

# Query current state at 2024
result = engine.query(
    entity="twitter_ceo",
    attribute="current_holder",
    query_time=datetime(2024, 1, 1)
)

print(f"Result: {result.value}")           # -> Linda Yaccarino
print(f"Status: {result.status.value}")    # -> ACTIVE
print(f"Provenance ID: {result.memory_id}") # Append-only cryptographic trace

# Query historical state as of 2022
past_result = engine.query(
    entity="twitter_ceo",
    attribute="current_holder",
    query_time=datetime(2022, 1, 1)
)
print(f"Past State (2022): {past_result.value}") # -> Parag Agrawal
```

### 3. Running All Tests

Verify the full suite of 36 unit tests in ~0.11 seconds:

```bash
pytest
```

---

## 📁 Repository Structure

```
HERM4AI/
├── src/herm4ai/                  # Core Cognitive Memory Engine
│   ├── engine.py                 # Valid-time declarative memory engine
│   ├── working_memory.py         # 7-slot salience-gated buffer (Miller's Law)
│   ├── agent.py                  # Conversational agent & procedural integration
│   ├── consolidation.py          # Sleep-phase replay & compaction (CLS theory)
│   ├── procedural.py             # ACT-R condition-action production rules
│   ├── explainability.py         # Q-MIA counterfactual attribution engine
│   ├── models.py                 # Core data models and memory enums
│   ├── baselines.py              # BM25 & Stateless reference implementations
│   ├── dashboard.py              # Observability dashboard generator
│   └── evaluator.py              # Benchmark evaluation harness
├── tests/                        # 36 Unit Tests (100% Passing)
├── scripts/                      # Reproducible benchmark & evaluation runners
│   ├── run_realworld_benchmark.py
│   ├── run_consolidation_benchmark.py
│   ├── run_procedural_benchmark.py
│   ├── run_associative_benchmark.py
│   └── generate_ai_observatory.py
├── data/                         # Benchmark datasets (Synthetic & Real-World)
├── docs/                         # LaTeX manuscript & publication files
│   ├── paper.tex                 # Two-column camera-ready LaTeX source
│   ├── references.bib            # BibTeX references
│   └── Beyond_Flat_Vector_Retrieval...pdf # Published PDF
├── notebooks/                    # Executed GPU Notebooks (Tesla T4)
│   ├── phase3-retrieval-baseline-gpu-completed.ipynb
│   ├── phase4-hybrid-memory-scaling-gpu-completed.ipynb
│   ├── phase5-evaluation-full-gpu-completed.ipynb
│   └── phase6-modern-llm-comparison-gpu-completed.ipynb
├── results/                      # Markdown benchmark reports & observatory HTML
├── pyproject.toml                # Package configuration
├── requirements.txt              # Minimal dependencies
├── CONTRIBUTING.md               # Open source contribution guidelines
├── CODE_OF_CONDUCT.md            # Contributor Covenant Code of Conduct
├── LICENSE                       # MIT License
└── README.md
```

---

## 📓 GPU Notebook Reproducibility

Four dedicated GPU experiment tracks were executed on **Dual Tesla T4 GPUs (16 GB VRAM each)** via Kaggle/Google Colab:

1. **`phase3-retrieval-baseline-gpu-completed.ipynb`**: Demonstrates 41.7% Temporal Inversion in dense bi-encoders (`all-MiniLM-L6-v2`).
2. **`phase4-hybrid-memory-scaling-gpu-completed.ipynb`**: Proves the Dual Collapse Phenomenon at 10,000 passages (collapsing to 9.0% accuracy).
3. **`phase5-evaluation-full-gpu-completed.ipynb`**: Evaluates encoder-decoder generation (`flan-t5-base`) showing 40% hallucination elimination.
4. **`phase6-modern-llm-comparison-gpu-completed.ipynb`**: Evaluates modern open decoders (`Qwen2.5-1.5B-Instruct`) proving elimination of In-Context Prompt Poisoning on real-world entities.

All notebooks are archived with full execution logs under [`notebooks/`](./notebooks/).

---

## 📜 Citation

If you find HERM4AI useful in your research or applications, please cite our paper:

```bibtex
@article{shayini2026beyond,
  author    = {Shayini Siddardha},
  title     = {Beyond Flat Vector Retrieval: Mitigating the Dual Collapse and In-Context Prompt Poisoning of RAG via Structured Valid-Time Cognitive Architectures},
  journal   = {Zenodo Preprint},
  year      = {2026},
  month     = {November},
  doi       = {10.5281/zenodo.23978209},
  url       = {https://zenodo.org/records/23978209}
}
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

## Developer

**Siddardha Shayini**  
GitHub: [https://github.com/SiddardhaShayini](https://github.com/SiddardhaShayini)
