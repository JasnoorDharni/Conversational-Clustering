# Related Work — Conversational Clustering on UCDP GEDEvent 25.1

**Project:** Conversational Clustering\
**Current version:** v1

---

## Changelog

| Version | Date | Summary |
| --- | --- | --- |
| v0 | 2026-05-14 | Initial anchor set committed at Sprint 1. Six thematic clusters identified (interactive/conversational clustering, LLM-as-evaluator, internal validity indices, conflict event datasets, human-in-the-loop ML, LLM-enhanced semantic clustering). Anchor references per cluster, with one-line takes and an explicit open-questions list. No positioning paragraph yet — deferred to v1 once the experimental design stabilises. |
| v1 | 2026-05-29 | Positioning paragraphs added for all six threads. Per-thread "how we differ" sentences written for references [1]–[7] and [15]–[17]. §3 updated: two open questions resolved (safety filters, context window limits) based on project execution; remaining open questions retained. §4 (notes for v1) replaced with §4 (synthesis and positioning statement) — a unified paragraph suitable for use in the final report's related work section. |

---

## 1. Overview

This document surveys the literature adjacent to our project along six threads:

1. **Interactive and conversational clustering** — systems that let users guide cluster formation through natural language or structured feedback (historical context).
2. **LLM-as-evaluator** — using language models as proxy raters in the absence of ground truth.
3. **Internal cluster validity indices** — the evaluation metrics we rely on (Silhouette, Davies-Bouldin) and their known limitations.
4. **Conflict event datasets and the UCDP GED** — prior uses of the dataset relevant to feature choice.
5. **Human-in-the-loop machine learning** — the broader methodological tradition our interactive loop belongs to.
6. **LLM-Enhanced and Semantic Intent-Driven Clustering (NEW)** — the recent state-of-the-art shift towards using LLMs not just for evaluation, but to actively extract features, generate constraints, and align clusters with complex human semantics.

This v1 update adds positioning paragraphs for each thread and a unified synthesis statement in §4.

---

## 2. Anchor References

### Thread 1 — Interactive and Conversational Clustering *(Pre-LLM Context)*

**Positioning.** Prior work in interactive clustering required users to express preferences in structured, system-defined vocabularies — binary pairwise constraints [1], GUI drag-and-drop operations [3], or explicit split/merge commands. Our system differs in accepting *free-form natural language* as the sole input channel, delegating constraint extraction to an LLM interpreter. This removes the need for users to learn any interface grammar, at the cost of introducing LLM-induced ambiguity in how instructions are translated to feature weights — a source of variability that Conditions B and C of our experiment are designed to expose. Furthermore, unlike [2] and [3] which operate on text or visual data, we apply conversational refinement to *structured tabular conflict event data*, where the distance metric is sensitive to categorical encoding choices that users cannot easily reason about without guidance.

**\[1\] Cohn, M., Chang, M., Kauchak, D. (2017). Active learning for interactive cluster refinement.** *Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP).Take:* Proposes an active-learning loop where a system queries the user for pairwise must-link / cannot-link constraints to refine text clusters. Closest methodological ancestor to our refinement loop — their constraint vocabulary (merge / split / isolate) maps directly to the natural-language instructions we anticipate. Key difference: they use explicit binary constraints, we use free-form text interpreted by an LLM.

**\[2\] Andrienko, N., & Andrienko, G. (2006). *Exploratory Analysis of Spatial and Temporal Data: A Systematic Approach*. Springer**.*Take:* Canonical reference for interactive visual analytics on spatio-temporal data, including georeferenced event data. Informs our understanding of what a non-conversational baseline for geographic clustering looks like, and motivates why users struggle to tune spatial vs. thematic feature weights by hand — the core motivation for our system.

**\[3\] Choo, J., Lee, C., Reddy, C. K., & Park, H. (2013). UTOPIAN: User-driven topic modeling based on interactive nonnegative matrix factorization. *IEEE Transactions on Visualization and Computer Graphics*, 19(12), 1992–2001**.*Take:* Demonstrates interactive refinement of topic models (a cousin of clustering) through direct user manipulation. Shows that iterative human feedback converges to more interpretable clusters than one-shot automated methods on text data.

**\[4\] Amershi, S., Cakmak, M., Knox, W. B., & Kulesza, T. (2014). Power to the people: The role of humans in interactive machine learning. *AI Magazine*, 35(4), 105–120**.*Take:* Broad survey of interactive ML paradigms — the paper that establishes the vocabulary we use (feedback modes, convergence, interpretability).

---

### Thread 2 — LLM-as-Evaluator

**Positioning.** The LLM-as-judge literature [5][6][7] has focused almost exclusively on evaluating *natural language generation* quality — fluency, factual accuracy, helpfulness of text responses. We extend this paradigm to a structurally different task: judging the quality of *cluster assignments* over structured tabular data, where the oracle must reason about geographic and actor patterns in conflict events rather than about linguistic coherence. This is a harder setting for LLM evaluation because the oracle cannot rely on surface-level textual similarity — it must infer whether a grouping of events is semantically meaningful from a sparse, schema-bound summary. Our H3 (Spearman ρ > 0.7 between oracle and human rater rankings) is directly motivated by the empirical baselines in [5] and [7], reframed for this non-text domain.

**\[5\] Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., … & Stoica, I. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *arXiv:2306.05685*.**\
*Take:* The foundational paper on using GPT-4 as a proxy judge for model output quality. Reports high agreement with human raters on open-ended tasks. Directly motivates our RQ2 and our ρ &gt; 0.7 threshold — their correlation figures set the empirical bar for "acceptable proxy agreement." Key caveat they raise: the oracle is biased toward its own output style, which may distort preference scores. Relevant to our Condition C (LLM oracle as simulated user).

**\[6\] Guo, Z., Jin, R., Liu, C., Huang, Y., Shi, D., Yu, L., … & Xu, W. (2023). Evaluating large language models: A comprehensive survey. *arXiv:2310.19736*.**\
*Take:* Survey of LLM evaluation paradigms including reference-free, oracle-based, and human-in-the-loop variants. Useful for framing where our oracle evaluation fits in the broader landscape and for anticipating failure modes (position bias, verbosity bias, cultural priors).

**\[7\] Chiang, C.-H., & Lee, H.-Y. (2023). Can large language models be an alternative to human evaluations? *Proceedings of ACL 2023*, 15607–15631.**\
*Take:* Directly tests whether LLM ratings can substitute for human ratings on NLP tasks. Finds moderate to high correlation in some settings and low correlation in others — the nuance here informs the phrasing of H3 and why we treat ρ &gt; 0.7 as a non-trivial threshold rather than a foregone conclusion.

---

### Thread 3 — Internal Cluster Validity Indices

**Positioning.** We use Silhouette [8] and Davies-Bouldin [9] as our primary and secondary outcome measures precisely because they are reference-free — there is no ground-truth partition for UCDP GED events. [10] justifies choosing both in tandem rather than a single index. One limitation that emerged during our study is that the Silhouette score rises monotonically with K on our geographically concentrated dataset (Donetsk oblast = 49.1% of events), making it unsuitable for K selection but still valid as a comparative metric across conditions at fixed K = 8. This behavior was not anticipated in the pre-registered design and is disclosed as a limitation.

**\[8\] Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*, 20, 53–65.**\
*Take:* Original paper defining the Silhouette coefficient, our primary outcome measure in H1. We use it because it is reference-free (no ground truth needed), interpretable as a \[-1, 1\] score, and widely reproduced. Its known weakness — sensitivity to cluster shape assumptions — is relevant when clustering geographic + categorical mixed data; we note this as a limitation.

**\[9\] Davies, D. L., & Bouldin, D. W. (1979). A cluster separation measure. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 1(2), 224–227.**\
*Take:* Defines the Davies-Bouldin index, our secondary outcome measure. Complements Silhouette because it penalises clusters that are compact but close together, a failure mode relevant to geographic event data where nearby events may belong to distinct operational categories.

**\[10\] Arbelaitz, O., Gurrutxaga, I., Muguerza, J., Pérez, J. M., & Perona, I. (2013). An extensive comparative study of cluster validity indices. *Pattern Recognition*, 46(1), 243–256.**\
*Take:* Benchmarks 30 internal validity indices across many dataset types. Key finding: no single index dominates; Silhouette and Davies-Bouldin are among the most robust across mixed data types. Justifies our choice of these two as a paired primary/secondary measure rather than picking a single index.

---

### Thread 4 — UCDP GED and Conflict Event Data

**Positioning.** To our knowledge, no prior published work has applied unsupervised clustering to the UCDP GED Russia-Ukraine subset. Existing uses of GED data in the literature are almost exclusively regression-based (predicting fatality counts or conflict onset) or descriptive (event counts by region and period). Our study is therefore the first to treat the GED as a clustering testbed, using it to evaluate whether conversational refinement can reveal structure that automated methods miss. The near-constant actor field (`side_a` = Government of Russia in 100% of events) is a dataset-specific constraint identified through our EDA [11][12] that limits the effective dimensionality of the F2 feature set and must be disclosed as a scope limitation.

**\[11\] Sundberg, R., & Melander, E. (2013). Introducing the UCDP Georeferenced Event Dataset. *Journal of Peace Research*, 50(4), 523–532.**\
*Take:* The original methodological paper describing GED coding rules, unit of analysis (organised violence event), and known data quality issues (reporting bias in conflict zones, retroactive revision). Essential reading for data ethics and for understanding which features are reliable enough to use in clustering.

**\[12\] Croicu, M., & Sundberg, R. (2017). UCDP GED Codebook version 18.1. Uppsala Conflict Data Program, Uppsala University.**\
*Take:* Authoritative codebook for all variable definitions. We consult this when choosing feature encodings for `event_type`, `side_a`/`side_b`, and `where_description`. Informs the preliminary encoding strategy in study plan §4.2.

---

### Thread 5 — Human-in-the-Loop ML and Evaluation Without Ground Truth

**Positioning.** Our conversational loop is a specific instantiation of the human-in-the-loop paradigm surveyed in [4] and [13]: each user instruction functions as an oracle query that reduces uncertainty about the "correct" feature weighting. Unlike classical active learning [13], which queries the user for labels on individual data points, our loop queries the user for *global preference updates* expressed as natural language — a coarser but more accessible interaction model. The inter-rater reliability measurement (Krippendorff's α, following [14]) is required before H3 analysis proceeds, ensuring that the human preference signal is reliable enough to serve as a reference for oracle evaluation.

**\[13\] Settles, B. (2012). Active Learning. *Synthesis Lectures on Artificial Intelligence and Machine Learning*. Morgan & Claypool.**\
*Take:* Standard reference for active learning theory, including convergence bounds and query strategies. We cite this when explaining why our conversational loop is epistemically different from passive automated tuning — each user instruction is an information-efficient oracle query. Also useful for framing the "without ground truth" evaluation challenge referenced in Session 11 of the course.

**\[14\] Krippendorff, K. (2004). *Content Analysis: An Introduction to Its Methodology* (2nd ed.). Sage.**\
*Take:* Source for Krippendorff's α, the inter-rater agreement statistic we plan to use in §4.3. We follow this methodological precedent because α handles ordinal ratings with more than two raters and missing data, which is expected given our small rater pool.

---

### Thread 6 — LLM-Enhanced and Semantic Intent-Driven Clustering *(The Modern SOTA)*

**Positioning.** The modern SOTA in LLM-assisted clustering [15][16][17] operates primarily on *text data* and uses the LLM to extract semantic features, generate constraints, or label clusters — all in a single automated pass without an ongoing human conversation. Our work occupies a different point in this design space: we apply LLM-assisted clustering to *structured tabular data* (geographic coordinates, administrative codes, fatality counts) and test whether an *iterative human-in-the-loop conversation* produces better results than either the automated baseline (Condition A) or a fully automated LLM oracle (Condition C). ClusterLLM [15] is the closest methodological relative — both systems use an LLM to translate user intent into clustering constraints — but ClusterLLM requires no ongoing conversation and operates over text embeddings, while our system translates free-form natural language into continuous feature weights over a structured schema. Viswanathan et al. [16] validate that LLMs can map a single NL prompt to effective clustering constraints; our Condition C can be read as a multi-turn extension of that idea, testing whether iterative refinement compounds the benefit of each individual instruction.

**\[15\] Zhang, Y., et al. (2023). ClusterLLM: Large Language Models as a Guide for Text Clustering.** *Proceedings of EMNLP 2023.Take:* A foundational paper showing that LLMs can guide text clustering not by processing all data, but by evaluating small triplets of texts to dynamically tune the underlying embedding space. Crucial baseline for our work: they use LLMs as a "guide" for mathematical clustering, whereas we want to test a fully conversational/semantic loop.

**\[16\] Viswanathan, V., et al. (2023). Large Language Models Enable Few-Shot Clustering.** *arXiv:2307.00524.Take:* Demonstrates that giving an LLM a tiny natural language prompt (e.g., "cluster by military tactic") allows it to autonomously generate thousands of pseudo-constraints for traditional clustering algorithms, reducing human effort by 90%. This directly validates our core assumption: LLMs can map semantic intent to clustering constraints better than geometric distances.

**\[17\] Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure.** *arXiv:2203.05794* (Specifically the recent LLM representation updates). *Take:* The dominant framework for modern text clustering. Uses HDBSCAN for clustering and LLMs *post-hoc* to label the clusters. We cite this to clarify our positioning: BERTopic does "LLM-labeling of geometric clusters", while our project investigates "LLM-driven semantic clustering from the ground up".

---

## 3. Open Questions and Resolved Gaps

### Resolved during project execution

- ✅ **Safety filters on conflict data.** Zero refused completions across all 180 experimental runs (30 seeds × 3 conditions × 2 feature sets). The GED event summaries passed Claude's safety filters without triggering refusals in any condition. This outcome is reported as a finding (not assumed) and removes a previously anticipated source of data loss.
- ✅ **Context window limits.** Not a practical constraint: the interpreter and oracle prompts inject a cluster *summary* (≈300–500 tokens), not the raw dataset. The 2,000-event sample never enters the context window directly; token usage per call stayed well within the 512-token budget configured in `src/llm.py`.
- ✅ **Prior uses of GEDEvent for clustering.** No published work found applying unsupervised clustering to the GED Russia-Ukraine subset. Our use is novel in this respect.

### Still open

- **Constraint-based clustering algorithms** (COP-k-means, COBRAS) — not surveyed in depth. Whether they provide a stronger automated baseline than plain k-means for Condition A remains an open question for future work.
- **Prompt sensitivity in LLM-as-judge settings** — a single oracle prompt version was used (by design). How rankings shift with prompt paraphrasing is not tested here; flagged as a limitation in `docs/study_design.md §9`.
- **Evaluation of Silhouette and Davies-Bouldin on conflict event data specifically** — [10] benchmarks on standard UCI datasets. The monotonically increasing Silhouette behavior observed in our elbow analysis (§14 of `notebooks/eda_ucdp_ukraine.ipynb`) suggests these indices behave differently on geographically concentrated data; no prior characterisation of this was found.
- **Bootstrapped CIs for Silhouette comparison** — no canonical methodological reference identified for this specific practice. We follow the general bootstrap procedure; this is noted as a methodological gap.

---

## 4. Synthesis and Positioning Statement

*(Suitable for adaptation into the related work section of the final report.)*

Prior work on interactive clustering predates LLMs and relies on structured constraint vocabularies that require users to learn system-specific interaction models [1][3][4]. The LLM-assisted clustering literature [15][16][17] has recently demonstrated that language models can translate semantic intent into effective clustering constraints, but these systems operate on text data and do not involve an ongoing human conversation. The LLM-as-evaluator literature [5][6][7] has validated proxy evaluation for natural language generation quality, but has not been tested on structured clustering tasks. Our work sits at the intersection of these three streams: we apply a *multi-turn conversational refinement loop*, interpreted by an LLM, to *structured tabular conflict event data*, and evaluate the result using both internal validity indices [8][9][10] and an LLM oracle whose correlation with human judgment is tested directly (H3). The dataset [11][12] is novel for this type of analysis — to our knowledge no prior work has used the UCDP GED as a clustering testbed — and the near-constant actor structure of the Russia-Ukraine subset introduces a dimensionality constraint that limits the effective levers available to conversational refinement. The LLM used as interpreter and oracle is `claude-sonnet-4-5` (Anthropic, 2025); its system card is the appropriate citation for model-specific capabilities and safety properties.