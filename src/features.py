"""
src/features.py
---------------
Feature encoding for the UCDP GEDEvent clustering study.

F1 — Location-only:
    latitude, longitude (continuous, min-max normalised)
    adm_1 (one-hot encoded)

F2 — Full:
    F1 + type_of_violence (one-hot)
        + side_b (one-hot, top-N actors by frequency)
        + best (fatality estimate, min-max normalised)

    Note: side_a is constant in this dataset (always "Government of Ukraine"
    or "Russia"), so it is excluded from F2 to avoid a zero-variance column.
    This was confirmed in EDA (eda_summary.txt: side_a cardinality = 1).

Feature weights:
    Each feature group can be scaled by a weight (default 1.0).
    Weights are applied AFTER normalisation, so they act as soft emphases
    rather than changing the raw scale. The interpreter LLM returns a weight
    dict; this module applies them before clustering.

Public API:
    build_feature_matrix(df, feature_set, weights=None, top_n_actors=20)
        -> np.ndarray  (n_events × n_features), column_names: list[str]
    default_weights(feature_set) -> dict[str, float]
    toy_dataframe(n=120, seed=0) -> pd.DataFrame
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder


# ── Public constants ──────────────────────────────────────────────────────

FEATURE_GROUPS = {
    "F1": ["latitude", "longitude", "adm1"],
    "F2": ["latitude", "longitude", "adm1", "event_type", "actor", "fatalities"],
}


def default_weights(feature_set: str) -> dict[str, float]:
    """Return a weight dict with all groups set to 1.0."""
    return {group: 1.0 for group in FEATURE_GROUPS[feature_set]}


# ── Main entry point ──────────────────────────────────────────────────────

def build_feature_matrix(
    df: pd.DataFrame,
    feature_set: str,
    weights: dict[str, float] | None = None,
    top_n_actors: int = 20,
) -> tuple[np.ndarray, list[str]]:
    """
    Encode df into a numeric feature matrix ready for k-means.

    Parameters
    ----------
    df           : DataFrame with UCDP GED columns (or toy columns).
    feature_set  : "F1" or "F2".
    weights      : Dict mapping feature-group name -> float multiplier.
                   Missing keys default to 1.0.
    top_n_actors : For F2, keep only the top-N side_b actors by frequency;
                   all others are collapsed into "other".

    Returns
    -------
    X            : np.ndarray, shape (n_events, n_features), float64.
    col_names    : list of column names matching X's columns.
    """
    if feature_set not in FEATURE_GROUPS:
        raise ValueError(f"feature_set must be 'F1' or 'F2', got {feature_set!r}")

    w = default_weights(feature_set)
    if weights:
        w.update(weights)

    blocks: list[np.ndarray] = []
    col_names: list[str] = []

    # ── Continuous: latitude & longitude ─────────────────────────────────
    lat_lon = df[["latitude", "longitude"]].copy().fillna(0.0)
    scaled = MinMaxScaler().fit_transform(lat_lon) * w["latitude"]  # same weight for both
    blocks.append(scaled)
    col_names += ["latitude_norm", "longitude_norm"]

    # ── Categorical: adm_1 (oblast) ───────────────────────────────────────
    adm1_vals = df["adm_1"].fillna("unknown").astype(str).values.reshape(-1, 1)
    enc_adm1 = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    adm1_enc = enc_adm1.fit_transform(adm1_vals) * w["adm1"]
    blocks.append(adm1_enc)
    col_names += [f"adm1_{c}" for c in enc_adm1.categories_[0]]

    if feature_set == "F2":
        # ── Categorical: type_of_violence ─────────────────────────────────
        tov_vals = df["type_of_violence"].fillna(1).astype(str).values.reshape(-1, 1)
        enc_tov = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        tov_enc = enc_tov.fit_transform(tov_vals) * w["event_type"]
        blocks.append(tov_enc)
        col_names += [f"tov_{c}" for c in enc_tov.categories_[0]]

        # ── Categorical: side_b (top-N actors) ───────────────────────────
        top_actors = (
            df["side_b"].value_counts().head(top_n_actors).index.tolist()
        )
        side_b = df["side_b"].where(df["side_b"].isin(top_actors), other="other")
        side_b = side_b.fillna("other").astype(str).values.reshape(-1, 1)
        enc_actor = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        actor_enc = enc_actor.fit_transform(side_b) * w["actor"]
        blocks.append(actor_enc)
        col_names += [f"actor_{c}" for c in enc_actor.categories_[0]]

        # ── Continuous: best (fatalities) ────────────────────────────────
        fat = df["best"].fillna(0.0).clip(lower=0).values.reshape(-1, 1)
        fat_scaled = MinMaxScaler().fit_transform(fat) * w["fatalities"]
        blocks.append(fat_scaled)
        col_names += ["fatalities_norm"]

    X = np.hstack(blocks).astype(np.float64)
    return X, col_names


# ── Toy data generator (used by toy.yaml smoke test) ─────────────────────

def toy_dataframe(n: int = 120, seed: int = 0) -> pd.DataFrame:
    """
    Generate a synthetic DataFrame with the same column names as sample_seed42.csv.
    Used by run_experiment.py when config data_path == 'TOY'.
    Creates 3 obvious geographic clusters (west / east / south Ukraine)
    so Condition A always produces a non-trivial silhouette score.
    """
    rng = np.random.default_rng(seed)

    cluster_centres = [
        (50.45, 30.52),   # Kyiv area
        (48.00, 37.80),   # Donetsk area
        (46.48, 30.73),   # Odesa area
    ]
    oblasts = ["Kyivska", "Donetska", "Odeska"]
    actors  = ["Government of Russia", "Armed Forces of Ukraine", "Wagner Group",
               "DPR Forces", "LPR Forces", "other"]

    rows = []
    per_cluster = n // 3
    for i, (lat_c, lon_c) in enumerate(cluster_centres):
        for _ in range(per_cluster):
            rows.append({
                "latitude":          lat_c  + rng.normal(0, 0.5),
                "longitude":         lon_c  + rng.normal(0, 0.5),
                "adm_1":             oblasts[i],
                "type_of_violence":  rng.choice([1, 3], p=[0.95, 0.05]),
                "side_b":            rng.choice(actors),
                "best":              int(rng.exponential(2)),
            })

    return pd.DataFrame(rows)
