# Study Plan — Conversational Clustering on the UCDP GEDEvent 25.1 Dataset

**Dataset:** UCDP Georeferenced Event Dataset (GED) v25.1 — filtered to Russia-Ukraine conflict\
**Version:** v0.4

---

## Changelog

| Version | Date | Summary of changes |
| --- | --- | --- |
| v0.1 | 2026-05-13 | Initial draft. Research questions, hypotheses, and scope committed at Sprint 1 start. Methodology and evaluation strategy preliminary. |
| v0.2 | 2026-05-20 | Updated after Sprint 1 completion. EDA findings incorporated: (1) `type_of_violence` and `side_a` dropped from F2 feature set due to near-zero variance (cardinality 2 and 1 respectively); (2) `where_description` embedding decision closed — excluded from feature sets, value over structured geographic features is marginal; (3) `adm_2` added to F2 cautiously given 19.8% null rate — decision documented; (4) geographic concentration finding noted (Donetsk 49.1%) with implication for F1 baseline interpretation; (5) two open questions from v0.1 resolved. Sprint 2 roadmap added. |
| v0.3 | 2026-05-22 | Updated after Sprint 2 execution. (1) Open questions §7 updated: model string, prompt files, and K=8 marked as resolved; experimenter assignment order and rater recruitment still pending. (2) Execution status documented: Conditions A and C fully executed (120 runs, seeds 0–29, all complete). Condition B pending. (3) Preliminary result for H1 (Condition C) added. (4) Model version inconsistency between Condition A and C runs noted and flagged — protocol amendment registered in `docs/study_design.md §12`. (5) Sprint 2 roadmap updated with current completion status. |
| v0.4 | 2026-05-28 | Updated during Condition B execution. (1) §9 execution status updated: B/F2 at 19/30, B/F1 at 3/30, all other conditions complete. (2) Remaining B seeds and per-person assignment documented. (3) New §10 added: results dashboard — a lightweight visualization tool planned to accompany the final analysis. (4) Dataset limitation noted: near-constant `side_a`/`side_b`/`type_of_violence` in the Russia-Ukraine subset reduces F2 effective dimensionality to geography + fatalities only. |

---

## 1. Context and Motivation

The UCDP GEDEvent 25.1 dataset provides structured, georeferenced records of organized violent events in the Russia-Ukraine conflict. Each record encodes event type, actor identities, location (coordinates + administrative divisions), date, and estimated casualties. The dataset has no canonical cluster labels — there is no ground-truth partition of events into meaningful groups. This makes it a suitable testbed for studying whether a conversational clustering system can help a user discover and refine meaningful groupings without manual hyperparameter tuning.

This project sits at the intersection of two questions: (1) does conversational refinement produce better clusters than automated baseline methods on structured conflict event data, and (2) can we evaluate cluster quality cheaply — without expensive human annotation — by using an LLM oracle as a proxy rater?

---

## 2. Research Questions

### Primary — RQ1: Conversational refinement vs. one-shot clustering

> **Does iterative conversational refinement produce measurably better clusters (by internal validity indices) than a single automated clustering run on the GEDEvent data, and does the magnitude of improvement depend on the feature set used to represent events?**

The intuition is that automated clustering on a mixed structured dataset (numeric + categorical + geographic features) is sensitive to feature weighting and distance metric choices that a user cannot easily specify upfront. Conversational refinement provides a channel through which domain knowledge — "separate events by casualty level, not just location" — can be injected incrementally.

### Secondary — RQ2: LLM oracle as proxy for human judgment

> **Do cluster quality rankings produced by an LLM oracle correlate with human rater preferences at ρ &gt; 0.7 (Spearman's rank correlation), making oracle-driven evaluation a viable low-cost substitute for human rating in this setting?**

This is a meta-claim about our evaluation methodology. If the oracle is a valid proxy, it justifies using it to evaluate the many experimental runs that human rating cannot cover at scale. A low correlation is an equally important finding — it would mean oracle-driven evaluation of structured conflict data is unreliable and should not be used without human validation.

---

## 3. Hypotheses

| ID | Type | Statement |
| --- | --- | --- |
| H1 | Confirmatory | Conversational refinement improves the Silhouette score of the final cluster assignment relative to the automated baseline (one-shot k-means on F2 features), with the improvement quantified as a 95% bootstrap CI excluding zero and a one-sided Wilcoxon signed-rank test p &lt; 0.05 over 30 replications. |
| H2 | Exploratory | The improvement from conversational refinement is larger under the full feature set (F2) than under location-only features (F1), suggesting refinement adds most value when the feature space is higher-dimensional. Reported without multiple-comparison correction; labelled exploratory. |
| H3 | Confirmatory | Spearman's ρ between LLM oracle cluster rankings and human rater rankings exceeds 0.7, with bootstrap CI lower bound &gt; 0.5, on a held-out sample of 20 cluster pairs. Cohen's κ ≥ 0.40 is additionally required for H3 to be considered met. |

H1 is the primary confirmatory test. H2 is exploratory and will be reported as such. H3 is confirmatory but depends on recruiting raters; its sample size will be revisited before human rating begins.

---

## 4. Study Design

Full operationalisation is in `docs/study_design.md` (v0.1, pre-registered). Key elements summarised here for orientation.

### 4.1 Conditions

| Condition | Description | Role |
| --- | --- | --- |
| A — Baseline | One-shot k-means on F1 or F2; no iterative refinement. K = 8 fixed. | Primary control |
| B — Conversational (human) | Team member issues up to 5 NL refinement instructions per session; blind to Silhouette score during the session. | Treatment |
| C — Conversational (LLM oracle) | LLM acts as both user and interpreter to simulate many sessions cheaply. | Proxy-validity arm |

30 replications per (condition × feature set) cell, seeds 0–29. Analysis is paired by seed.

### 4.2 Feature Sets

| Level | Features included | EDA notes |
| --- | --- | --- |
| F1 — Location-only | latitude, longitude (continuous, min-max normalised) + adm_1 (one-hot, 26 oblasts, 6.8% nulls handled by dropping column entry) | Clean. Severe geographic concentration (Donetsk 49.1%) will produce one dominant cluster — disclosed as F1 limitation. |
| F2 — Full | F1 + side_b actor identity (one-hot, cardinality 2 after EDA) + best fatality estimate (log(best+1), min-max normalised) | `type_of_violence` dropped (99.2% type 1, near-zero variance). `side_a` dropped (cardinality 1 — always "Government of Russia"). `adm_2` excluded given 19.8% null rate and 128-level cardinality (would dominate one-hot space). `where_description` excluded (median 32 chars; marginal value over structured geographic features per §5.7 of data_provenance.md). |

**Decision log (v0.2 additions):**

- `type_of_violence` excluded from F2: cardinality 2, 99.2% type 1 — near-zero variance column adds noise without signal.
- `side_a` excluded from F2: cardinality 1 throughout filtered subset — constant column, no clustering value.
- `where_description` excluded from both feature sets: median length 32 chars; EDA concluded incremental value over structured geographic features is modest; embedding adds complexity without proportionate analytical benefit.
- `adm_2` excluded from F2: 19.8% null rate + 128-category one-hot would create a 128-dimensional sparse block dominating the feature space. May be revisited in future work.

### 4.3 Outcome Measures

Full specification in `docs/quality_spec.md` (v0.1, pre-registered).

- **Primary:** Silhouette score (final assignment, sklearn euclidean).
- **Secondary:** Davies-Bouldin index; turns to stable assignment (Δ &lt; 0.01).
- **For RQ2:** Spearman's ρ + Cohen's κ (oracle vs. human majority vote); Krippendorff's α (inter-rater reliability, must be ≥ 0.40 before H3 proceeds).

### 4.4 Sample

- N = 2,000 events, random sample from 27,942-event Russia-Ukraine subset (country_id = 369, date_start ≥ 2022-02-24).
- Seed: 42. File: `data/sample_seed42.csv`. MD5: `a92a9a2dc2bec3a0dfa3accb6759daf0`.
- Sample fraction: 14.3% of the filtered subset. Feasibility-driven choice.

---

## 5. Minimum Viable Build (scope boundary)

The build exists solely to run the study. Required capabilities:

- Config-driven: accepts `condition`, `feature_set`, `K`, `seed` as parameters.
- Runs clustering pipeline end-to-end; writes `{run_id, condition, feature_set, seed, K, silhouette_final, db_final, timestamp}` to `runs/run_log.jsonl`.
- For Conditions B/C: CLI conversational loop; logs each turn as `{run_id, turn, instruction, parsed_params, silhouette_turn_N, db_turn_N, timestamp}`; does **not** display Silhouette score to human experimenter in Condition B.
- Runnable from fresh clone with `pip install -r requirements.txt` + one command.

No UI beyond CLI output. No caching, auth, or extensibility abstractions.

**Stack (finalised):** Python, scikit-learn (clustering + metrics), pandas (data), \[LLM API TBD — see open questions\], jsonlines (logging).

---

## 6. Team Roles and Contribution Boundaries

| Person | Sprint ownership | Primary gradable artifacts |
| --- | --- | --- |
| Person 1 | Study design · evaluation instrument · statistical analysis · related work | `docs/study_plan.md`, `docs/related_work.md`, `docs/study_design.md`, `docs/quality_spec.md`, analysis notebooks, final report §results |
| Person 2 | MVB · prompt engineering · logging infrastructure | `src/` (pipeline code), `prompts/` (versioned prompt files), `README.md`, `requirements.txt`, `config/model.yaml` |
| Person 3 | Data pipeline · EDA · experiment runner · data ethics | `data/eda_ucdp_ukraine.ipynb`, `data/sample_seed42.csv`, `docs/data_provenance.md`, run execution logs, `docs/study_plan.md §data` |

---

## 7. Open Questions

### Resolved (v0.2)

- [x] **Dataset size and sampling.** 27,942 events post-filter; N = 2,000 sample drawn with seed 42, MD5 confirmed. No downsampling needed.

- [x] `where_description` **embedding.** Decided: excluded. Median 32 chars; marginal value over structured geographic features per EDA §5.7.

- [x] `type_of_violence` **and** `side_a` **in F2.** Decided: both excluded due to near-zero variance (EDA cardinality table).

- [x] **Ethical classification.** UCDP GED is publicly available, covers no individual persons, published by Uppsala University under academic terms. No IRB required. Human rater consent procedure documented in `docs/study_design.md §10`.

### Resolved (v0.3)

- [x] **LLM model string.** Pinned as `claude-sonnet-4-5` in `config/model.yaml`. Note: Condition A runs were executed with an earlier model string (`claude-sonnet-4-20250514`) before the string was corrected. This discrepancy is inconsequential for Condition A (k-means does not call the LLM) but is registered as a protocol amendment in `docs/study_design.md §12`.

- [x] **K = 8 confirmation.** K = 8 used in all 120 completed runs (Conditions A and C, both feature sets). Confirmed as the working fixed value. Formal elbow plot not committed separately — this is noted as a documentation gap.

- [x] **Prompt files.** `prompts/interpreter.md` and `prompts/oracle_user.md` committed and operational. Both used in all Condition C runs without triggering placeholder errors.

### Still open

- [x] **Experimenter assignment order.** `config/experimenter_order.txt` exists but still contains `PENDING`. Must be filled before any Condition B session begins. **Blocking for Condition B.**

- [ ] **Human rater recruitment.** Target 5–8 raters; course peers as candidates. Rating form (Google Form) must be committed as a link in `docs/rating_instrument_link.txt` before any rater is recruited. Required for H3. **Blocking for H3.**

---

## 8. Sprint 2 Roadmap

Sprint 1 delivered: EDA complete, study design and quality spec pre-registered, experimental sample committed. The repo build is the critical gap going into Sprint 2.

| Person | Sprint 2 job | Status (v0.3, 2026-05-22) |
| --- | --- | --- |
| Person 1 | Draft human rating instrument (Google Form, 20 pairs structure) · Begin rater recruitment · Finalize K via elbow method and commit to `study_design.md §2.3` · Update `related_work.md` to v1 (positioning paragraphs) | ⚠ **Partial.** `experimenter_order.txt` and K operationally confirmed, but elbow plot not formally committed and rating form not yet linked. `related_work.md` still at v0. Rater recruitment not started. |
| Person 2 | **Build the MVB**: feature encoding pipeline (`src/features.py`) · baseline clustering run (Condition A) · conversational loop CLI (`src/loop.py`) · logging to `runs/run_log.jsonl` · commit versioned prompt files (`prompts/interpreter.md`, `prompts/oracle_user.md`) · confirm and pin LLM model string in `config/model.yaml` | ✅ **Complete.** All modules built and operational. Prompts committed. Model string pinned. |
| Person 3 | Run Condition A × F1 and F2 × seeds 0–29 once the build is stable · Sanity-check run logs · Begin Condition C oracle runs · Sprint notes committed | ✅ **Complete and exceeded.** 60 Condition A runs complete (seeds 0–29, F1+F2). 60 Condition C runs also complete (seeds 0–29, F1+F2). All 120 runs logged with status `complete`. |

**The locking condition:** The study design is pre-registered and locks when the first entry is written to `runs/run_log.jsonl`. Any change to hypotheses, conditions, or outcome measures after that point requires a timestamped protocol amendment in `docs/study_design.md §12`. Do not begin Condition B runs until `config/experimenter_order.txt` is filled.

---

## 9. Execution Status and Preliminary Results (added v0.3)

### 9.1 Run completion

| Condition | Feature set | Seeds complete | Status |
| --- | --- | --- | --- |
| A | F1 | 30/30 | ✅ Complete |
| A | F2 | 30/30 | ✅ Complete |
| B | F1 | 3/30 | ⏳ In progress — seeds 6, 8, 11 done; 27 remaining |
| B | F2 | 19/30 | ⏳ In progress — seeds 0–12, 17–22 done; seeds 13–16, 23–29 remaining |
| C | F1 | 30/30 | ✅ Complete |
| C | F2 | 30/30 | ✅ Complete |

Total records in `runs/run_log.jsonl`: **142**, all with `status: complete`.

**Condition B remaining work by person** (from `config/experimenter_order.txt`):

| Person | B/F2 remaining | B/F1 remaining |
| --- | --- | --- |
| Daniele | seeds 13, 14, 15, 16 | seeds 0–5, 13–16 |
| Jasnoor | — | seeds 12, 17–22 |
| Giacomo | seeds 23–29 | seeds 7, 9, 10, 23–29 |

### 9.2 Preliminary results (Condition C vs A — pre-specified analysis)

These figures are from `notebooks/analysis.ipynb` executed on the completed log. They are preliminary in the sense that Condition B data is not yet available.

**Silhouette score — descriptive statistics (mean ± SD over 30 seeds):**

| Condition | F1 | F2 |
| --- | --- | --- |
| A — Baseline | 0.905 ± 0.001 | 0.894 ± 0.001 |
| C — Oracle | 0.874 ± 0.167 | 0.863 ± 0.053 |

**H1 (Condition C/F2 vs A/F2):** Wilcoxon p = 0.9992; median improvement = −0.007; bootstrap 95% CI = \[−0.031, −0.001\]. **H1 not supported for Condition C.** The oracle refinement does not improve on the baseline — it slightly degrades Silhouette in the majority of seeds (22/30 negative). This is a substantive finding: automated oracle-driven refinement under these prompt and feature configurations does not outperform one-shot k-means. The confirmatory test for H1 remains the human-driven Condition B, which is still pending.

**H2 (exploratory):** Cannot be computed until Condition B data is available.

**H3:** Cannot be computed until human ratings are collected.

### 9.3 Dataset limitation identified during Condition B execution

During Condition B sessions it became clear that the Russia-Ukraine GED subset presents near-zero variance in actor identity and violence type: `side_a` is constant (100% Government of Russia), `side_b` is Government of Ukraine in 99.2% of events, and `type_of_violence` is state-based (type 1) in 99.2% of events. As a result, the conversational feature-weighting mechanism has effectively only two informative dimensions to explore: **geographic position** (lat/lon + adm1) and **fatality level**. Actor-based instructions in F2 sessions produce minimal effect. This limitation must be disclosed in the final report and is partially responsible for the low variance in F2 vs F1 Silhouette scores (0.863 vs 0.874 for Condition C).

---

## 10. Results Dashboard (added v0.4)

### 10.1 Purpose and scope

To accompany the final analysis, the team plans to build a **lightweight results dashboard** to visualize the experimental outputs interactively. The dashboard is a communication and exploration tool — it does not affect the pre-registered analysis in `docs/study_design.md`, does not modify `runs/run_log.jsonl`, and is not part of the experimental protocol.

### 10.2 Planned technology

**Streamlit** — chosen for its minimal setup (pure Python, no frontend code), direct compatibility with pandas/matplotlib/plotly, and ability to run locally from a single script file.

```bash
pip install streamlit plotly
streamlit run dashboard/app.py
```

### 10.3 Planned views

| View | Description |
| --- | --- |
| **Overview** | Summary table: mean Silhouette and Davies-Bouldin per (condition × feature set), with run count and status. Mirrors the summary table in `notebooks/analysis.ipynb §8`. |
| **H1 — Condition comparison** | Box plot of final Silhouette scores for A vs B vs C, split by feature set. Per-seed improvement bar chart (B − A and C − A). |
| **Per-turn trajectory** | Line plot of median Silhouette by turn number for Conditions B and C (F2). Individual seed traces shown faintly in the background. |
| **Geographic cluster map** | For a selected run (condition, feature set, seed), a scatter map of the 2,000 events coloured by cluster assignment. Uses Plotly `scatter_mapbox` with OpenStreetMap tiles. |
| **Run explorer** | Filterable table of all records in `run_log.jsonl`. Allows drill-down into individual run metadata, turn-by-turn instructions, and parsed feature weights. |

### 10.4 Data source

All views read exclusively from `runs/run_log.jsonl` and `data/sample_seed42.csv`. No recomputation of clustering is performed at runtime — the dashboard is read-only.

### 10.5 Deliverable

A single file `dashboard/app.py`, runnable with `streamlit run dashboard/app.py` from the repo root. To be committed once Condition B runs are complete and the full log is available.