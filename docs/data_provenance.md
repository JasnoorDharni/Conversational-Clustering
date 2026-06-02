# Data Provenance and Exploration - UCDP GEDEvent 25.1

**Project:** Conversational Clustering  
**Document:** `docs/data_provenance.md`  
**Version:** v0.4  
**Status:** EDA complete

---

## Changelog

| Version | Date | Summary |
|---|---|---|
| v0.1 | 2026-05-19 | Initial provenance and ethics note. |
| v0.2 | 2026-05-20 | EDA sections filled from `data/eda_outputs/eda_summary.txt`. |
| v0.3 | 2026-05-20 | Remaining EDA placeholders completed from the updated notebook outputs. |
| v0.4 | 2026-06-02 | Repository alignment pass. Project-level ethics content moved to `docs/ethics_note.md`; this document now focuses on provenance, dataset properties, and exploration. Stale script references were removed. |

---

## 1. Dataset Provenance

### 1.1 Source

| Field | Value |
|---|---|
| Full name | UCDP Georeferenced Event Dataset (GED), version 25.1 |
| Producer | Uppsala Conflict Data Program (UCDP), Uppsala University |
| Download URL | https://ucdp.uu.se/downloads/ |
| Codebook URL | https://ucdp.uu.se/downloads/ged/ged251.pdf |
| Coverage | Global, 1989-01-01 to 2024-12-31 |
| Data extracted from UCDP systems | 2025-03-19 |
| File used | `GEDEvent_v25_1.csv` |
| Raw file MD5 | `56d33581a615c8e3772b7500c8a2c1c6` |
| Sample file MD5 | `a92a9a2dc2bec3a0dfa3accb6759daf0` |

### 1.2 Required Citations

All uses of this dataset must cite both:

- Sundberg, Ralph, and Erik Melander (2013). "Introducing the UCDP Georeferenced Event Dataset." *Journal of Peace Research*, 50(4), 523-532.
- Hogbladh, Stina (2025). "UCDP GED Codebook version 25.1." Department of Peace and Conflict Research, Uppsala University.

When referencing the 2024 update, also cite:

- Davies, S., Pettersson, T., Sollenberg, M., and Oberg, M. (2025). "Organized violence 1989-2024, and the challenges of identifying civilian victims." *Journal of Peace Research*, 62(4).

### 1.3 License and Use

UCDP datasets are available for academic, non-commercial use under UCDP's terms. Access requires registration. The raw dataset is not redistributed in this repository. The repository includes only derived artifacts such as `data/sample_seed42.csv` and EDA summaries.

### 1.4 Collection Process and Known Biases

UCDP codes events through a two-pass source process:

- First pass: global newswires and BBC Monitoring.
- Second pass: regional and local sources used to supplement and correct the first pass.

Known issues relevant to this project:

- Media-access bias can underrepresent events from restricted or poorly reported areas.
- Spatial precision varies across records; lower-precision events can distort geographic clustering.
- Fatality estimates are conservative and should not be treated as exact death tolls.
- Older events may be revised in future UCDP releases, so this project is pinned to version 25.1.

---

## 2. Ethics Scope

Project-level ethics, consent, privacy, and data-handling notes are documented in `docs/ethics_note.md`. This file keeps only the provenance and exploratory-analysis details needed to understand the dataset and reproduce the EDA.

---

## 3. Dataset Structure and Variables Used

The full schema is in the official codebook. The variables most relevant here are:

| Variable | Description | Used in clustering? |
|---|---|---|
| `date_start` | Event start date | Filter variable |
| `type_of_violence` | 1=state-based, 2=non-state, 3=one-sided | Yes in F2 |
| `side_b` | Side B actor | Yes in F2 |
| `adm_1` | First-order administrative division | Yes in F1 and F2 |
| `latitude` / `longitude` | Event coordinates | Yes in F1 and F2 |
| `geo_precision` | Precision of geocoding | Quality indicator only |
| `best` | Best fatality estimate | Yes in F2 |
| `where_description` | Textual location description | Explored, not used in executed feature sets |

The executed implementation excludes `side_a`, `adm_2`, and `where_description` from the final feature matrices.

---

## 4. Filtering and Sampling Procedure

### 4.1 Filter Criteria

```text
country_id == 369
AND date_start >= 2022-02-24
```

### 4.2 Sample

A random sample of **N = 2,000 events** is drawn from the filtered subset using `random_state=42`. The workflow is documented in `notebooks/eda_ucdp_ukraine.ipynb`, and the resulting file is committed as `data/sample_seed42.csv`.

This sample is the only event table used in the experiment runs.

### 4.3 Held-out Split Declaration

No held-out test split is used. The primary outcome is internal cluster validity, and H3 evaluates pairwise cluster descriptions rather than unseen prediction targets.

---

## 5. Exploratory Data Analysis - Results

All values below come from the committed EDA outputs under `data/eda_outputs/`.

### 5.1 Global dataset size

| Measure | Value |
|---|---|
| Global GED 25.1 events | 385,918 |
| Filtered Ukraine subset, date >= 2022-02-24 | 27,942 |
| Date range of subset | 2022-02-24 to 2024-12-31 |
| Duplicate event IDs | 0 |

### 5.2 Event type distribution

| Type | Label | Count | % |
|---|---|---|---|
| 1 | State-based conflict | 27,716 | 99.2% |
| 2 | Non-state conflict | 0 | 0.0% |
| 3 | One-sided violence | 226 | 0.8% |

This confirms that `type_of_violence` carries limited variance in this subset.

### 5.3 Fatality distribution

| Statistic | `best` |
|---|---|
| Min | 0 |
| Median | 2.0 |
| Mean | 8.4 |
| 99th percentile | 74 |
| Max | 15,996 |
| Events with `best = 0` | 206 (0.7%) |

The distribution is strongly right-skewed. The executed implementation used raw `best` with min-max normalization.

### 5.4 Geographic precision

| Precision code | Meaning | Count | % |
|---|---|---|---|
| 1 | Village / town | 24,275 | 86.9% |
| 2 | ADM2 | 2,860 | 10.2% |
| 3 | ADM1 | 807 | 2.9% |
| 4 | Country centroid | 0 | 0.0% |

Most records are precise enough for geographic clustering, but the precision-3 events remain a documented limitation.

### 5.5 Top oblasts by event count

| Oblast | Count | % |
|---|---|---|
| Donetsk oblast | 13,731 | 49.1% |
| Kharkiv oblast | 3,125 | 11.2% |
| Kherson oblast | 2,731 | 9.8% |
| Luhansk oblast | 2,327 | 8.3% |
| Zaporizhzhya oblast | 2,295 | 8.2% |

The subset is heavily concentrated in eastern and southern front-line regions.

### 5.6 Actor landscape

- `side_a` is effectively constant in the filtered subset and was excluded from the executed feature set.
- `side_b` was retained but has limited effective variation relative to geography and fatalities.

### 5.7 `where_description` quality

| Statistic | Value |
|---|---|
| Non-null entries | 27,139 / 27,942 (97.1%) |
| Empty strings | 0 |
| Median length | 32 characters |
| Mean length | 46.3 characters |
| Entries under 10 chars | 2,821 (10.4%) |

The field is often short and was not used in the executed feature sets.

### 5.8 Key Data Quality Observations

- Duplicate event IDs: 0.
- `best` is fully populated, though some events have `best = 0`.
- `type_of_violence` is near-constant but retained in executed F2.
- Sample successfully drawn at N = 2,000 with seed 42.
- `adm_1` has nulls, but `latitude` and `longitude` are complete.
- No multi-actor comma-separated entries were found in `side_a` or `side_b`.

---

## 6. Known Limitations to Disclose

1. Media-access bias means clusters reflect the observable conflict, not the full conflict.
2. Temporal incompleteness near the end of the covered period may affect event counts.
3. Actor standardization can hide meaningful unit-level differences.
4. Spatial precision heterogeneity complicates geographic interpretation.
5. There is no ground-truth clustering label set.

---

## 7. Reproducibility Checklist

- [x] Raw file obtained from UCDP for the local EDA workflow; the raw file itself is not committed to this repository.
- [x] `notebooks/eda_ucdp_ukraine.ipynb` run successfully; outputs saved in `data/eda_outputs/`.
- [x] Raw file MD5 recorded in this document.
- [x] Sample file MD5 recorded in this document and `data/eda_outputs/eda_summary.txt`.
- [x] `data/sample_seed42.csv` committed to the repository.
- [x] EDA findings reflected in this document.
