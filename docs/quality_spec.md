# Quality Specification — Conversational Clustering on the UCDP GEDEvent 25.1 Dataset

**Project:** Conversational Clustering  
**Document:** `docs/quality_spec.md`  
**Version:** v0.2  
**Status:** Pre-registered — committed before any experimental runs or human rating sessions

---

## Changelog

| Version | Date | Summary of changes |
|---|---|---|
| v0.1 | 2026-05-19 | Initial quality spec committed at Sprint 1/2 boundary. Defines quality dimensions, operationalisations, measurement methods, and decision rules for all metrics reported in the final paper. Locked against post-hoc revision once the first run log entry is written (same lock event as `docs/study_design.md`). |
| v0.2 | 2026-06-02 | H3 proxy-validity measurement updated post-hoc to document original/swapped oracle evaluation, displayed-label-bias diagnostics, and the interpretation rule used after the suspicious first oracle pass. |

---

## 1. Purpose and Scope

This document answers one question precisely: **what does "better" mean in this study, and how is it measured?**

The study has two distinct quality claims to support:

- **Claim 1 (RQ1 / H1–H2).** Conversational refinement produces better cluster assignments than one-shot automated clustering, on the UCDP GEDEvent Russia-Ukraine subset.
- **Claim 2 (RQ2 / H3).** An LLM oracle is a valid proxy for human judgment when ranking cluster assignments by quality.

Each claim requires its own quality operationalisation. They are treated separately in §§3–4. §2 establishes the multi-dimensional quality framework and explains which dimensions are in scope and which are explicitly excluded.

Every metric reported in the final paper appears in this document. Any metric not listed here that appears in the paper must be flagged as a post-hoc addition in the paper's limitations section.

---

## 2. Quality Dimensions: In-Scope and Out-of-Scope

The table below maps the standard quality dimensions from the course framework to this project's specific constructs.

| Dimension | In scope? | Rationale |
|---|---|---|
| **Cluster cohesion and separation** | ✅ Primary | The core technical quality of a clustering. Operationalised via Silhouette score (primary) and Davies-Bouldin index (secondary). |
| **Human interpretability** | ✅ Secondary | Whether a human judge finds the resulting clusters meaningful as categories of conflict event. Operationalised via forced-choice pairwise human rating. |
| **Oracle–human agreement (proxy validity)** | ✅ Confirmatory (H3) | Whether the LLM oracle's quality rankings correlate with human rankings. Operationalised via Spearman's ρ and Cohen's κ on the forced-choice judgements. |
| **Position-bias resistance** | ✅ Required for H3 interpretation | Whether the oracle tracks the same underlying clustering after A/B labels are swapped, rather than preserving the same displayed label. |
| **Inter-rater reliability** | ✅ Required | Krippendorff's α across human raters on the pairwise judgement task. Reported before oracle-correlation results are interpreted. |
| **Faithfulness / grounding** | ❌ Out of scope | The system does not generate text claims about the world; it produces cluster assignments. Hallucination is not a meaningful construct here. |
| **Calibration** | ❌ Out of scope | The system does not produce probabilistic outputs or confidence scores. |
| **Correctness / task success (binary)** | ❌ Not applicable | No ground-truth partition of GED events exists. Binary correctness cannot be computed. This is the definitional reason internal validity indices and human ratings are used. |
| **Robustness under distribution shift** | ❌ Deferred | Testing robustness across different conflict subsets (e.g., non-Ukraine GED data) is beyond the scope of this study. Noted as future work. |
| **Latency / token cost** | ❌ Secondary / logged only | Per-run token usage and wall-clock time are logged (`runs/run_log.jsonl`) for reproducibility but are not claimed as quality outcomes. |
| **User-facing utility (behavioral)** | ❌ Partially addressed | We do not recruit real analyst users. Condition B (team-member experimenter) and human pairwise rating are the closest proxies. Limitations of this substitution are noted in §7. |

---

## 3. Operationalisation: Cluster Assignment Quality (Claim 1)

### 3.1 Primary Metric — Silhouette Score

**What it measures.** For each event *i*, the Silhouette coefficient *s(i)* compares:
- *a(i)*: mean distance from *i* to all other events in the same cluster (intra-cluster cohesion).
- *b(i)*: mean distance from *i* to all events in the nearest other cluster (inter-cluster separation).

*s(i)* = (*b(i)* − *a(i)*) / max(*a(i)*, *b(i)*)

The dataset-level Silhouette score *S* is the mean of *s(i)* over all events.

**Range and interpretation.** [−1, 1]. Values near 1 indicate well-separated, cohesive clusters. Values near 0 indicate overlapping clusters. Negative values indicate likely misassignment.

**Measurement procedure.**
- Computed using `sklearn.metrics.silhouette_score` with `metric='euclidean'` on the min-max normalised feature matrix.
- Computed on the final cluster assignment (after 0 turns for Condition A; after turn 5 for Conditions B and C).
- Logged to `runs/run_log.jsonl` as field `silhouette_final`.
- Also computed after each intermediate turn (Conditions B/C) and logged as `silhouette_turn_{n}`.

**Construct validity note.** Silhouette score with Euclidean distance implicitly assumes convex, roughly equal-sized clusters — an assumption that may not hold for geographic conflict data (clusters may be spatially elongated or unequal in size). This is a known limitation (see Arbelaitz et al., 2013, cited in `docs/related_work.md` [10]). The Davies-Bouldin index is used as a secondary measure precisely because it has different failure modes; if the two measures diverge, both are reported and the discrepancy is discussed.

**What a higher Silhouette score does and does not mean.**
- It means the clustering is more geometrically coherent under the chosen features and distance metric.
- It does not mean the clusters are more meaningful to a domain analyst. That is measured separately (§3.3).
- It does not imply correctness relative to any ground truth.

### 3.2 Secondary Metric — Davies-Bouldin Index

**What it measures.** For each cluster *k*, the Davies-Bouldin index considers the ratio of within-cluster scatter to between-cluster distance, averaging over the worst-case neighbour for each cluster. Lower values indicate better separation.

**Measurement procedure.** Computed using `sklearn.metrics.davies_bouldin_score` on the same normalised feature matrix and logged as `db_final` (and `db_turn_{n}` for intermediate turns). Lower = better; the direction of "improvement" is reversed relative to Silhouette.

**Role in analysis.** Secondary robustness check only. The primary hypothesis test (H1) uses Silhouette. If Silhouette and Davies-Bouldin conclusions conflict, both are reported with a note on which failure mode may explain the divergence.

### 3.3 Tertiary Metric — Human Interpretability (Pairwise Forced Choice)

**What it measures.** Whether a human judge, given descriptions of two alternative cluster assignments, prefers one as more meaningful for understanding conflict events. This operationalises **human-perceived cluster quality** — a construct that Silhouette score does not capture.

**Measurement procedure.** Described fully in `docs/study_design.md` §6.2. In brief: each rater sees two cluster descriptions (label + 3 representative events) side by side and makes a forced choice. Aggregation: majority vote across 5–8 raters per pair. Ties (≤ 1 rater difference) are recorded as ties, not coerced to a winner; tied pairs are excluded from the H3 Spearman calculation and their count is reported.

**Construct validity note.** Forced-choice pairwise preference is a well-established paradigm for comparing subjective quality without requiring raters to use an absolute scale (avoiding scale-use heterogeneity bias). Its limitation is that it yields only relative, not absolute, quality judgements — we cannot say a "winning" cluster assignment is good in absolute terms, only that it was preferred over its pair.

**Relationship to Silhouette.** Human interpretability and Silhouette score are treated as independent quality dimensions. The study does not assume they are correlated; the degree of correlation between human preference and Silhouette rank is an empirical question and will be reported descriptively (Spearman's ρ between human majority-vote rank and Silhouette rank, computed within each comparison cell).

### 3.4 Logged-Only Metrics (Not Reported as Quality Outcomes)

| Metric | Field in run log | Why logged |
|---|---|---|
| Turns to stable assignment | `turns_to_stable` | Convergence speed; reported descriptively, not as a quality claim |
| Per-turn Silhouette trajectory | `silhouette_turn_0` … `silhouette_turn_5` | Exploratory trajectory analysis (§8 of study design) |
| API token count per run | `tokens_total` | Reproducibility; cost estimation |
| Wall-clock time per run | `elapsed_seconds` | Reproducibility |

---

## 4. Operationalisation: Oracle Validity (Claim 2)

### 4.1 The Construct Being Validated

The claim is that the LLM oracle's forced-choice rankings of cluster pairs are a **valid proxy** for human forced-choice rankings. "Valid proxy" is operationalised as: the oracle and human majority-vote agree often enough that the oracle can be used as a substitute in the many runs where human rating is not feasible.

This is a claim about **measurement equivalence**, not about which ranking is "correct." There is no ground truth; the oracle is validated against human judgment, and human judgment is treated as the reference standard for this construct.

### 4.2 Primary Metric — Spearman's ρ (Ranking Agreement)

**What it measures.** Rank-order correlation between the oracle's preference ranking and the human majority-vote ranking over 20 cluster pairs. ρ = 1 means perfect rank agreement; ρ = 0 means no rank agreement.

**Measurement procedure.**
- For each of the 20 pairs, the oracle receives the same prompt and the same cluster descriptions as human raters (the forced-choice instrument from `docs/study_design.md` §6.2), with no additional context about the study or conditions.
- Each pair is evaluated twice by the oracle: once in the original displayed A/B order used for humans, and once with displayed A/B swapped while keeping the underlying pair fixed.
- Oracle output is a binary preference (A or B). Ties are not possible for the oracle (the prompt forbids "no preference").
- Human output is majority vote over 5–8 raters per pair; ties excluded (see §3.3).
- Spearman's ρ is computed over the 20 (oracle choice, human majority choice) pairs, treating each as a binary outcome (1 = same choice, 0 = different choice). Equivalently, ρ here reduces to a point-biserial correlation, but we report it as Spearman's for consistency with H3's framing.
- Bootstrap 95% CI: 10,000 resamples of the 20 pairs with replacement.

**Decision rule.** Stated in `docs/study_design.md` §4.3. Confirmatory threshold: ρ > 0.7 AND bootstrap CI lower bound > 0.5.

### 4.3 Secondary Metric — Cohen's κ (Agreement Beyond Chance)

**What it measures.** Agreement between oracle binary choices and human majority-vote binary choices, corrected for chance. κ = 1 is perfect agreement; κ = 0 is chance-level; κ < 0 is worse than chance.

**Measurement procedure.** Computed on the same 20 pairs as Spearman's ρ. Oracle choice coded as {0, 1}; human majority-vote coded as {0, 1} (tied pairs excluded). Standard two-rater κ formula applied with oracle and human as the two "raters."

**Benchmarks for interpretation** (following Landis & Koch, 1977, as reported in the reliability literature):
- κ < 0.20: slight agreement — oracle is not a useful proxy.
- 0.20 ≤ κ < 0.40: fair — oracle provides weak signal only.
- 0.40 ≤ κ < 0.60: moderate — use with caution, report discrepancies.
- 0.60 ≤ κ < 0.80: substantial — oracle is an acceptable proxy.
- κ ≥ 0.80: near-perfect — oracle can substitute for human rating.

κ is reported alongside Spearman's ρ. If ρ > 0.7 but κ < 0.40, the confirmatory threshold for H3 is not considered met (the rank correlation may be driven by marginal distributions rather than genuine agreement on individual pairs). Likewise, if the oracle preserves the same displayed label after swapping A/B rather than the same underlying clustering, κ from the original-order pass is treated as contaminated by displayed-label bias and cannot by itself support H3.

### 4.4 Position-Bias Diagnostic

**What it measures.** Whether the oracle tracks the same underlying clustering after the displayed A/B labels are swapped.

**Measurement procedure.**
- For each pair, compare original-order and swapped-order oracle choices in two ways: whether the same underlying side / run was chosen, and whether the same displayed label was repeated.
- A pair is flagged for displayed-label bias if the oracle keeps the same displayed label after the swap but does **not** keep the same underlying clustering.

**Interpretation rule.** If this pattern dominates the 20 pairs, H3 is treated as failed due to response-position / label bias even if original-order agreement looks acceptable.

### 4.5 Inter-Rater Reliability Among Human Raters

**What it measures.** Agreement among the 5–8 human raters on the pairwise forced-choice task, before computing the majority vote used in H3. Low inter-rater reliability would undermine the validity of the human reference standard.

**Measurement procedure.** Krippendorff's α computed over the full rating matrix (raters × pairs), treating the binary forced-choice as a nominal variable. Computed using the `krippendorff` Python package.

**Reporting rule.** Inter-rater α is reported before oracle-correlation results in the paper. If α < 0.20 (slight agreement), the human rating data is considered unreliable and H3 is reported as infeasible regardless of oracle-human correlation.

**Minimum acceptable α for H3 to proceed:** 0.40 (moderate). If 0.20 ≤ α < 0.40, H3 results are reported with a prominent caveat about the reliability of the reference standard.

**Calibration subset.** A random 5-pair subset of the 20 is re-rated by a second team member independent of the primary rater pool, to provide an independent estimate of measurement noise. Agreement on this subset is reported as a secondary reliability check.

---

## 5. Confidence Intervals: Requirements

Every quantitative quality claim in the final paper must be accompanied by a 95% confidence interval. The table below lists the CI method for each reported metric.

| Metric | CI method |
|---|---|
| Silhouette score (per condition × feature set cell) | Bootstrap CI over 30 seeds (10,000 resamples) |
| Median B−A Silhouette improvement (H1) | Bootstrap CI over 30 paired differences (10,000 resamples) |
| Davies-Bouldin (secondary) | Bootstrap CI over 30 seeds |
| Spearman's ρ (oracle–human, H3) | Bootstrap CI over 20 pairs (10,000 resamples) |
| Cohen's κ (oracle–human) | Bootstrap CI over 20 pairs |
| Krippendorff's α (inter-rater) | Bootstrap CI using `krippendorff` package's built-in bootstrap |

Reporting rule: CIs are reported in the format *estimate* [*lower*, *upper*] inline in the text. Bar charts and box plots include CI overlays or error bars. A result described as an "improvement" or "agreement" must have a CI that excludes the null value (zero for differences; 0.7 for ρ in H3) for a confirmatory claim to be made; otherwise the result is described as "trending" or "inconclusive."

---

## 6. LLM-as-Judge Validation Requirement

This study uses the LLM oracle both as a simulated user (Condition C) and as a proxy evaluator (H3). The minimum validation requirement for the oracle-as-judge role is:

1. **Subset size:** The 20-pair human-rating task (§4.4) constitutes the validation set. This meets the minimum requirement of ≥ 20 items stated in the professor's framework (the course minimum is 30; our justification for 20 is stated in `docs/study_design.md` §5.2 and is accepted as feasibility-driven).

2. **Agreement statistic:** Cohen's κ is reported (§4.3). Spearman's ρ alone is insufficient because it can be inflated by marginal-distribution effects in a binary outcome.

3. **Bias disclosure:** The oracle is the same model and, in Condition C, the same prompt configuration that generated some of the cluster assignments being rated. This creates a self-preference risk and a displayed-label bias risk. Both are disclosed in the paper's limitations section (see §7 of this document).

4. **Prompt text:** The oracle evaluation prompt is committed to `prompts/oracle_eval.md` before any oracle ratings are collected. The prompt does not reveal which cluster assignment was generated by which condition.

---

## 7. Threats to Measurement Validity

The following threats to the validity of the quality measures are acknowledged and must be disclosed in the final paper. They do not invalidate the study but bound the conclusions that can be drawn.

| Threat | Affected metric(s) | Nature of the threat | Mitigation applied |
|---|---|---|---|
| **Euclidean distance assumption** | Silhouette, Davies-Bouldin | k-means + Euclidean distance assumes convex, roughly isotropic clusters. Conflict events may form geographically elongated or temporally stratified clusters that are penalised. | Davies-Bouldin used as secondary check; divergence between the two is reported. |
| **Fixed K assumption** | Silhouette, Davies-Bouldin | Silhouette is sensitive to K. Fixing K = 8 across conditions ensures comparability but means a conversational condition that would benefit from a different K cannot express that benefit. | Limitation disclosed; K sensitivity analysis deferred to future work. |
| **Rater domain knowledge** | Human pairwise rating | Team members and course peers lack expert knowledge of the Russia-Ukraine conflict. Ratings reflect a domain-naive analyst's intuitions, not expert geopolitical judgment. | This is the relevant user population for the prototype; explicitly described in the paper. |
| **Oracle self-preference bias** | Cohen's κ, Spearman's ρ | The oracle model may prefer Condition C outputs (its own) when rating pairs. | Blind prompt (condition labels omitted); disclosed as residual risk. |
| **Displayed-label / position bias** | Spearman's ρ, Cohen's κ | The oracle may preserve the displayed label A or B after swapping, rather than preserving the same underlying clustering. | Original/swapped-order diagnostic added; same-label-after-swap behaviour is treated as evidence against H3. |
| **Majority-vote aggregation** | Spearman's ρ, Cohen's κ | Majority vote discards rater disagreement information and can mask bimodal preferences. | Krippendorff's α reported first; tied pairs excluded from ρ calculation. |
| **Small validation set (N = 20)** | Spearman's ρ, Cohen's κ | CI width of ±0.15 on ρ means marginal results (ρ ≈ 0.7) cannot be clearly distinguished from threshold. | Decision rule requires both ρ > 0.7 and CI lower bound > 0.5; marginal results reported as inconclusive. |
| **Feature encoding validity** | All cluster-quality metrics | One-hot encoding of actor names introduces a high-dimensional, sparse space that may not represent semantic actor similarity. A unit that changes actor coding (e.g., splitting actor categories) would improve encoding validity but change the feature space mid-experiment. | Encoding fixed before any runs; limitation disclosed. |

---

## 8. Summary Table: All Reported Metrics

| Metric | Dimension | Primary / Secondary | Measurement method | CI method | Threshold for confirmatory claim |
|---|---|---|---|---|---|
| Silhouette score (final) | Cohesion & separation | **Primary (H1)** | `sklearn.metrics.silhouette_score` | Bootstrap over 30 seeds | Median improvement > 0, 95% CI excludes 0, Wilcoxon p < 0.05 |
| B−A Silhouette improvement | Cohesion & separation | **Primary (H1)** | Paired difference over 30 seeds | Bootstrap over 30 differences | See above |
| Davies-Bouldin index (final) | Cohesion & separation | Secondary | `sklearn.metrics.davies_bouldin_score` | Bootstrap over 30 seeds | Robustness check only; no standalone threshold |
| Human pairwise preference | Interpretability | Secondary | Forced-choice, majority vote | — (proportion with binomial CI) | Descriptive; no standalone confirmatory threshold |
| Spearman's ρ (oracle vs. human) | Proxy validity | **Confirmatory (H3)** | Rank correlation on 20 pairs | Bootstrap over 20 pairs | ρ > 0.7 AND CI lower bound > 0.5 |
| Cohen's κ (oracle vs. human) | Proxy validity | Secondary (H3 check) | Standard two-rater κ | Bootstrap over 20 pairs | κ ≥ 0.40 required for H3 to be considered met |
| Position-bias diagnostic | Proxy validity safeguard | Prerequisite for H3 interpretation | Original/swapped oracle comparison on the same 20 pairs | Pair-level counts | Same displayed label after swap without the same underlying choice counts against H3 |
| Krippendorff's α (inter-rater) | Measurement reliability | Prerequisite | `krippendorff` package | Bootstrap | α ≥ 0.40 required before H3 proceeds |
| Silhouette per turn (trajectory) | Convergence | Exploratory | Per-turn `silhouette_score` | — | Descriptive only |

---

## 9. What Is Not a Quality Metric in This Study

To prevent garden-of-forking-paths analysis, the following are explicitly excluded from the quality framework, even if they appear to be measurable from the data:

- **Cluster label coherence** (the quality of the auto-generated cluster label text) — not a property of the cluster assignment, and the labels are used only for the human rating display.
- **Instruction clarity in Condition B** — the naturalness or precision of the experimenter's refinement instructions is not a quality outcome; it is an uncontrolled aspect of the interaction.
- **Model perplexity or token probability** of the oracle's outputs — not a meaningful proxy for cluster quality in this setting.
- **Absolute number of clusters with Silhouette > 0** — this is a per-cluster statistic that is not pre-specified as an aggregate outcome.

Any analysis of these quantities in the final paper must be clearly labelled as exploratory and post-hoc.
