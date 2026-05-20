# Study Plan — Conversational Clustering on the UCDP GEDEvent 25.1 Dataset

**Dataset:** UCDP Georeferenced Event Dataset (GED) v25.1 — filtered to Russia-Ukraine conflict\
**Version:** v0.1

---

## Changelog

| Version | Date | Summary of changes |
| --- | --- | --- |
| v0.1 | 2025-05-13 | Initial draft. Research questions, hypotheses, and scope committed at Sprint 1 start. Methodology and evaluation strategy are preliminary and will evolve. |

---

## 1. Context and Motivation

The UCDP GEDEvent 25.1 dataset provides structured, georeferenced records of organized violent events in the Russia-Ukraine conflict. Each record encodes event type, actor identities, location (coordinates + administrative divisions), date, and estimated casualties. The dataset has no canonical cluster labels — there is no ground-truth partition of events into meaningful groups. This makes it a suitable testbed for studying whether a conversational clustering system can help a user discover and refine meaningful groupings without manual hyperparameter tuning.

This project sits at the intersection of two questions: (1) does conversational refinement produce better clusters than automated baseline methods, and (2) can we evaluate cluster quality cheaply — without expensive human annotation — by using an LLM oracle as a proxy rater?

---

## 2. Research Questions

### Primary — RQ1: Conversational refinement vs. one-shot clustering

> **Does iterative conversational refinement produce measurably better clusters (by internal validity indices) than a single automated clustering run on the GEDEvent data, and does the magnitude of improvement depend on the feature set used to represent events?**

The intuition is that automated clustering on a mixed structured dataset (numeric + categorical + geographic features) is sensitive to feature weighting and distance metric choices that a user cannot easily specify upfront. Conversational refinement provides a channel through which domain knowledge — "separate events by actor type, not just location" — can be injected incrementally.

### Secondary — RQ2: LLM oracle as proxy for human judgment

> **Do cluster quality rankings produced by an LLM oracle correlate with human rater preferences at ρ &gt; 0.7 (Spearman's rank correlation), making oracle-driven evaluation a viable low-cost substitute for human rating in this setting?**

This is a meta-claim about our evaluation methodology. If the oracle is a valid proxy, it justifies using it to evaluate the many experimental runs that human rating cannot cover at scale. A low correlation is an equally important finding — it would mean oracle-driven evaluation of structured conflict data is unreliable and should not be used without human validation.

---

## 3. Hypotheses

| ID | Type | Statement |
| --- | --- | --- |
| H1 | Confirmatory | Conversational refinement improves the Silhouette score of the final cluster assignment relative to the automated baseline (one-shot k-means on default features), with the improvement quantified as a 95% CI excluding zero. |
| H2 | Exploratory | The improvement from conversational refinement is larger when clustering uses a richer feature set (event type + actor + location + casualties) than when using location alone, suggesting refinement adds most value when the feature space is high-dimensional and ambiguous. |
| H3 | Confirmatory | Spearman's ρ between LLM oracle cluster rankings and human rater rankings exceeds 0.7 on a held-out sample of 20 cluster pairs. |

H1 is the primary confirmatory test. H2 is exploratory and will be reported as such. H3 is confirmatory but depends on recruiting raters — its sample size will be revisited in v0.2.

---

## 4. Study Design (preliminary)

### 4.1 Conditions

| Condition | Description | Role |
| --- | --- | --- |
| A — Baseline | One-shot k-means on default feature set (location + event type), K chosen by elbow method | Primary control |
| B — Full conversational | User (or simulated oracle) refines clusters through natural language over up to 5 turns | Treatment |
| C — LLM oracle | LLM acts as the user in condition B; used to simulate many sessions cheaply | Proxy-validity arm |

### 4.2 Dataset scope

- Filter GEDEvent 25.1 to Russia-Ukraine conflict events only (country codes UKR/RUS, post-2022).
- Target sample: 1,000–3,000 events after filtering. If the filtered set is larger, random-sample with a fixed seed (documented in config).
- Features available for clustering: event type (categorical), side_a / side_b actor names (categorical), adm1 / adm2 administrative region (categorical), latitude / longitude (continuous), best estimate of fatalities (continuous), date_start (temporal).
- Encoding strategy (to be finalized in v0.2): one-hot for categoricals, min-max normalization for continuous, potential sentence embedding of the `where_description` text field if it proves informative.

### 4.3 Outcome measures

- **Primary:** Silhouette score of final cluster assignment (higher = better-separated, more cohesive clusters).
- **Secondary:** Davies-Bouldin index (lower = better); number of conversational turns to stable assignment (convergence speed).
- **For RQ2:** Spearman's ρ between oracle rankings and human rankings on a held-out sample of cluster pairs; inter-rater agreement (Krippendorff's α) among human raters.

### 4.4 Human rating instrument (preliminary)

Raters will be shown two cluster descriptions side by side — a short label and 3 representative events per cluster — and asked: "Which grouping makes more sense as a meaningful category of conflict event?" (forced-choice pairwise). We target N = 5–8 raters, each rating 20 pairs (within-subject). Rating instrument to be finalized and committed as a versioned artifact before data collection begins.

### 4.5 Sample size reasoning

With N = 20 cluster pairs and 5–8 raters per pair, we have adequate power to estimate Spearman's ρ with ±0.15 precision (bootstrap CI). We are underpowered for formal hypothesis testing of human preference differences; we will report effect sizes and CIs honestly and not overclaim. For the Silhouette comparison (H1), we will run 30 replications per condition with different random seeds and report the distribution of improvements.

---

## 5. Minimum Viable Build (scope boundary)

The build exists solely to run the study. It must:

- Accept a config file specifying condition (A/B/C), feature set, K, and random seed.
- Run the clustering pipeline end-to-end and write cluster assignments + Silhouette score to a JSONL log.
- For conditions B/C: implement a conversational loop (CLI or notebook) where user or oracle can issue one refinement instruction per turn; log each turn (instruction → LLM interpretation → new params → new score).
- Be runnable from a fresh clone with `pip install -r requirements.txt` + one command.

No UI beyond CLI output is required. No caching, auth, or "future extensibility" abstractions.

**Stack (preliminary):** Python, scikit-learn (clustering), sentence-transformers or sklearn encoders (features), Claude API or OpenAI API (LLM interpreter + oracle), pandas (data), jsonlines (logging).

---

## 6. Team Roles and Contribution Boundaries

| Person | Sprint ownership | Gradable artifact |
| --- | --- | --- |
| Person 1 | Study design · evaluation instrument · statistical analysis · related work | docs/study_plan.md, docs/related_work.md, docs/study_design.md, analysis notebooks, final report §results |
| Person 2 | MVB · prompt engineering · logging infrastructure | src/ (pipeline code), prompts/ (versioned prompt files), README, requirements.txt |
| Person 3 | Data pipeline · dataset exploration · experiment runner · data ethics section | data/ (cleaning scripts, EDA notebook), run logs, docs/study_plan.md §data provenance |

All three contribute to the final report and presentation. Individual contributions must be traceable in commit history — no shared-machine commits.

---

## 7. Open Questions (to resolve by v0.2)

- [x] What is the exact size of the Russia-Ukraine filtered subset of GEDEvent 25.1? Does it need downsampling? 27,942 events; sample is N = 2,000 (seed 42) — decided and reproducible.

- [x] Is the `where_description` text field rich enough to embed, or should we treat location as purely categorical (adm1/adm2)? §5.7 of the new provenance file answers this directly: embedding is *feasible* for \~90% of entries but "incremental value over structured geographic features is expected to be modest." This should be reflected in study_plan §7 as partially resolved, with a note that the final encoding decision is still to be made before the first run.

- [ ] Which LLM API will we use for the interpreter and oracle? (Cost and rate limits matter for 30 replications.)

- [ ] How do we recruit 5–8 human raters? (Classmates? Structured as a short online form?)

- [ ] Should K be fixed across conditions or allowed to vary? Fixed K is cleaner for comparison; variable K is more realistic for the conversational use case.

- [ ] Confirm ethical classification: GED data is publicly available, covers no individual persons, and is released by an academic institution (UCDP/Uppsala University). No IRB required for the dataset itself; human rater consent procedure to be documented.

---