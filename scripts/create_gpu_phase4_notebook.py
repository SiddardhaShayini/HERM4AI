"""
Script: scripts/create_gpu_phase4_notebook.py
Generates notebooks/phase4_hybrid_memory_scaling_gpu.ipynb adhering strictly
to the 7-cell hygiene protocol in AGENTS.md and PLAN.md.
"""

import json
from pathlib import Path


def create_phase4_gpu_notebook():
    notebook_dict = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# HERM4AI — Phase 4: Large-Scale Hybrid Memory Scaling Benchmark (10,000 Records)\n",
                    "**Platform:** Google Colab [Free T4] / Kaggle Notebooks [P100/T4]\n",
                    "**Research Objective:** Evaluate a Hybrid Cognitive Architecture combining Dense Neural Embeddings (`all-MiniLM-L6-v2`) for fuzzy semantic text search with HERM4AI Structured Valid-Time Boundaries $[valid\\_from, valid\\_to)$ to completely eliminate the 41.7% temporal inversion failure at 10,000-record scale."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 0 — Environment and Hardware Check\n",
                    "import platform\n",
                    "import psutil\n",
                    "import os\n",
                    "\n",
                    "print(f\"Python Version : {platform.python_version()}\")\n",
                    "print(f\"OS Platform    : {platform.system()} {platform.release()}\")\n",
                    "print(f\"Total Host RAM : {psutil.virtual_memory().total / (1024**3):.2f} GB\")\n",
                    "print(f\"Available RAM  : {psutil.virtual_memory().available / (1024**3):.2f} GB\")\n",
                    "\n",
                    "try:\n",
                    "    import torch\n",
                    "    print(f\"CUDA Available : {torch.cuda.is_available()}\")\n",
                    "    if torch.cuda.is_available():\n",
                    "        print(f\"Device Name    : {torch.cuda.get_device_name(0)}\")\n",
                    "        print(f\"Device VRAM    : {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB\")\n",
                    "except ImportError:\n",
                    "    print(\"PyTorch not yet imported.\")\n",
                    "\n",
                    "!nvidia-smi"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 1 — Pinned Dependency Installation\n",
                    "# Pinned versions; faiss-cpu>=1.9.0 for Python 3.13 compatibility\n",
                    "!pip install sentence-transformers==2.7.0 \"faiss-cpu>=1.9.0\" --quiet\n",
                    "print(\"Dependencies installed successfully.\")"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 2 — Experiment Configuration\n",
                    "SEED = 42\n",
                    "MODEL_NAME = \"sentence-transformers/all-MiniLM-L6-v2\"\n",
                    "TOTAL_PASSAGES = 10000\n",
                    "BATCH_SIZE = 128\n",
                    "\n",
                    "import random\n",
                    "import numpy as np\n",
                    "import torch\n",
                    "\n",
                    "random.seed(SEED)\n",
                    "np.random.seed(SEED)\n",
                    "torch.manual_seed(SEED)\n",
                    "if torch.cuda.is_available():\n",
                    "    torch.cuda.manual_seed_all(SEED)\n",
                    "\n",
                    "print(f\"Configured scale N = {TOTAL_PASSAGES} passages, model = '{MODEL_NAME}'\")"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 3 — Synthetic Data Generation (10,000 Unstructured Passages with Temporal Revisions)\n",
                    "entities = [f\"Agent_{i:04d}\" for i in range(500)]\n",
                    "attributes = [\"assignment\", \"security_tier\", \"current_jurisdiction\", \"project_role\"]\n",
                    "cities = [\"Geneva\", \"Tokyo\", \"Nairobi\", \"Reykjavik\", \"Singapore\", \"Toronto\", \"Berlin\", \"Austin\"]\n",
                    "\n",
                    "passages = []\n",
                    "metadata = []\n",
                    "test_queries = []\n",
                    "\n",
                    "for i in range(TOTAL_PASSAGES // 2):\n",
                    "    ent = entities[i % len(entities)]\n",
                    "    attr = attributes[i % len(attributes)]\n",
                    "    c_old, c_new = random.sample(cities, 2)\n",
                    "    \n",
                    "    # Old passage at t1\n",
                    "    p_old = f\"{ent}'s official {attr.replace('_', ' ')} was verified as {c_old} on 2024-01-10.\"\n",
                    "    passages.append(p_old)\n",
                    "    metadata.append({\"entity\": ent, \"attribute\": attr, \"val\": c_old, \"status\": \"SUPERSEDED\", \"valid_from\": \"2024-01-10\", \"valid_to\": \"2024-05-20\"})\n",
                    "    \n",
                    "    # New passage at t2\n",
                    "    p_new = f\"{ent}'s official {attr.replace('_', ' ')} was formally transitioned to {c_new} on 2024-05-20.\"\n",
                    "    passages.append(p_new)\n",
                    "    metadata.append({\"entity\": ent, \"attribute\": attr, \"val\": c_new, \"status\": \"ACTIVE\", \"valid_from\": \"2024-05-20\", \"valid_to\": None})\n",
                    "    \n",
                    "    if len(test_queries) < 100:\n",
                    "        test_queries.append({\n",
                    "            \"query\": f\"What is the current {attr.replace('_', ' ')} of {ent}?\",\n",
                    "            \"entity\": ent,\n",
                    "            \"attribute\": attr,\n",
                    "            \"expected_current\": c_new\n",
                    "        })\n",
                    "\n",
                    "print(f\"Generated {len(passages)} passages across {len(entities)} entities.\")\n",
                    "print(f\"Sample Passage 0: {passages[0]}\")\n",
                    "print(f\"Sample Passage 1: {passages[1]}\")"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 4 — Hybrid Retrieval Execution\n",
                    "# Compares Standard Dense Vector RAG vs HERM4AI Hybrid Retrieval (Dense Vector + Structured Temporal Filter)\n",
                    "import time\n",
                    "from sentence_transformers import SentenceTransformer\n",
                    "\n",
                    "device = \"cuda\" if torch.cuda.is_available() else \"cpu\"\n",
                    "print(f\"Loading {MODEL_NAME} onto {device}...\")\n",
                    "embedder = SentenceTransformer(MODEL_NAME, device=device)\n",
                    "\n",
                    "t0_enc = time.perf_counter()\n",
                    "corpus_embeddings = embedder.encode(passages, batch_size=BATCH_SIZE, show_progress_bar=True, normalize_embeddings=True)\n",
                    "t_enc = time.perf_counter() - t0_enc\n",
                    "print(f\"Encoded {len(passages)} passages in {t_enc:.2f} s ({len(passages)/t_enc:.1f} passages/s).\")\n",
                    "\n",
                    "# Encode queries\n",
                    "query_texts = [q[\"query\"] for q in test_queries]\n",
                    "query_embeddings = embedder.encode(query_texts, batch_size=BATCH_SIZE, normalize_embeddings=True)\n",
                    "\n",
                    "# 1. Standard Flat Dense RAG (No Temporal Indexing)\n",
                    "flat_rag_correct = 0\n",
                    "# 2. HERM4AI Hybrid (Dense Semantic Search with Active Temporal Validity Mask)\n",
                    "hybrid_correct = 0\n",
                    "\n",
                    "for idx, q_emb in enumerate(query_embeddings):\n",
                    "    sims = np.dot(corpus_embeddings, q_emb)\n",
                    "    \n",
                    "    # Flat RAG: Picks top-1 global similarity\n",
                    "    top_flat_idx = int(np.argmax(sims))\n",
                    "    if metadata[top_flat_idx][\"val\"] == test_queries[idx][\"expected_current\"]:\n",
                    "        flat_rag_correct += 1\n",
                    "        \n",
                    "    # HERM4AI Hybrid: Masks out superseded records (valid_to is not None) before argmax\n",
                    "    active_mask = np.array([m[\"status\"] == \"ACTIVE\" for m in metadata])\n",
                    "    masked_sims = np.where(active_mask, sims, -1.0)\n",
                    "    top_hybrid_idx = int(np.argmax(masked_sims))\n",
                    "    if metadata[top_hybrid_idx][\"val\"] == test_queries[idx][\"expected_current\"]:\n",
                    "        hybrid_correct += 1\n",
                    "\n",
                    "n_q = len(test_queries)\n",
                    "print(f\"\\nEvaluation completed on {n_q} test queries across 10,000 passages:\")\n",
                    "print(f\"  Standard Flat Dense RAG Accuracy : {flat_rag_correct}/{n_q} ({flat_rag_correct/n_q*100:.1f}%)\")\n",
                    "print(f\"  HERM4AI Hybrid Memory Accuracy   : {hybrid_correct}/{n_q} ({hybrid_correct/n_q*100:.1f}%)\")"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 5 — Results Summary Table\n",
                    "import pandas as pd\n",
                    "\n",
                    "peak_vram_mb = torch.cuda.max_memory_allocated() / (1024**2) if torch.cuda.is_available() else 0.0\n",
                    "\n",
                    "summary_data = [\n",
                    "    {\"Architecture\": \"Standard Flat Dense RAG\", \"Passage Count\": TOTAL_PASSAGES, \"Accuracy\": f\"{flat_rag_correct/n_q*100:.1f}%\", \"Temporal Inversion Rate\": f\"{(n_q - flat_rag_correct)/n_q*100:.1f}%\", \"Peak VRAM\": f\"{peak_vram_mb:.1f} MB\"},\n",
                    "    {\"Architecture\": \"HERM4AI Hybrid Memory\", \"Passage Count\": TOTAL_PASSAGES, \"Accuracy\": f\"{hybrid_correct/n_q*100:.1f}%\", \"Temporal Inversion Rate\": f\"{(n_q - hybrid_correct)/n_q*100:.1f}%\", \"Peak VRAM\": f\"{peak_vram_mb:.1f} MB\"}\n",
                    "]\n",
                    "\n",
                    "df = pd.DataFrame(summary_data)\n",
                    "print(\"=== HYBRID SCALING EXPERIMENT RESULTS ===\")\n",
                    "display(df) if 'display' in globals() else print(df.to_string())"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Cell 6 — Teardown and Cleanup\n",
                    "import gc\n",
                    "import datetime\n",
                    "\n",
                    "del embedder\n",
                    "del corpus_embeddings\n",
                    "del query_embeddings\n",
                    "gc.collect()\n",
                    "if torch.cuda.is_available():\n",
                    "    torch.cuda.empty_cache()\n",
                    "\n",
                    "print(f\"Teardown complete at: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\")"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    out_file = Path("notebooks/phase4_hybrid_memory_scaling_gpu.ipynb")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(notebook_dict, f, indent=2)

    print(f"Generated Phase 4 GPU notebook -> {out_file}")


if __name__ == "__main__":
    create_phase4_gpu_notebook()
