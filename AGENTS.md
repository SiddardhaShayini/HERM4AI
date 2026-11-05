# Instructions for HERM4AI contributors and agents

Before any project work:

1. Read [PROJECT_MEMORY.md](./PROJECT_MEMORY.md) for the project summary,
   decisions, known gaps, change history, and CPU/RAM limits.
2. Read the relevant sections of [PLAN.md](./PLAN.md) before proposing scope,
   implementation, or experiments.
3. Read [HERM4AI_Doc.md](./HERM4AI_Doc.md) for searchable proposal content.
   Treat [HERM4AI_Doc.docx](./HERM4AI_Doc.docx) as the formatted counterpart;
   verify and keep both copies substantively synchronized after edits.
4. Follow the “What future agents should explore” section in
   `PROJECT_MEMORY.md`, scoped to the current task and next plan gate.
5. Inspect the current workspace and verify that the memory is still accurate;
   do not assume files or decisions exist just because an older log mentions
   them.

When finishing work:

- Keep changes within the agreed research scope and the CPU-only, 8 GB RAM
  limits. Never start large downloads, model training, concurrent heavy jobs,
  or unbounded experiments without a documented resource estimate and owner
  approval.
- Record every project change in `PROJECT_MEMORY.md` (related edits may share
  one entry) with the local date/time and UTC offset, changed files, reason,
  validation outcome, resource impact, and follow-up. Record real mistakes and
  lessons learned; do not invent them.
- Update `PLAN.md` when a phase, scope, deliverable, gate, or resource
  assumption changes.
- Preserve failed tests, negative results, and uncertainty. Do not claim a
  check passed unless it was run.
- Do not treat memory provenance traces as complete explanations of hidden
  model reasoning, or human-inspired design as biological equivalence.

---

## GPU Experiment Proposal Protocol (Google Colab / Kaggle)

The project's primary environment is a CPU-only laptop (Intel i5, 8 GB RAM).
However, some experiments — particularly those involving embedding models,
neural memory components, or comparative benchmarks — may eventually require a
GPU. The owner has access to free GPU sessions via **Google Colab** or
**Kaggle Notebooks**.

### When an agent MUST propose a Colab / Kaggle plan before proceeding

An agent MUST pause and write a formal GPU Proposal (see template below)
before attempting any of the following on the local machine:

| Trigger condition | Reason |
|---|---|
| Embedding or encoding with a transformer model (e.g., `sentence-transformers`, `transformers`) | Model weights alone can exceed 1–2 GB |
| Fine-tuning or adapter training of any neural network | GPU memory and compute required; CPU training is unbounded in time |
| Running a benchmark that requires a GPU-accelerated library (e.g., FAISS-GPU, cuML) | Will silently fall back or crash on CPU-only |
| A single experiment is estimated to exceed 10 minutes on CPU | Violates the run-time guardrail; GPU offload needed |
| Dataset exceeds 1,000 records or 4 MB total text | Violates the initial data-size guardrail |
| Any workload that pushes available system RAM below 2 GB in a dry run | Risk of OOM on the laptop |
| Installing a dependency whose footprint alone exceeds 500 MB | Threatens disk and RAM budget |

### GPU Proposal format

When a trigger condition is met, the agent MUST output a proposal in this
exact format before writing any code or making any changes:

```
## GPU Experiment Proposal — <short title>

**Platform recommended:** Google Colab [Free T4] | Kaggle [P100/T4] | Either
**Trigger:** <which condition above was met and measured estimate>
**Experiment goal:** <one sentence>
**What runs locally first (CPU pre-flight):**
  - [ ] <step 1 — e.g., generate synthetic dataset, verify schema>
  - [ ] <step 2 — e.g., run stateless baseline, confirm it finishes in < 2 min>
**What runs on GPU (Colab / Kaggle notebook):**
  - [ ] <step 1 — e.g., encode 1,000 records with sentence-transformers>
  - [ ] <step 2 — e.g., evaluate retrieval accuracy>
**Estimated GPU session time:** < X minutes (justify)
**Estimated Colab / Kaggle RAM needed:** < Y GB
**Free-tier fit:** Yes / No — reason
**Data privacy check:** synthetic / public-domain / [requires owner review]
**Notebook filename to create:** notebooks/<snake_case_name>.ipynb
**Owner approval required before running:** Yes (default) / No — only if
  purely synthetic data and < 5 min session
```

The owner reviews the proposal and either approves, modifies, or rejects it.
Do not write the notebook or run code until the proposal is approved.

### After approval — notebook hygiene rules

Once approved, the agent creates the notebook under `notebooks/` and follows
these rules:

1. **Cell 0 — environment check:** `import platform, psutil` and print GPU
   info (`!nvidia-smi`) so the session type is recorded in the notebook output.
2. **Cell 1 — install only pinned versions:** e.g.,
   `!pip install sentence-transformers==2.7.0 --quiet`. Never `pip install`
   without a version pin.
3. **Data cell:** Upload only synthetic or approved-public data. Never paste
   real user conversations or sensitive text into a Colab / Kaggle cell.
4. **Checkpoint cell:** Save intermediate results to `/content/drive/` (Colab)
   or `/kaggle/working/` (Kaggle) so they survive a session reset.
5. **Results cell:** Print a concise summary table (approach, metric, value)
   that can be copy-pasted into `PROJECT_MEMORY.md`.
6. **Teardown cell:** Delete temporary files; do not leave model weights in the
   session storage after the experiment ends.
7. After the session, download the `.ipynb` output and commit it under
   `notebooks/` in the workspace. Update `PROJECT_MEMORY.md` with the results.

### Platform selection guidance

| Criterion | Prefer Colab | Prefer Kaggle |
|---|---|---|
| Need Google Drive mount for data | Yes | — |
| Need > 12 GB GPU RAM | Use Colab Pro (paid) | Kaggle P100 (30 h/wk free) |
| Reproducible public notebook | — | Yes (Kaggle has version history) |
| Quick one-off experiment (< 90 min) | Yes | — |
| Longer training run (< 9 h) | — | Yes (Kaggle allows up to 9 h/session) |
| Privacy: data must stay private | Yes (Drive) | Yes (private dataset) |

Default to **Google Colab Free Tier (T4 GPU)** for the first GPU experiment
unless the session time estimate exceeds 90 minutes, in which case prefer
**Kaggle (P100, up to 9 h/session)**.

### What agents must NOT do without a proposal

- Install `torch`, `tensorflow`, `transformers`, `sentence-transformers`,
  `faiss-gpu`, or any GPU-accelerated package on the local machine without
  owner approval and a measured resource pre-check.
- Download model weights (e.g., from Hugging Face Hub) without a documented
  size estimate and approval.
- Run any experiment loop without a timeout. The local guardrail is 10 minutes;
  Colab/Kaggle sessions should have a cell-level timeout guard too.
- Treat a successful Colab/Kaggle run as proof the experiment works on the
  local laptop — always note which environment was used in `PROJECT_MEMORY.md`.
