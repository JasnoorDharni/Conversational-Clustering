# Data Provenance, Ethics, and Exploration — UCDP GEDEvent 25.1

**Project:** Conversational Clustering  
**Document:** `docs/data_provenance.md`  
**Version:** v0.1  
**Status:** Committed before any experimental runs

---

## Changelog

| Version | Date | Summary |
|---|---|---|
| v0.1 | 2026-05-19 | Initial provenance and ethics note. EDA summary statistics to be filled in after the team downloads the dataset and runs `data/eda_ucdp_ukraine.py`. Placeholders marked [EDA]. |

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
| **Raw file MD5** | [EDA — fill in after download; computed by `data/eda_ucdp_ukraine.py`] |
| **Sample file MD5** | [EDA — fill in after running EDA script] |

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

*This section is populated after running `python data/eda_ucdp_ukraine.py`. Placeholder values are marked [EDA].*

### 5.1 Global dataset size

| | Value |
|---|---|
| Global GED 25.1 events (all conflicts, 1989–2024) | [EDA] |
| Events in Ukraine (country_id = 369) | [EDA] |
| Events in Ukraine ≥ 2022-02-24 (our analysis subset) | [EDA] |
| Date range of subset | [EDA] |
| Duplicate event IDs | [EDA] |

### 5.2 Event type distribution

| Type | Label | Count | % |
|---|---|---|---|
| 1 | State-based conflict | [EDA] | [EDA] |
| 2 | Non-state conflict | [EDA] | [EDA] |
| 3 | One-sided violence | [EDA] | [EDA] |

*Expected: the overwhelming majority of events in the Russia-Ukraine post-invasion period will be type 1 (state-based). Type 3 (one-sided violence against civilians) will be a meaningful minority. Type 2 will be rare.*

### 5.3 Fatality distribution

| Statistic | `best` estimate |
|---|---|
| Min | [EDA] |
| Median | [EDA] |
| Mean | [EDA] |
| 99th percentile | [EDA] |
| Max | [EDA] |
| Events with best = 0 | [EDA] (%) |

*Known pattern: fatality distributions in conflict datasets are heavy-tailed and right-skewed. Most events record 1–5 deaths; a small number of major engagements record hundreds. Log transformation will be applied for clustering (see `docs/study_plan.md` §4.2).*

### 5.4 Geographic precision

| Precision code | Meaning | Count | % |
|---|---|---|---|
| 1 | Village / town | [EDA] | [EDA] |
| 2 | ADM2 (raion) | [EDA] | [EDA] |
| 3 | ADM1 (oblast) | [EDA] | [EDA] |
| 4 | Country centroid | [EDA] | [EDA] |

*A high proportion of precision-1 events indicates good spatial resolution. Precision-3 and 4 events assigned to oblast or country centroids will introduce artificial spatial clustering — a known data artifact to flag in the results.*

### 5.5 Top oblasts by event count (adm_1)

[EDA — top 10 oblasts table]

*Expected: Donetsk, Zaporizhzhia, Kherson, Kharkiv, and Luhansk oblasts will dominate, reflecting the geographic concentration of frontline fighting.*

### 5.6 Actor landscape

[EDA — top 10 side_a actors]

*Expected: "Government of Ukraine" and "Government of Russia" will be the dominant Side A actors by event count. Volunteer battalions, territorial defense units, and Wagner Group may appear as distinct actors in a minority of events.*

### 5.7 where_description field quality

| Statistic | Value |
|---|---|
| Non-null entries | [EDA] (%) |
| Median length (chars) | [EDA] |
| Mean length (chars) | [EDA] |

*This informs the open question in `docs/study_plan.md` §7: whether `where_description` is rich enough to embed. If median length is below ~20 characters, the field is likely too sparse for sentence embeddings to add information beyond the structured geographic fields.*

### 5.8 Key data quality observations

[EDA — to be filled in after running the script. Expected observations to check:]
- [ ] Null rate in `adm_1` (should be near 0 for Ukraine events).
- [ ] Null rate in `latitude` / `longitude` (should be 0; all GED events are fully geocoded).
- [ ] Null rate in `best` (should be 0; `best` is always populated when an event exists).
- [ ] Whether any events have `best = 0` (possible if all deaths are in `low` or `high` only).
- [ ] Whether actor names contain comma-separated multiple actors (affects one-hot encoding cardinality).

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
- How many instances? GED 25.1 contains data covering 1989–2024 globally; our subset: [EDA] events.
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

- [ ] Raw file downloaded from https://ucdp.uu.se/downloads/ and placed at `data/raw/GEDEvent_v25_1.csv`.
- [ ] `python data/eda_ucdp_ukraine.py` run successfully; all outputs in `data/eda_outputs/`.
- [ ] Raw file MD5 recorded in §1.1 of this document.
- [ ] Sample file MD5 recorded in §1.1 and in `data/eda_outputs/eda_summary.txt`.
- [ ] `data/sample_seed42.csv` committed to the repository.
- [ ] EDA placeholder fields (§5) filled in from `data/eda_outputs/eda_summary.txt`.
- [ ] All figures from `data/eda_outputs/` reviewed by the team; notable patterns and anomalies noted in §5.8.
