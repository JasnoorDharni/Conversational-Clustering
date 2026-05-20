"""
src/cluster.py
--------------
k-means clustering wrapper for the conversational clustering study.

Wraps sklearn KMeans with the exact settings fixed in study_design.md §2.3:
    init='k-means++'
    n_init=10
    random_state=<seed>

Returns labels, silhouette score, and Davies-Bouldin index together so the
calling code never has to remember to compute both.

Public API:
    run_kmeans(X, K, seed) -> ClusterResult
    summarise_clusters(df, labels, K) -> str   (human-readable cluster summary
                                                 for LLM interpreter prompt)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score


# ── Result dataclass ──────────────────────────────────────────────────────

@dataclass
class ClusterResult:
    labels: np.ndarray          # shape (n_events,), int cluster ids 0..K-1
    silhouette: float
    davies_bouldin: float
    K: int
    seed: int

    def as_dict(self) -> dict:
        return {
            "silhouette":      round(self.silhouette, 6),
            "davies_bouldin":  round(self.davies_bouldin, 6),
            "K":               self.K,
            "seed":            self.seed,
        }


# ── Main clustering function ──────────────────────────────────────────────

def run_kmeans(X: np.ndarray, K: int, seed: int) -> ClusterResult:
    """
    Run k-means with the parameters fixed in study_design.md §2.3.

    Parameters
    ----------
    X    : Feature matrix, shape (n_events, n_features).
    K    : Number of clusters (fixed at 8 in the study; 3 for toy).
    seed : Random seed for KMeans initialisation. Recorded in every log entry.

    Returns
    -------
    ClusterResult with labels, silhouette, davies_bouldin.

    Raises
    ------
    ValueError if n_events < K (can't have more clusters than samples).
    """
    n_events = X.shape[0]
    if n_events < K:
        raise ValueError(
            f"Cannot form {K} clusters from {n_events} events. "
            "Reduce K or increase the dataset size."
        )

    km = KMeans(
        n_clusters=K,
        init="k-means++",
        n_init=10,
        random_state=seed,
    )
    labels = km.fit_predict(X)

    # silhouette_score requires at least 2 distinct labels
    n_distinct = len(set(labels))
    if n_distinct < 2:
        sil = 0.0
        db  = float("inf")
    else:
        sil = float(silhouette_score(X, labels, sample_size=min(2000, n_events),
                                     random_state=seed))
        db  = float(davies_bouldin_score(X, labels))

    return ClusterResult(labels=labels, silhouette=sil,
                         davies_bouldin=db, K=K, seed=seed)


# ── Cluster summary for LLM prompts ──────────────────────────────────────

def summarise_clusters(
    df: pd.DataFrame,
    labels: np.ndarray,
    K: int,
    n_events_per_cluster: int = 3,
) -> str:
    """
    Build a plain-text summary of current clusters for injection into
    the interpreter and oracle prompts ({cluster_summary} variable).

    For each cluster reports:
      - cluster id and size
      - most common adm_1 (oblast)
      - most common side_b actor
      - mean fatalities (if 'best' column is present)
      - n_events_per_cluster representative events

    Parameters
    ----------
    df                   : Original DataFrame (same row order as labels).
    labels               : Cluster assignment array from run_kmeans().
    K                    : Number of clusters.
    n_events_per_cluster : How many representative events to show per cluster.
    """
    df = df.copy()
    df["_cluster"] = labels

    lines: list[str] = [f"Current clustering: K={K} clusters\n"]

    for k in range(K):
        sub = df[df["_cluster"] == k]
        size = len(sub)

        top_oblast = (
            sub["adm_1"].value_counts().index[0]
            if "adm_1" in sub.columns and not sub["adm_1"].isna().all()
            else "unknown"
        )
        top_actor = (
            sub["side_b"].value_counts().index[0]
            if "side_b" in sub.columns and not sub["side_b"].isna().all()
            else "unknown"
        )
        mean_fat = (
            f"{sub['best'].mean():.1f}"
            if "best" in sub.columns
            else "n/a"
        )

        lines.append(
            f"Cluster {k}  (n={size})  "
            f"dominant oblast: {top_oblast}  |  "
            f"dominant actor: {top_actor}  |  "
            f"mean fatalities: {mean_fat}"
        )

        # Sample representative events
        sample = sub.sample(min(n_events_per_cluster, size), random_state=0)
        for _, row in sample.iterrows():
            date  = str(row.get("date_start", ""))[:10]
            loc   = row.get("adm_1", "?")
            actor = row.get("side_b", "?")
            fat   = row.get("best", "?")
            lines.append(f"    • {date}  {loc}  vs {actor}  fatalities={fat}")

        lines.append("")

    return "\n".join(lines)
