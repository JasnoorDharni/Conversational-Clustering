# Related Work — Conversational Clustering on UCDP GEDEvent 25.1

**Project:** Conversational Clustering\
**Current version:** v0

---

## Changelog

| Version | Date | Summary |
| --- | --- | --- |
| v0 | 2026-05-14 | Initial anchor set committed at Sprint 1. Six thematic clusters identified (interactive/conversational clustering, LLM-as-evaluator, internal validity indices, conflict event datasets, human-in-the-loop ML, LLM-enhanced semantic clustering). Anchor references per cluster, with one-line takes and an explicit open-questions list. No positioning paragraph yet — deferred to v1 once the experimental design stabilises. |

---

## 1. Overview

This document surveys the literature adjacent to our project along six threads:

1. **Interactive and conversational clustering** — systems that let users guide cluster formation through natural language or structured feedback (historical context).
2. **LLM-as-evaluator** — using language models as proxy raters in the absence of ground truth.
3. **Internal cluster validity indices** — the evaluation metrics we rely on (Silhouette, Davies-Bouldin) and their known limitations.
4. **Conflict event datasets and the UCDP GED** — prior uses of the dataset relevant to feature choice.
5. **Human-in-the-loop machine learning** — the broader methodological tradition our interactive loop belongs to.
6. **LLM-Enhanced and Semantic Intent-Driven Clustering (NEW)** — the recent state-of-the-art shift towards using LLMs not just for evaluation, but to actively extract features, generate constraints, and align clusters with complex human semantics.

The document will be updated to v1 by the end of Sprint 2, at which point it will include a positioning paragraph ("prior work X measured Y using method Z; we differ in…") and notes on methodological precedents for specific instruments.

---

## 2. Anchor References

### Thread 1 — Interactive and Conversational Clustering *(Pre-LLM Context)*

**\[1\] Cohn, M., Chang, M., Kauchak, D. (2017). Active learning for interactive cluster refinement.** *Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP).Take:* Proposes an active-learning loop where a system queries the user for pairwise must-link / cannot-link constraints to refine text clusters. Closest methodological ancestor to our refinement loop — their constraint vocabulary (merge / split / isolate) maps directly to the natural-language instructions we anticipate. Key difference: they use explicit binary constraints, we use free-form text interpreted by an LLM.

**\[2\] Andrienko, N., & Andrienko, G. (2006). *Exploratory Analysis of Spatial and Temporal Data: A Systematic Approach*. Springer**.*Take:* Canonical reference for interactive visual analytics on spatio-temporal data, including georeferenced event data. Informs our understanding of what a non-conversational baseline for geographic clustering looks like, and motivates why users struggle to tune spatial vs. thematic feature weights by hand — the core motivation for our system.

**\[3\] Choo, J., Lee, C., Reddy, C. K., & Park, H. (2013). UTOPIAN: User-driven topic modeling based on interactive nonnegative matrix factorization. *IEEE Transactions on Visualization and Computer Graphics*, 19(12), 1992–2001**.*Take:* Demonstrates interactive refinement of topic models (a cousin of clustering) through direct user manipulation. Shows that iterative human feedback converges to more interpretable clusters than one-shot automated methods on text data.

**\[4\] Amershi, S., Cakmak, M., Knox, W. B., & Kulesza, T. (2014). Power to the people: The role of humans in interactive machine learning. *AI Magazine*, 35(4), 105–120**.*Take:* Broad survey of interactive ML paradigms — the paper that establishes the vocabulary we use (feedback modes, convergence, interpretability).

---

### Thread 2 — LLM-as-Evaluator

**\[5\] Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., … & Stoica, I. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *arXiv:2306.05685*.**\
*Take:* The foundational paper on using GPT-4 as a proxy judge for model output quality. Reports high agreement with human raters on open-ended tasks. Directly motivates our RQ2 and our ρ &gt; 0.7 threshold — their correlation figures set the empirical bar for "acceptable proxy agreement." Key caveat they raise: the oracle is biased toward its own output style, which may distort preference scores. Relevant to our Condition C (LLM oracle as simulated user).

**\[6\] Guo, Z., Jin, R., Liu, C., Huang, Y., Shi, D., Yu, L., … & Xu, W. (2023). Evaluating large language models: A comprehensive survey. *arXiv:2310.19736*.**\
*Take:* Survey of LLM evaluation paradigms including reference-free, oracle-based, and human-in-the-loop variants. Useful for framing where our oracle evaluation fits in the broader landscape and for anticipating failure modes (position bias, verbosity bias, cultural priors).

**\[7\] Chiang, C.-H., & Lee, H.-Y. (2023). Can large language models be an alternative to human evaluations? *Proceedings of ACL 2023*, 15607–15631.**\
*Take:* Directly tests whether LLM ratings can substitute for human ratings on NLP tasks. Finds moderate to high correlation in some settings and low correlation in others — the nuance here informs the phrasing of H3 and why we treat ρ &gt; 0.7 as a non-trivial threshold rather than a foregone conclusion.

---

### Thread 3 — Internal Cluster Validity Indices

**\[8\] Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*, 20, 53–65.**\
*Take:* Original paper defining the Silhouette coefficient, our primary outcome measure in H1. We use it because it is reference-free (no ground truth needed), interpretable as a \[-1, 1\] score, and widely reproduced. Its known weakness — sensitivity to cluster shape assumptions — is relevant when clustering geographic + categorical mixed data; we note this as a limitation.

**\[9\] Davies, D. L., & Bouldin, D. W. (1979). A cluster separation measure. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 1(2), 224–227.**\
*Take:* Defines the Davies-Bouldin index, our secondary outcome measure. Complements Silhouette because it penalises clusters that are compact but close together, a failure mode relevant to geographic event data where nearby events may belong to distinct operational categories.

**\[10\] Arbelaitz, O., Gurrutxaga, I., Muguerza, J., Pérez, J. M., & Perona, I. (2013). An extensive comparative study of cluster validity indices. *Pattern Recognition*, 46(1), 243–256.**\
*Take:* Benchmarks 30 internal validity indices across many dataset types. Key finding: no single index dominates; Silhouette and Davies-Bouldin are among the most robust across mixed data types. Justifies our choice of these two as a paired primary/secondary measure rather than picking a single index.

---

### Thread 4 — UCDP GED and Conflict Event Data

**\[11\] Sundberg, R., & Melander, E. (2013). Introducing the UCDP Georeferenced Event Dataset. *Journal of Peace Research*, 50(4), 523–532.**\
*Take:* The original methodological paper describing GED coding rules, unit of analysis (organised violence event), and known data quality issues (reporting bias in conflict zones, retroactive revision). Essential reading for data ethics and for understanding which features are reliable enough to use in clustering.

**\[12\] Croicu, M., & Sundberg, R. (2017). UCDP GED Codebook version 18.1. Uppsala Conflict Data Program, Uppsala University.**\
*Take:* Authoritative codebook for all variable definitions. We consult this when choosing feature encodings for `event_type`, `side_a`/`side_b`, and `where_description`. Informs the preliminary encoding strategy in study plan §4.2.

---

### Thread 5 — Human-in-the-Loop ML and Evaluation Without Ground Truth

**\[13\] Settles, B. (2012). Active Learning. *Synthesis Lectures on Artificial Intelligence and Machine Learning*. Morgan & Claypool.**\
*Take:* Standard reference for active learning theory, including convergence bounds and query strategies. We cite this when explaining why our conversational loop is epistemically different from passive automated tuning — each user instruction is an information-efficient oracle query. Also useful for framing the "without ground truth" evaluation challenge referenced in Session 11 of the course.

**\[14\] Krippendorff, K. (2004). *Content Analysis: An Introduction to Its Methodology* (2nd ed.). Sage.**\
*Take:* Source for Krippendorff's α, the inter-rater agreement statistic we plan to use in §4.3. We follow this methodological precedent because α handles ordinal ratings with more than two raters and missing data, which is expected given our small rater pool.

---

### Thread 6 — LLM-Enhanced and Semantic Intent-Driven Clustering *(The Modern SOTA)*

**\[15\] Zhang, Y., et al. (2023). ClusterLLM: Large Language Models as a Guide for Text Clustering.** *Proceedings of EMNLP 2023.Take:* A foundational paper showing that LLMs can guide text clustering not by processing all data, but by evaluating small triplets of texts to dynamically tune the underlying embedding space. Crucial baseline for our work: they use LLMs as a "guide" for mathematical clustering, whereas we want to test a fully conversational/semantic loop.

**\[16\] Viswanathan, V., et al. (2023). Large Language Models Enable Few-Shot Clustering.** *arXiv:2307.00524.Take:* Demonstrates that giving an LLM a tiny natural language prompt (e.g., "cluster by military tactic") allows it to autonomously generate thousands of pseudo-constraints for traditional clustering algorithms, reducing human effort by 90%. This directly validates our core assumption: LLMs can map semantic intent to clustering constraints better than geometric distances.

**\[17\] Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure.** *arXiv:2203.05794* (Specifically the recent LLM representation updates). *Take:* The dominant framework for modern text clustering. Uses HDBSCAN for clustering and LLMs *post-hoc* to label the clusters. We cite this to clarify our positioning: BERTopic does "LLM-labeling of geometric clusters", while our project investigates "LLM-driven semantic clustering from the ground up".

---

## 3. What We Do Not Yet Know About the Field

The following threads exist but have not been surveyed:

- **Constraint-based clustering algorithms** (COP-k-means, COBRAS, MustLink/CannotLink frameworks) — we know they handle user-supplied constraints directly, but we have not read enough to say whether they are a better algorithmic baseline than plain k-means for condition A.
- **Prompt sensitivity in LLM-as-judge settings** — \[5\] reports high aggregate agreement, but we have not surveyed work on how much oracle rankings shift when the prompt is paraphrased. This matters for the reliability of our Condition C.
- **Evaluation of clustering on mixed geographic-categorical-numeric data** — \[10\] benchmarks on standard UCI datasets; we do not know whether their conclusions hold for conflict event data specifically.
- **Prior uses of GEDEvent for clustering or unsupervised analysis** — we know GED is used extensively in conflict studies for regression and event counts, but we have not confirmed whether any prior work has applied clustering to the Russia-Ukraine subset.
- **Bootstrapped confidence intervals for Silhouette scores** — our plan calls for 30 replications and CI reporting (H1); we have not identified a canonical methodological reference for this specific practice in the clustering literature.
- **Embedding strategies for the** `where_description` **text field** — we note sentence-transformers as a candidate encoder (study plan §4.2) but have not reviewed which embedding model performs best on geographic/conflict text.
- **Context Window Limits and Cost in Conversational Clustering (NEW)** — we do not yet know how the SOTA handles the token limits when an LLM is asked to re-cluster an entire dataset dynamically. We need to explore if recent work uses map-reduce architectures or iterative sampling.
- **Safety Filters on Conflict Data (NEW)** — GED dataset contains violent and sensitive descriptions. We do not know to what extent commercial LLMs (GPT-4/Claude) will refuse to process this specific subset of data due to alignment filters, potentially skewing the evaluation pipeline.

---

## 4. Notes for v1 (Sprint 2 targets)

- Add positioning paragraph: for each anchor reference in threads 1–2 **and 6**, write one sentence on how our work differs.
- Expand thread 4 with any papers found to have applied clustering to GED or similar conflict datasets.
- Resolve open thread on COP-k-means / COBRAS as potential algorithmic baselines.
- Add methodological precedent note for bootstrap CI procedure (H1) once a reference is identified.
- **Review the Few-Shot Clustering (Viswanathan) and ClusterLLM (Zhang) papers to solidify our H1 and H2 baselines.**
- If a specific LLM is chosen for the interpreter and oracle (study plan §7, open question 3), add a citation for its system card or technical report.