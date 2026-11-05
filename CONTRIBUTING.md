# Contributing to HERM4AI

Thank you for your interest in contributing to **HERM4AI** (*Human-like Evolving & Reasoning Memory for Artificial Intelligence*)! We welcome contributions from researchers, software engineers, and cognitive scientists.

---

## 1. Code of Conduct

All contributors are expected to uphold our [Code of Conduct](./CODE_OF_CONDUCT.md). Please report any unacceptable behavior to `shayinisiddardha3@gmail.com`.

---

## 2. Core Architectural Principles

Before contributing code, please keep the foundational design principles of HERM4AI in mind:

1. **Model-Free & Lightweight Core:**  
   The core memory engine operates without requiring large neural weights, heavy embeddings, or continuous gradient updates. It runs efficiently on commodity CPUs with minimal RAM (< 6 MB).
2. **Deterministic Valid-Time Semantics:**  
   Assertions are stored with half-open validity intervals $[t_{\text{from}}, t_{\text{to}})$. Factual currency is determined by temporal interval predicates, not fuzzy cosine similarity heuristics.
3. **Cognitive Grounding:**  
   Component designs are inspired by established cognitive science:
   - 7-slot working memory with salience decay (Miller's Law)
   - Sleep-phase episodic-to-semantic consolidation (Complementary Learning Systems theory)
   - ACT-R condition-action production rules for conflict arbitration
   - Hebbian synaptic potentiation and spreading activation
4. **Transparent & Causal Provenance:**  
   Every retrieved assertion must be attributable with exact causal influence via counterfactual scoring (Q-MIA) and append-only event ledgers. We distinguish storage-level provenance from claims of neural model interpretability.

---

## 3. Development Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### Installation
Clone the repository and install the development dependencies:

```bash
git clone https://github.com/SiddardhaShayini/HERM4AI.git
cd HERM4AI

# Create and activate a virtual environment
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies and editable package
pip install -r requirements.txt
pip install -e .
```

---

## 4. Running Tests & Benchmarks

### Unit Tests
The test suite covers memory lifecycle, working memory salience, associative spreading activation, sleep consolidation, procedural execution, and explainability.

Run tests using `pytest`:

```bash
python -m pytest tests/
```

All 36 unit tests should pass in under a quarter of a second (~0.12s on standard CPUs).

### Running Benchmarks
To run the automated benchmark suites:

```bash
# Real-world temporal factuality benchmark
python scripts/run_realworld_benchmark.py

# Sleep-phase consolidation benchmark
python scripts/run_consolidation_benchmark.py

# ACT-R procedural conflict arbitration benchmark
python scripts/run_procedural_benchmark.py

# Associative graph benchmark
python scripts/run_associative_benchmark.py

# Generate interactive AI Observatory dashboard
python scripts/generate_ai_observatory.py
```

Generated reports are saved in `results/`.

---

## 5. Development Workflow

1. **Fork & Branch:** Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Write Tests:** Add unit tests in `tests/` for any new functionality or bug fixes.
3. **Maintain Resource Efficiency:** Avoid adding dependencies that introduce heavy neural models or unconstrained memory footprints into the core package (`src/herm4ai/`).
4. **Run Test Suite:** Verify that `python -m pytest tests/` passes cleanly.
5. **Commit Cleanly:** Write concise, descriptive commit messages:
   ```bash
   git commit -m "feat(working_memory): optimize salience decay calculation"
   ```
6. **Open a Pull Request:** Push to your fork and submit a Pull Request against the `main` branch. Provide a clear summary of changes, motivation, and test verification output.

---

## 6. Questions & Discussions

If you have questions about the paper, architecture, or benchmark results:
- Open an [Issue on GitHub](https://github.com/SiddardhaShayini/HERM4AI/issues)
- Read the published paper on [Zenodo](https://zenodo.org/records/23978209)
- Email maintainer: `shayinisiddardha3@gmail.com`
