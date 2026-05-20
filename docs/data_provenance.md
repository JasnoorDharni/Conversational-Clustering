# Data Provenance, Ethics, and Exploration — UCDP GEDEvent 25.1

**Project:** Conversational Clustering  
**Document:** `docs/data_provenance.md`  
**Version:** v0.3  
**Status:** EDA complete — all §5 placeholders filled

---

## Changelog

| Version | Date | Summary |
|---|---|---|
| v0.1 | 2026-05-19 | Initial provenance and ethics note. EDA summary statistics to be filled in after the team downloads the dataset and runs `data/eda_ucdp_ukraine.py`. Placeholders marked [EDA]. |
| v0.2 | 2026-05-20 | EDA completed. Filled §5.1–§5.3 and §5.8 confirmed findings from initial `eda_summary.txt`. Sections §5.4–§5.7 remained pending. |
| v0.3 | 2026-05-20 | All pending placeholders filled from updated `eda_summary.txt` (notebook re-run with tabular output for geo-precision, oblasts, actors, `where_description`). §5.8 checklist fully ticked. Reproducibility checklist complete. |

---

## 1. Dataset Provenance

### 1.1 Source

| Field | Value |
|---|---|
| **Full name** | UCDP Georeferenced Event Dataset (GED), version 25.1 |
| **Abbreviation** | UCDP GED 25.1 |
| **Producer** | Uppsala Conflict Data Program (UCDP), Department of Peace and Conflict Research, Uppsala University |
| **Download URL** | https://ucdp.uu.se/downloads/ |
| **Codebook URL** | https://ucdp.uu.se/downloads/ged/ged251.pdf |
| **Coverage** | Global, 1989-01-01 – 2024-12-31 |
| **Data extracted from UCDP systems** | 2025-03-19 (per codebook cover) |
| **File used** | `GEDEvent_v25_1.csv` (CSV format) |
| **Raw file MD5** | `56d33581a615c8e3772b7500c8a2c1c6` |
| **Sample file MD5** | `a92a9a2dc2bec3a0dfa3accb6759daf0` |

### 1.2 Required Citations

All uses of this dataset must cite both:

> Sundberg, Ralph, and Erik Melander (2013). "Introducing the UCDP Georeferenced Event Dataset." *Journal of Peace Research*, 50(4), 523–532.

> Högbladh, Stina (2025). "UCDP GED Codebook version 25.1." Department of Peace and Conflict Research, Uppsala University.

The companion annual update paper should also be cited when referencing the 2024 data:

> Davies, S., Pettersson, T., Sollenberg, M., & Öberg, M. (2025). "Organized violence 1989–2024, and the challenges of identifying civilian victims." *Journal of Peace Research*, 62(4).

### 1.3 License and Terms of Use

UCDP datasets are made available for academic, non-commercial use under UCDP's standard terms of use. Access requires free registration at https://ucdp.uu.se/. The dataset may not be redistributed without permission. We will not publish the raw dataset file in the project repository; we will publish only the derived sample (`data/sample_seed42.csv`) and summary statistics, which is standard practice for academic replication packages using UCDP data.

### 1.4 How the Data Was Collected by UCDP

Understanding UCDP's collection methodology is essential for interpreting clustering results.

UCDP collects event data through a two-pass source process:

**First pass (global newswires and BBC Monitoring):** Events are coded initially from wire services (AFP, AP, Reuters) and the BBC Monitoring Service, which provides translated reports from local media worldwide. This pass ensures broad global coverage but is biased toward events that attract international media attention.

**Second pass (specialized regional sources):** UCDP staff consult regional and local sources — local newspapers, NGO reports, government announcements, academic literature — to supplement and correct the first pass. The second pass is more complete for conflicts with established local media ecosystems.

**Known systematic bias — reporting lag and conflict intensity.** Events in high-intensity phases of the Russia-Ukraine conflict (e.g., major offensives) are likely better reported than lower-intensity periods. Covert operations, small-unit actions, and events in areas with media access restrictions will be systematically underrepresented. This means our clustering may find "well-documented clusters" rather than "operationally distinct clusters."

**Known systematic bias — spatial precision degradation.** GED assigns a geo-precision code (1 = village/town, 2 = ADM2, 3 = ADM1, 4 = country centroid) reflecting the precision of the location in the source. Events with low precision (codes 3–4) are assigned coordinates at a larger geographic unit's centroid. For a conflict like Russia-Ukraine — which was heavily covered internationally — most events should be at precision 1 or 2, but events in contested or access-restricted areas may be coded at ADM1 precision. Spatial clustering on low-precision events will conflate events that may have occurred far apart. **Mitigation:** We report the geo-precision distribution in §3.4 and flag it as a limitation when interpreting geographic clusters.

**Known systematic bias — fatality underestimation.** UCDP tends to be highly conservative in fatality estimates (using the `best` estimate, not `high`). Battles with disputed casualty counts will have `best` close to `low`. The `best` estimate is the appropriate field for our analysis, but users should not interpret it as the true death toll.

**Retroactive revision.** UCDP revises past events as better sources become available. Version 25.1 represents the state of the data as of March 2025; a future version may recode some 2022–2024 events. We pin to 25.1 throughout.

---

## 2. Ethics Note

### 2.1 Dataset ethics

**Personal data.** The UCDP GED dataset contains no personal identifying information. The unit of analysis is an organized violence *event*, not an individual person. Actors are identified by organizational name (e.g., "Government of Ukraine," "Wagner Group"), not by individual combatants. The `where_description` field is a geographic description, not a personal identifier. **No anonymization is required.**

**Sensitivity of content.** The dataset describes violent events including fatalities, attacks on civilians (type_of_violence = 3), and one-sided violence. The data is factual and academic; it is the same dataset used in peer-reviewed conflict research. However:
- LLM processing of event descriptions may encounter content that triggers safety filters. Any refusals by the Claude API when processing event text must be logged and reported as data loss (not silently dropped). See `docs/related_work.md` §3, open question on "Safety Filters on Conflict Data."
- Cluster labels auto-generated by the LLM from event content should be reviewed before being shown to human raters, to ensure they do not inadvertently minimize or sensationalize violence.

**IRB classification.** The UCDP GED dataset is publicly available, covers no individual persons, involves no deception, and is published by an academic institution under standard terms. **No IRB review is required for use of the dataset itself.** This classification follows standard practice in quantitative conflict studies.

**Attribution and dual-use.** The dataset is designed for academic analysis of conflict patterns. We use it for a methodological study (clustering algorithm evaluation); we do not make causal or policy claims about the conflict. Results should not be interpreted as a definitive operational picture of the war.

### 2.2 Human rater ethics

**Who are the raters.** Raters are course peers recruited voluntarily. They will view descriptions of real conflict events, including fatality estimates and descriptions of violent incidents.

**Consent procedure.** Before accessing the rating form, raters will see a one-page information sheet explaining: (1) the purpose of the study; (2) the nature of the content they will view (descriptions of conflict events, not graphic imagery); (3) that participation is voluntary and they may stop at any time; (4) how their data will be used (aggregated ratings only; no individual rater identified in publications). Raters must click "I agree to participate" before seeing the first pair.

**Data collected.** The rating form collects: forced-choice preference per pair (A or B); optional free-text comments. No names, emails, or demographic information are collected. Ratings are stored in an anonymized form (rater ID assigned at form entry, not linked to identity).

**Sensitive content warning.** The rating form includes a header: *"This study involves descriptions of military conflict events including references to casualties. If you find this content distressing, you are free to stop at any time."*

**Data retention.** Rating data will be stored in the project repository (anonymized) and may be included in the final report as aggregated statistics. No individual-level data will be published.

**Consent artifact.** The information sheet is committed to `docs/rater_consent_form.md` before any rater is recruited. It will not be modified after the first rater completes it.

---

## 3. Dataset Structure and Variable Dictionary

The following variables are present in UCDP GED 25.1 and are relevant to this project. The full variable list is documented in the [official codebook](https://ucdp.uu.se/downloads/ged/ged251.pdf).

| Variable | Type | Description | Used in clustering? |
|---|---|---|---|
| `id` | integer | Unique event identifier | No (identifier only) |
| `year` | integer | Year of event | No (derived from date_start) |
| `date_start` | date | First date of the event | Filter variable; temporal feature (exploratory) |
| `date_end` | date | Last date of the event | Not used |
| `type_of_violence` | integer (1/2/3) | 1=state-based, 2=non-state, 3=one-sided | **Yes — F2 feature set** |
| `conflict_name` | string | Name of the conflict | Not used directly |
| `dyad_name` | string | Pair of conflicting actors | Not used directly |
| `side_a` | string | Name of Side A actor (always government in state-based) | **Yes — F2 feature set** |
| `side_b` | string | Name of Side B actor | **Yes — F2 feature set** |
| `country` | string | Country name where event occurred | Filter variable |
| `country_id` | integer | Gleditsch-Ward country code | Filter variable (369 = Ukraine) |
| `adm_1` | string | First-order administrative division (oblast) | **Yes — F1 and F2** |
| `adm_2` | string | Second-order administrative division (raion) | F2 (supplementary) |
| `latitude` | float | Latitude of event (geocoded) | **Yes — F1 and F2** |
| `longitude` | float | Longitude of event (geocoded) | **Yes — F1 and F2** |
| `geo_precision` | integer (1–4) | Spatial precision of geocoding (1=best) | Quality indicator; not a clustering feature |
| `best` | integer | Best fatality estimate | **Yes — F2 feature set** |
| `low` | integer | Low fatality estimate | Not used (use `best`) |
| `high` | integer | High fatality estimate | Not used (use `best`) |
| `deaths_civilians` | integer | Civilian deaths (subset of `best`) | Not used in clustering |
| `deaths_a` | integer | Deaths on Side A | Not used in clustering |
| `deaths_b` | integer | Deaths on Side B | Not used in clustering |
| `where_description` | string | Text description of the event location | Candidate for embedding (open question) |
| `source_original` | string | Primary source for the event | Not used |
| `active_year` | integer (0/1) | Whether the dyad was in an active year | Not used |

---

## 4. Filtering and Sampling Procedure

### 4.1 Filter criteria

```
country_id == 369          # Ukraine (Gleditsch-Ward code)
AND date_start >= 2022-02-24  # Full-scale invasion start date
```

The filter is applied before any other processing. Events in Russia itself (country_id = 365) are excluded because GED coverage of events occurring on Russian soil is expected to be sparse and may reflect a different reporting regime.

### 4.2 Sample

A random sample of **N = 2,000 events** is drawn from the filtered subset using `random_state=42`. The sampling is performed by `data/eda_ucdp_ukraine.py` and the resulting file is committed to `data/sample_seed42.csv`.

If the filtered subset contains fewer than 2,000 events (unlikely given the scale of the conflict), the full filtered subset is used and downsampling is not applied.

**Rationale for N = 2,000.** This is large enough for k-means to produce stable cluster structure while remaining computationally tractable for 180 experimental runs (30 seeds × 3 conditions × 2 feature sets). Full details in `docs/study_design.md` §5.1.

### 4.3 Held-out split declaration

**The experimental sample (`data/sample_seed42.csv`) is the only data used in any experimental run.** No held-out test split is required for this study design, because:
- The primary outcome (Silhouette score) is an internal validity measure computed on the clustering itself, not a predictive accuracy measure on unseen data.
- Human rating (H3) is conducted on a 20-pair subset of clustering results, not on held-out events.

This is consistent with standard practice in unsupervised learning evaluation studies, where a train/test split is not meaningful without a predictive model.

**What is locked before analysis begins:** The sample file (`data/sample_seed42.csv`) is committed and its MD5 hash recorded before any experimental run is executed. Any analysis must use this exact file; re-drawing the sample is a protocol violation.

---

## 5. Exploratory Data Analysis — Results

*EDA complete (v0.3). All fields populated from `data/eda_outputs/eda_summary.txt`. No pending placeholders remain.*

### 5.1 Global dataset size

| | Value |
|---|---|
| Global GED 25.1 events (all conflicts, 1989–2024) | 385,918 |
| Events in Ukraine (country_id = 369) | — (all post-filter; see below) |
| Events in Ukraine ≥ 2022-02-24 (our analysis subset) | 27,942 |
| Date range of subset | 2022-02-24 – 2024-12-31 |
| Duplicate event IDs | 0 |

### 5.2 Event type distribution

| Type | Label | Count | % |
|---|---|---|---|
| 1 | State-based conflict | 27,716 | 99.2% |
| 2 | Non-state conflict | 0 | 0.0% |
| 3 | One-sided violence | 226 | 0.8% |

*The distribution confirms the expected pattern: virtually all events are state-based (type 1), reflecting the interstate character of the Russia-Ukraine conflict. One-sided violence against civilians (type 3) constitutes a small but meaningful minority (226 events, 0.8%). Non-state conflict (type 2) is entirely absent in this subset, consistent with the conflict's structure. The near-total dominance of type 1 means `type_of_violence` will contribute very low variance as a clustering feature; this should be noted when interpreting F2 feature-set results.*

### 5.3 Fatality distribution

| Statistic | `best` estimate |
|---|---|
| Min | 0 |
| Median | 2.0 |
| Mean | 8.4 |
| 99th percentile | 74 |
| Max | 15,996 |
| Events with best = 0 | 206 (0.7%) |

*The distribution is strongly right-skewed, as expected for conflict event data. The median of 2 deaths per event confirms that most engagements are small-scale, while the maximum of 15,996 and the 99th percentile gap (74 vs. 15,996) indicate a small number of catastrophic outliers that will dominate a linear scale. **Log transformation of `best` is confirmed as necessary** before clustering, as specified in `docs/study_plan.md` §4.2. The 206 zero-fatality events (0.7%) require a decision on log-transform handling (e.g., log(best + 1)); this is pre-specified in the encoding strategy.*

### 5.4 Geographic precision

| Precision code | Meaning | Count | % |
|---|---|---|---|
| 1 | Village / town | 24,275 | 86.9% |
| 2 | ADM2 (raion) | 2,860 | 10.2% |
| 3 | ADM1 (oblast) | 807 | 2.9% |
| 4 | Country centroid | 0 | 0.0% |

97.1% of events are coded at precision 1 or 2, meaning geographic coordinates are reliable for the large majority of the subset. The 807 precision-3 events (2.9%) are assigned to oblast centroids and will cluster artificially at a small number of fixed points — a known data artifact to flag when interpreting geographic clusters. No events are assigned to the country centroid (precision 4), which is a positive quality indicator for this high-coverage conflict.

### 5.5 Top oblasts by event count (adm_1)

*Top oblasts by event count (adm_1), full filtered subset (N = 27,942):*

| Oblast | Count | % |
|---|---|---|
| Donetsk oblast | 13,731 | 49.1% |
| Kharkiv oblast | 3,125 | 11.2% |
| Kherson oblast | 2,731 | 9.8% |
| Luhansk oblast | 2,327 | 8.3% |
| Zaporizhzhya oblast | 2,295 | 8.2% |
| Sumy oblast | 366 | 1.3% |
| Dnipropetrovsk oblast | 325 | 1.2% |
| Mykolayiv oblast | 270 | 1.0% |
| Chernihiv oblast | 261 | 0.9% |
| Kyiv oblast | 255 | 0.9% |

The top 3 oblasts (Donetsk, Kharkiv, Kherson) account for 70.1% of all events, confirming extreme geographic concentration along the eastern and southern front lines. This concentration is a design consideration for k-means with K = 8: clusters in Donetsk oblast will likely be further subdivided by sub-regional or actor features rather than geography alone. The 1,910 events with null `adm_1` (6.84% — see §5.8) are excluded from adm_1-based features; these events retain valid latitude/longitude coordinates.

### 5.6 Actor landscape

*Top `side_a` actors, full filtered subset:*

| Actor | Count | % |
|---|---|---|
| Government of Russia (Soviet Union) | 27,942 | 100.0% |

`side_a` is entirely dominated by a single actor — the Government of Russia appears in 100% of events, consistent with the state-based conflict type that makes up 99.2% of the subset (§5.2). This means the `side_a` one-hot column will be a zero-variance feature and should be dropped from the F2 feature set before clustering.

`side_b` cardinality is substantially higher, reflecting the variety of Ukrainian government, military, and territorial defence units coded as the opposing actor. The `side_b` one-hot encoding will produce a sparse matrix with a small number of high-frequency entries (Government of Ukraine and its armed forces) alongside many low-frequency entries. Truncation to the top-N actors by frequency (as specified in `docs/study_design.md §2.2`) is confirmed as necessary.

Comma-separated actor names: 0 entries in both `side_a` and `side_b` (0.0%), so one-hot encoding does not require multi-label handling.

### 5.7 where_description field quality

| Statistic | Value |
|---|---|
| Non-null entries | 27,139 / 27,942 (97.1%) |
| Empty strings | 0 |
| Median length (chars) | 32 |
| Mean length (chars) | 46.3 |
| Entries < 10 chars | 2,821 (10.4%) |

97.1% of events have a non-null `where_description`. However, 10.4% of those entries are under 10 characters — too short to carry useful semantic content beyond what the structured `adm_1`/`adm_2` fields already provide. The median length of 32 characters and mean of 46.3 characters indicate descriptions are generally brief geographic references rather than rich narrative text. This resolves the open question in `docs/study_plan.md §7`: embedding `where_description` is feasible for the ~90% of entries exceeding 10 characters, but the incremental value over structured geographic features is expected to be modest. The decision to embed or exclude this field should be finalised before the first experimental run.

### 5.8 Key data quality observations

*EDA completed. Confirmed observations:*

- [x] **Duplicate IDs: 0.** No duplicate event IDs in the filtered subset (27,942 events, 0 duplicates confirmed by EDA script).
- [x] **`best` is fully populated.** 206 events have `best = 0` (0.7%), confirming the field is non-null throughout but that zero-fatality records exist. Log(best + 1) transform is required.
- [x] **Event type is near-constant.** Type 2 (non-state conflict) has zero occurrences; type 1 accounts for 99.2%. The `type_of_violence` one-hot column will contribute negligible variance in F2 clustering — effectively a near-zero-variance feature. Consider whether to retain or drop it from F2.
- [x] **Sample successfully drawn.** N = 2,000 events sampled with seed 42 from the 27,942-event filtered subset (14.3% sample fraction). Sample MD5 confirmed (`a92a9a2dc2bec3a0dfa3accb6759daf0`).
- [x] **Null rate in `adm_1`: 1,910 nulls (6.84%).** These events retain valid coordinates and will contribute to geographic features but not to adm_1 one-hot columns. Imputation is not required; null adm_1 rows are handled by dropping the adm_1 column entry for those events.
- [x] **Null rate in `latitude` / `longitude`: 0 (0.00%).** Confirmed by EDA script. All events have valid coordinates — geographic features are fully usable without imputation.
- [x] **Actor name comma-separation: 0 entries in both `side_a` and `side_b` (0.0%).** No multi-actor entries exist; one-hot encoding does not require multi-label handling.

---

## 6. Known Limitations and Biases to Disclose in the Final Report

1. **Media access bias.** Events in areas with restricted media access (e.g., active front lines, Russian-controlled territory) are systematically underreported relative to events near population centers with functioning media. Clusters identified from GED data reflect the *observable* conflict, not the full conflict.

2. **Temporal incompleteness.** GED 25.1 covers through 2024-12-31. Events near the end of the period may not yet be fully coded due to the second-pass review lag. The most recent months in the dataset may have lower event counts than earlier periods, not because the conflict was less intense, but because second-pass coding was not complete at the time of the 2025-03-19 data extraction.

3. **Actor name inconsistency.** Actor names in GED are standardized by UCDP, but may not capture the full diversity of units involved (e.g., different Ukrainian territorial defense brigades may be aggregated under "Government of Ukraine"). One-hot encoding of actor names will treat two events labeled "Government of Ukraine" as identical along the actor dimension, regardless of which specific unit was involved.

4. **Spatial precision heterogeneity.** Mixing precision-1 (village-level) and precision-3 (oblast centroid) events in the same geographic feature space is methodologically problematic. Events at precision 3 are effectively jittered to an arbitrary point within a large region. This is noted as a limitation; robustness analysis by geo-precision level is deferred to future work.

5. **No ground truth.** The dataset has no canonical clustering. This is the definitional motivation for the study (see `docs/study_plan.md` §1) but also means we cannot compute accuracy or F1 against a true partition.

---

## 7. Data Card (Gebru et al. style)

*Following the structure of Gebru, T., et al. (2021). "Datasheets for Datasets." Communications of the ACM, 64(12), 86–92.*

**Motivation**
- For what purpose was the dataset created? To provide a globally consistent, geocoded record of organized violent events for academic conflict research.
- Who created it? Uppsala Conflict Data Program, Uppsala University, funded in part by DEMSCORE (Swedish Research Council grant 2021-00162).
- Who funded it? Swedish Research Council and Uppsala University.

**Composition**
- What does each instance represent? One organized violence event — a discrete incident of lethal violence between organized actors at a specific location and date.
- How many instances? GED 25.1 contains 385,918 events globally (1989–2024); our filtered subset: 27,942 events (Ukraine, ≥ 2022-02-24); experimental sample: 2,000 events.
- Does the dataset contain all instances, or a sample? It aims to be comprehensive but has known reporting-bias gaps (see §1.4).
- Is there a label? No ground-truth cluster labels. Violence type (state-based / non-state / one-sided) is a field, not a label.
- Is any information missing? Events in access-restricted zones are systematically underrepresented. See §1.4.
- Are there known errors? UCDP maintains an errata process; version 25.1 incorporates corrections through March 2025.

**Collection process**
- How was the data collected? Systematic coding from global newswires (first pass) and specialized regional sources (second pass). See §1.4.
- Who did the data collection? UCDP research staff.
- Over what timeframe? Data for 2024 was extracted 2025-03-19. Earlier years were coded over many release cycles.

**Preprocessing**
- Was any preprocessing done? UCDP applies geocoding, source deduplication, and quality assurance. See codebook §4.4.
- Is the raw data available? Yes, from https://ucdp.uu.se/downloads/.

**Uses**
- Has the dataset been used before? Yes, extensively in quantitative conflict research (regression, survival analysis, predictive modeling). Not known to have been used for clustering specifically on the Russia-Ukraine subset.
- What tasks is it not appropriate for? Identifying individual combatants; real-time operational intelligence; definitive casualty accounting.

**Distribution**
- How is it distributed? Free download with registration from Uppsala University.
- Is it under copyright? UCDP terms of use apply. Academic non-commercial use permitted; redistribution requires permission.

**Maintenance**
- Is it maintained? Yes, updated annually. Monthly "candidate events" releases are also available (UCDP Candidate Events Dataset) but were not used in this study.
- Will older versions remain available? Yes (https://ucdp.uu.se/downloads/olddw.html).

---

## 8. Reproducibility Checklist

- [x] Raw file downloaded from https://ucdp.uu.se/downloads/ and placed at `data/raw/GEDEvent_v25_1.csv`.
- [x] `python data/eda_ucdp_ukraine.py` run successfully; all outputs in `data/eda_outputs/`.
- [x] Raw file MD5 recorded in §1.1 of this document (`56d33581a615c8e3772b7500c8a2c1c6`).
- [x] Sample file MD5 recorded in §1.1 and in `data/eda_outputs/eda_summary.txt` (`a92a9a2dc2bec3a0dfa3accb6759daf0`).
- [x] `data/sample_seed42.csv` committed to the repository.
- [x] EDA placeholder fields (§5.1–§5.3) filled in from `data/eda_outputs/eda_summary.txt`.
- [x] EDA placeholder fields (§5.4–§5.7) filled in from updated `data/eda_outputs/eda_summary.txt` (v0.3 notebook run).
- [x] All figures from `data/eda_outputs/` reviewed by the team; notable patterns and anomalies noted in §5.8.
