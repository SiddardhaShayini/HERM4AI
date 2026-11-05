# HERM4AI Research Protocol & Evaluation Specification
*Phase 2 Deliverable — Operational Definitions, Metrics, and Benchmark Protocol*
*Date: 2026-11-04*

---

## 1. Problem Formulation & Operational Definitions

Let an operational environment provide a time-ordered stream of factual assertions $\mathcal{S} = \{e_1, e_2, \dots, e_T\}$. Each assertion is formalized as a tuple:

$$e_t = \langle \text{entity}, \text{attribute}, \text{value}, t, \text{source}, \text{confidence} \rangle$$

The memory engine maintains an internal state $\mathcal{M}$ over time. Given a natural language or structured query $q$ at query time $t_q$, the system must return:
1. The predicted answer value $\hat{y}$.
2. The operational status $\sigma \in \{\text{ACTIVE}, \text{SUPERSEDED}, \text{CONFLICTED}, \text{UNKNOWN}, \text{DELETED}\}$.
3. A verifiable provenance trace $\mathcal{P} = \{\text{event\_ids}, \text{sources}, \text{timestamps}\}$.

### Operational Definitions

- **Active Memory:** A factual association that is currently valid, uncontradicted, and undeleted.
- **Superseded Memory:** An earlier factual assertion whose $(entity, attribute)$ pair has been superseded by a newer assertion with timestamp $t_2 > t_1$.
- **Conflicted Memory:** Two or more assertions regarding $(entity, attribute)$ at overlapping validity windows with divergent values and differing sources where neither clearly supersedes the other.
- **Tombstone / Deleted Memory:** A record explicitly expunged via user request, retaining an auditable tombstone event without leaking the expunged value.
- **Abstention:** The explicit operational behavior of declining to provide an answer when $\mathcal{M}$ contains no relevant, non-deleted factual assertions.

---

## 2. Benchmark Task: TFSR-Bench (Temporal Fact & State Revision)

The benchmark assesses memory systems across five distinct evaluation axes:

| Axis | Name | Description | Key Failure Mode of Naive Systems |
|---|---|---|---|
| **DR** | Direct Recall | Recall a stable fact after $K$ intervening distractor items | Context overflow, retrieval noise |
| **TR** | Temporal Revision | Query the current state of an entity whose property changed at $t_2 > t_1$ | Retrieves outdated historical fact due to high lexical/semantic overlap |
| **CA** | Conflict Attribution | Query an entity where Source A and Source B disagree at time $t$ | Randomly selects one source; fails to detect contradiction |
| **AU** | Abstention on Unknown | Query an entity or property never introduced in the stream | Hallucinates a plausible value or guesses |
| **TD** | Tombstone & Deletion | Query an entity whose property was explicitly deleted at $t_{del}$ | Leaks deleted data; violates "right to be forgotten" |

---

## 3. Evaluation Metrics

1. **Exact Match Accuracy ($\text{EM}$):**
   $$\text{EM} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}[\hat{y}_i = y_i]$$

2. **Temporal Revision Resolution Rate ($\text{TRRR}$):**
   $$\text{TRRR} = \frac{1}{|\text{TR}|} \sum_{i \in \text{TR}} \mathbf{1}[\hat{y}_i = y_i^* \land \sigma_i = \text{ACTIVE}]$$
   Measures whether the system correctly returns the newest valid value rather than an obsolete predecessor.

3. **Conflict Detection Rate ($\text{CDR}$):**
   $$\text{CDR} = \frac{1}{|\text{CA}|} \sum_{i \in \text{CA}} \mathbf{1}[\sigma_i = \text{CONFLICTED}]$$
   Measures whether contradictions are explicitly flagged rather than suppressed.

4. **Abstention Accuracy ($\text{AA}$):**
   $$\text{AA} = \frac{1}{|\text{AU}|} \sum_{i \in \text{AU}} \mathbf{1}[\sigma_i = \text{UNKNOWN} \land \hat{y}_i = \text{"UNKNOWN"}]$$

5. **Provenance Attribution Coverage ($\text{PAC}$):**
   $$\text{PAC} = \frac{1}{N_{\text{valid}}} \sum_{i=1}^{N_{\text{valid}}} \mathbf{1}[\text{len}(\mathcal{P}_i) > 0 \land \forall p \in \mathcal{P}_i: \text{valid\_event}(p)]$$

6. **Computational Efficiency Guardrails:**
   - Peak Process Memory $\le 50$ MB RAM.
   - Total evaluation latency across benchmark $\le 10.0$ seconds on CPU.
   - Zero GPU requirement; zero network/cloud API call.

---

## 4. Evaluated Systems

1. **Stateless Baseline (`StatelessBaseline`):**
   Maintains zero persistent storage across assertions. Only possesses context from the immediate query turn. Serves as the lower-bound reference.
2. **Naive Retrieval Baseline (`NaiveRetrievalBaseline`):**
   Stores all incoming assertions as unstructured text in an SQLite lexical store. Retrieves top-1 match via BM25/keyword similarity without lifecycle, timestamp, or conflict modeling. Simulates typical naive RAG implementations.
3. **HERM4AI Prototype (`HERMMemoryEngine`):**
   Maintains structured entity-attribute state with temporal intervals, deterministic lifecycle state transitions, conflict detection, tombstone expungement, and append-only provenance auditing.

---

## 5. Predeclared Numerical Success Criteria (Phase 2 Exit Gate)

Before running the held-out evaluation, we lock the following falsifiable hypotheses:

| Metric | Stateless Baseline | Naive Retrieval Baseline | HERM4AI Prototype (Target) |
|---|---|---|---|
| Direct Recall (DR) | $0.0\%$ | $\ge 90.0\%$ | $\ge 95.0\%$ |
| Temporal Revision (TR) | $0.0\%$ | $\le 50.0\%$ (fails on outdated docs) | $\ge 90.0\%$ |
| Conflict Detection (CA) | $0.0\%$ | $0.0\%$ (cannot represent conflicts) | $\mathbf{100.0\%}$ |
| Abstention Accuracy (AU) | $\le 20.0\%$ | $\le 20.0\%$ (returns nearest neighbor) | $\mathbf{100.0\%}$ |
| Deletion Audit (TD) | $0.0\%$ | $0.0\%$ (retains deleted strings) | $\mathbf{100.0\%}$ |
| Provenance Coverage (PAC)| $0.0\%$ | $0.0\%$ | $\mathbf{100.0\%}$ |
| Peak RAM | $< 25$ MB | $< 30$ MB | $< 50$ MB |
| Runtime | $< 1$ s | $< 2$ s | $< 5$ s |
