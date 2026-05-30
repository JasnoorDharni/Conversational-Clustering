# Study Design — Conversational Clustering on the UCDP GEDEvent 25.1 Dataset

**Project:** Conversational Clustering  
**Document:** `docs/study_design.md`  
**Version:** v0.1  
**Status:** Pre-registration draft — committed before any experimental runs

---

## Changelog

| Version | Date | Summary of changes |
|---|---|---|
| v0.1 | 2026-05-19 | Initial study design committed at Sprint 1/2 boundary. Factor structure, conditions, outcome measures, decision rules, and sample-size justification pre-specified. Randomization plan and stratification to be finalised in v0.2 before main experiment runs. |

---

## 1. Purpose of This Document

This document is the pre-registered blueprint of the experiment. It is committed to version control before any experimental runs are executed. Its function is to make the investigation confirmatory rather than exploratory after the fact: the hypotheses, outcome measures, decision rules, and analysis plan stated here cannot be revised once data collection begins without an explicit, timestamped protocol amendment. Discrepancies between this document and the final analysis must be reported as deviations.

The authoritative statement of research questions and hypotheses is `docs/study_plan.md` (v0.1). This document translates those into an operationalisable experimental blueprint.

---

## 2. Factor Structure

### 2.1 Independent Variable (Manipulated Factor)

**Factor:** Clustering method / user-interaction regime  
**Levels:** Three discrete conditions (see §3).  
**Unit of assignment:** A single clustering session run on a fixed dataset sample with a fixed random seed. Each combination of (condition × feature set × seed) constitutes one experimental run.

### 2.2 Moderating Factor (Feature Set)

**Factor:** Feature representation of events  
**Levels:** Two levels (crossed with the interaction regime factor):

| Level | Features included |
|---|---|
| F1 — Location-only | Latitude / longitude (continuous, min-max normalised) + adm1 administrative region (one-hot encoded) |
| F2 — Full | F1 + event type (one-hot) + side_a / side_b actor identity (one-hot, top-N by frequency) + best fatality estimate (continuous, min-max normalised) |

The feature-set factor is included to test H2 (exploratory): whether conversational refinement adds more value when the feature space is richer and more ambiguous. It is a moderator, not a second primary factor — the experiment is not fully powered to detect interactions, and H2 will be reported as exploratory.

### 2.3 Held Constant (Controls)

The following are held constant across all experimental runs to isolate the effect of the interaction regime:

| Element | Fixed value / procedure |
|---|---|
| Dataset | UCDP GEDEvent 25.1, Russia-Ukraine subset (country codes UKR/RUS, events with date_start ≥ 2022-02-24), random sample of N = 2,000 events drawn with seed 42 |
| Base clustering algorithm | k-means (scikit-learn `KMeans`, `init='k-means++'`, `n_init=10`) |
| Number of clusters K | Fixed at K = 8 across all conditions (chosen by elbow method on the baseline feature set in a one-time pre-experiment run; see §3.1) |
| Cluster initialisation seed | Varied systematically (30 seeds per condition, seeds 0–29); seed is a blocking variable, not a free parameter |
| LLM model (interpreter + oracle) | `claude-sonnet-4-6` throughout; model version pinned in `config/model.yaml` |
| Maximum conversational turns | 5 turns per session (Conditions B and C) |
| Prompt templates | Versioned in `prompts/`; committed before any run; not revised during the experiment |
| Evaluation instrument | Pairwise forced-choice form (see §6.2); committed before human rating begins |

**Rationale for fixed K.** Fixing K makes the three conditions directly comparable on Silhouette score, which is sensitive to K. Allowing variable K in the conversational condition would confound the refinement effect with a K-selection effect. This is noted as a design limitation in §9.

---

## 3. Conditions

| Condition | Label | Description |
|---|---|---|
| A | Baseline | One-shot k-means on feature set F1 or F2; no iterative refinement. K fixed at 8. Represents standard automated clustering without human input. |
| B | Conversational (human-simulated) | A team member plays the role of user and issues up to 5 natural-language refinement instructions per session. The LLM interpreter translates each instruction into updated clustering parameters; k-means reruns after each turn. The experimenter is blind to the Silhouette score during the session. |
| C | Conversational (LLM oracle) | The LLM acts as both user and interpreter. The oracle receives a structured prompt (versioned in `prompts/oracle_user.md`) that instructs it to play the role of a domain-naive analyst examining cluster output and issuing refinement instructions. Used to simulate many sessions cheaply and to test RQ2. |

**What Condition A is not.** Condition A is not "the worst possible clustering." It is a competent automated baseline — the kind of output a researcher would obtain by applying k-means with default settings and the elbow method. The study tests whether conversational refinement improves on this plausible baseline, not on a strawman.

**Condition B session protocol.** The experimenter conducting a Condition B session must:
1. Not view the Silhouette score or Davies-Bouldin index during the session.
2. Interact only through the CLI conversational interface; no manual parameter edits.
3. Complete all 5 turns before the session is logged as finished (even if the clusters appear satisfactory earlier).
4. Record their post-session qualitative assessment of cluster interpretability (freeform, 2–3 sentences), logged to `runs/session_notes.jsonl`.

---

## 4. Outcome Measures

### 4.1 Primary Outcome

**Silhouette score** of the final cluster assignment (after 0 refinement turns for Condition A; after turn 5 for Conditions B and C).

- Range: [−1, 1]. Higher = better-separated, more cohesive clusters.
- Computed using scikit-learn `silhouette_score` with Euclidean distance on the normalised feature matrix.
- Logged to `runs/run_log.jsonl` alongside run metadata (condition, feature set, seed, K, timestamp).
- **Decision rule for H1:** A one-sided Wilcoxon signed-rank test (paired by seed) comparing Condition B (full feature set F2) vs. Condition A (full feature set F2), over 30 replications. Reject the null if p < 0.05 and the 95% bootstrap CI on the median improvement excludes zero. Both criteria must be met.

### 4.2 Secondary Outcomes

| Measure | Description | Logging location |
|---|---|---|
| Davies-Bouldin index | Lower = better. Computed after each turn; final value reported. Complements Silhouette by penalising close but compact clusters. | `runs/run_log.jsonl` |
| Turns to stable assignment | Number of conversational turns after which the Silhouette score changes by < 0.01 in consecutive turns. Measures convergence speed. | `runs/run_log.jsonl` |
| Per-turn Silhouette trajectory | Silhouette score at each of the 5 turns (Conditions B and C only). Enables analysis of where in the conversational loop improvement occurs. | `runs/run_log.jsonl` |

### 4.3 RQ2 Outcome (Oracle validity)

**Spearman's ρ** between LLM oracle cluster rankings and human rater rankings on a held-out sample of 20 cluster pair comparisons.

- Oracle ranking: for each pair (cluster assignment X, cluster assignment Y), the oracle is prompted to choose which grouping "makes more sense as a meaningful category of conflict event" (forced-choice, mirroring the human instrument).
- Human ranking: aggregated from 5–8 raters using majority vote. Inter-rater agreement reported as Krippendorff's α.
- **Decision rule for H3:** Reject the null (ρ ≤ 0.7) if the point estimate exceeds 0.7 and the bootstrap 95% CI lower bound exceeds 0.5 (a conservative floor). A point estimate above 0.7 with a wide CI that includes 0.5 will be reported as inconclusive, not confirmatory.

---

## 5. Sample-Size Justification

### 5.1 H1 — Silhouette comparison (30 replications per condition)

With 30 paired observations (one per seed), a one-sided Wilcoxon signed-rank test achieves approximately 80% power to detect a medium effect size (r ≈ 0.4, corresponding to a consistent improvement visible in roughly 20 of 30 pairs) at α = 0.05. We do not claim to detect small effects (r < 0.2) with this N; any observed improvement smaller than r ≈ 0.3 will be reported as inconclusive.

The 30-replication plan also allows reporting the distribution of Silhouette improvements as a box plot, providing effect size and variance information beyond the binary hypothesis test. This is the primary deliverable for H1 regardless of statistical significance.

**Computational feasibility.** Each run (one seed, one condition, one feature set) completes in under 2 minutes on a standard laptop. 30 seeds × 3 conditions × 2 feature sets = 180 runs ≈ 6 hours of compute. This is feasible within Sprint 2.

### 5.2 H3 — Oracle-human correlation (20 cluster pairs, 5–8 raters)

With N = 20 cluster pairs, bootstrapped 95% CIs on Spearman's ρ have a half-width of approximately ±0.15 (based on simulation with ρ = 0.7, N = 20). This is sufficient to distinguish "clearly adequate proxy" (ρ > 0.85) from "marginal" (ρ ≈ 0.7) from "inadequate" (ρ < 0.55).

**What this N cannot detect.** We are underpowered to formally test differences in oracle accuracy across sub-conditions (e.g., by feature set or condition). We will not make such claims. The 20-pair sample is drawn to be representative of the full run set (see §5.3).

**Rater recruitment.** Target: 5–8 raters drawn from the course cohort. Each rater completes 20 pairwise judgements (estimated 15–20 minutes). Informed consent procedure documented in `docs/ethics_note.md`. If fewer than 5 raters complete the task, H3 will be reported as infeasible and removed from the confirmatory analysis.

### 5.3 Sampling plan for the 20 cluster pairs (H3)

The 20 pairs will be drawn as follows to ensure representativeness:
- 5 pairs from Condition A vs. Condition B (same seed, F2 feature set) — tests whether refinement is perceptible to humans.
- 5 pairs from Condition A vs. Condition C (same seed, F2) — tests whether oracle-refined clusters are perceptible.
- 5 pairs from Condition B vs. Condition C (same seed, F2) — tests whether human- vs. oracle-refined clusters differ.
- 5 pairs from F1 vs. F2 within Condition A (same seed) — tests whether feature richness matters perceptually.

Pairs are selected by stratified random sampling within each cell, with the restriction that no seed appears more than once across the 20 pairs.

---

## 6. Instruments

### 6.1 Conversational loop (Conditions B and C)

The CLI interface accepts one natural-language instruction per turn, passes it to the LLM interpreter (`prompts/interpreter.md`), which returns a structured parameter update (feature weights, merge/split instruction, or K adjustment — within the constraint that K is fixed). The updated parameters are applied and k-means reruns. The Silhouette score is computed and logged but not displayed to the human experimenter in Condition B. Each turn is logged as a JSONL record: `{run_id, turn, instruction, parsed_params, silhouette, db_index, timestamp}`.

### 6.2 Human rating instrument

Raters are shown two cluster descriptions side-by-side. Each description consists of:
- A short auto-generated cluster label (produced by the LLM from the 5 most frequent event types and actor names in the cluster).
- 3 representative events (randomly sampled from the cluster), displayed as: date, location (adm1), event type, actors involved, fatality estimate.

The forced-choice prompt: **"Which grouping makes more sense as a meaningful category of conflict event? Choose one."** No ties allowed.

The instrument is committed as a versioned Google Form (link in `docs/rating_instrument_link.txt`) before any rater is recruited. The form will not be modified after the first rater completes it.

---

## 7. Randomisation Plan

| Element | Randomisation procedure |
|---|---|
| Dataset sample | Fixed random sample, seed 42, drawn once before any runs. Sample committed to `data/sample_seed42.csv`. |
| Run seeds | Seeds 0–29 assigned sequentially. Order of execution randomised per condition using `random.shuffle` with seed 100 (logged). |
| Condition B experimenter assignment | Condition B sessions for a given seed assigned to team members by a pre-drawn random order (committed to `config/experimenter_order.txt`). No experimenter runs more than 10 sessions to reduce habituation effects. |
| Human rater pair order | For each rater, the 20 pairs are presented in a randomised order (individual per-rater seed). Within each pair, the left/right position of the two cluster descriptions is randomised. |
| Oracle prompt variant | A single versioned oracle prompt is used throughout (no A/B prompt testing in this study). Prompt sensitivity is flagged as a limitation (§9). |

---

## 8. Analysis Plan

All analyses are pre-specified. Deviations will be noted in the final report.

1. **Descriptive statistics first.** For each (condition × feature set) cell, report: mean Silhouette, SD, min, max, and a box plot over 30 seeds. Report Davies-Bouldin and convergence speed in a supplementary table.

2. **H1 test.** One-sided Wilcoxon signed-rank test, Condition B (F2) vs. Condition A (F2), paired by seed. Report W statistic, p-value, and 95% bootstrap CI on median improvement (10,000 bootstrap samples). Effect size: matched-pairs r.

3. **H2 (exploratory).** Compare the B−A improvement under F1 vs. F2 using a Mann-Whitney U test on the per-seed improvement scores. Report without correcting for multiple comparisons; label as exploratory.

4. **H3 test.** Compute Spearman's ρ between oracle and human majority-vote rankings on the 20 pairs. Bootstrap 95% CI (10,000 samples). Report Krippendorff's α among human raters as a validity check on the human-rating data.

5. **Robustness check.** Repeat H1 analysis using Davies-Bouldin as the outcome measure (lower = better; flip the comparison direction). If conclusions diverge between Silhouette and Davies-Bouldin, report both and note the discrepancy.

6. **Per-turn trajectory analysis (exploratory).** Plot median Silhouette by turn number for Conditions B and C. Identify whether improvement is front-loaded (turn 1–2) or distributed. No formal test; descriptive only.

---

## 9. What This Design Does Not Rule Out

The following alternative explanations are **not** eliminated by this design. They must be disclosed as limitations in the final report.

| Alternative explanation | Why it is not ruled out |
|---|---|
| **Experimenter demand effects (Condition B).** The team member conducting Condition B sessions knows the study hypothesis and may unconsciously issue more effective instructions. | We do not use blind experimenters or naive users. Condition C (oracle) partially mitigates this, but the oracle prompt was written by the same team. |
| **Oracle self-agreement bias (H3).** The LLM oracle used to evaluate cluster pairs in H3 is the same model used to generate Condition C cluster assignments. It may prefer its own output style. | We cannot randomise the evaluating model in this study. The bias is flagged; future work should use a different model for evaluation. |
| **Fixed-K confound.** Fixing K = 8 may advantage the conversational conditions if a user's refinements effectively move the solution closer to the "true" K, whatever that is. | K is fixed to make conditions comparable, but this means we are not testing whether conversational refinement helps users find a better K. This is a scope limitation, not a flaw. |
| **Feature encoding choices.** The one-hot encoding of actor names and event types may introduce high-dimensional noise that k-means handles poorly regardless of refinement. | We do not test alternative encodings (e.g., target encoding, embeddings) in this study. The encoding is held constant to isolate the interaction effect. |
| **Prompt sensitivity (oracle and interpreter).** Results may be sensitive to the specific wording of the interpreter and oracle prompts. | We use a single prompt version. Prompt sensitivity is an open question identified in `docs/related_work.md` (§3) and is not addressed here. |
| **Sample non-representativeness.** The 2,000-event random sample from the Russia-Ukraine GED subset may not represent the full dataset's distributional properties. | Sample size was chosen for feasibility. Results generalise to the sample; generalisation to the full dataset or other conflicts is not claimed. |

---

## 10. Ethical Considerations

- **Dataset.** The UCDP GEDEvent 25.1 dataset is publicly available, covers no individual persons, and is published by Uppsala University under an academic data-sharing agreement. No IRB review is required for its use.
- **Human raters.** Raters will view descriptions of real conflict events including fatality estimates. A brief content warning will precede the rating form. Participation is voluntary; raters may withdraw at any time. Consent procedure documented in `docs/ethics_note.md`.
- **LLM processing of conflict data.** The dataset contains descriptions of violent events. Safety filters on the LLM API may affect processing of specific event descriptions. Any refused completions will be logged and reported as data loss in the final analysis rather than silently dropped.

---

## 11. Open Questions (to resolve before data collection begins)

- [ ] Confirm final size of Russia-Ukraine GED subset and verify that N = 2,000 is below the full filtered count (so random sampling applies).
- [ ] Pre-run elbow method to fix K = 8 (or revise K before committing v0.2 of this document).
- [ ] Finalise oracle prompt (`prompts/oracle_user.md`) and interpreter prompt (`prompts/interpreter.md`) and commit before any Condition B or C runs.
- [ ] Confirm rater recruitment pathway and timeline.
- [ ] Document experimenter assignment order (`config/experimenter_order.txt`).

---

## 12. Document Status and Amendment Procedure

This document is in **draft (pre-registration)** status. It becomes locked when the first experimental run log entry is written to `runs/run_log.jsonl`. After that point, any change to the analysis plan must be recorded as a numbered amendment in the table below, with a rationale.

| Amendment | Date | Description | Rationale |
|---|---|---|---|
| A-002 | 2026-05-29 | **Post-hoc exploratory analyses added.** Four additional analyses planned after Condition B data collection began: (1) instruction taxonomy comparing B vs C instruction categories; (2) feature weight trajectory over turns for B and C; (3) instruction-weight alignment check validating the interpreter prompt; (4) per-turn silhouette delta analysis. All four are explicitly labeled **exploratory** and do not modify H1, H2, or H3. The pre-registered confirmatory analysis plan in §8 is unchanged. Full specification in `docs/study_plan.md §11`. |
| A-001 | 2026-05-22 | **Model version inconsistency between Condition A and Condition C runs.** Condition A runs (60 runs, seeds 0–29, F1+F2) were executed while `config/model.yaml` still contained the string `claude-sonnet-4-20250514`. The string was subsequently corrected to `claude-sonnet-4-5` (commit `b90e7c0`). All Condition C runs use `claude-sonnet-4-5`. The two strings refer to the same underlying model family; the format change was a naming correction, not a model upgrade. **Impact:** Condition A does not call the LLM at any point (it is a one-shot k-means run), so the logged model string in Condition A records is informational only and has no effect on any computed metric. No replication of Condition A is required. The discrepancy is reported here for transparency and completeness of the audit trail. |
