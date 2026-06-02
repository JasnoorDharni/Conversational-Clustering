#!/usr/bin/env python
"""
Analyze H3 oracle-human agreement.

Inputs:
  - runs/h3/human/ratings_wide.csv
  - runs/h3/metadata.csv
  - runs/h3/oracle/ratings_long.csv (optional until oracle has been run)

Outputs:
  - optional runs/h3/analysis/pair_level_results.csv
  - runs/h3/analysis/results_summary.csv
  - optional runs/h3/analysis/oracle_bias_diagnostic.png
"""

from __future__ import annotations

import argparse
import html
import math
from pathlib import Path

import numpy as np
import pandas as pd

from h3_utils import EXPECTED_PAIR_COUNT, ensure_can_write


def nominal_krippendorff_alpha(matrix: pd.DataFrame) -> float:
    values = matrix.replace({"A": 0, "B": 1, "": np.nan}).apply(pd.to_numeric, errors="coerce").to_numpy()

    observed_disagreement = 0.0
    observed_pairs = 0
    for row in values:
        valid = row[~np.isnan(row)]
        n = len(valid)
        if n < 2:
            continue
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                observed_pairs += 1
                observed_disagreement += 0.0 if valid[i] == valid[j] else 1.0

    if observed_pairs == 0:
        return math.nan

    do = observed_disagreement / observed_pairs
    all_values = values[~np.isnan(values)]
    n_total = len(all_values)
    if n_total < 2:
        return math.nan

    expected_disagreement = 0.0
    expected_pairs = 0
    for i in range(n_total):
        for j in range(n_total):
            if i == j:
                continue
            expected_pairs += 1
            expected_disagreement += 0.0 if all_values[i] == all_values[j] else 1.0

    de = expected_disagreement / expected_pairs
    if de == 0:
        return 1.0 if do == 0 else math.nan

    return 1.0 - (do / de)


def encode_ab(series: pd.Series) -> np.ndarray:
    values = series.astype(str).str.strip().str.upper()
    invalid = sorted(set(values) - {"A", "B"})
    if invalid:
        raise ValueError(f"Unexpected A/B values: {invalid}")
    return (values == "B").astype(int).to_numpy()


def encode_side(series: pd.Series) -> np.ndarray:
    values = series.astype(str).str.strip().str.lower()
    invalid = sorted(set(values) - {"left", "right"})
    if invalid:
        raise ValueError(f"Unexpected side values: {invalid}")
    return (values == "right").astype(int).to_numpy()


def safe_spearman(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    if len(set(x.tolist())) < 2 or len(set(y.tolist())) < 2:
        return math.nan, math.nan
    x_ranks = pd.Series(x).rank(method="average").to_numpy(dtype=float)
    y_ranks = pd.Series(y).rank(method="average").to_numpy(dtype=float)
    rho = float(np.corrcoef(x_ranks, y_ranks)[0, 1])
    return rho, math.nan


def safe_kappa(x: np.ndarray, y: np.ndarray) -> float:
    if len(set(x.tolist())) < 2 or len(set(y.tolist())) < 2:
        return math.nan
    labels = sorted(set(x.tolist()) | set(y.tolist()))
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    matrix = np.zeros((len(labels), len(labels)), dtype=float)

    for x_value, y_value in zip(x.tolist(), y.tolist()):
        matrix[label_to_idx[x_value], label_to_idx[y_value]] += 1.0

    total = matrix.sum()
    if total == 0:
        return math.nan

    observed = float(np.trace(matrix) / total)
    row_marginals = matrix.sum(axis=1) / total
    col_marginals = matrix.sum(axis=0) / total
    expected = float(np.sum(row_marginals * col_marginals))
    if math.isclose(1.0 - expected, 0.0):
        return math.nan
    return float((observed - expected) / (1.0 - expected))


def order_mode(values: pd.Series) -> str:
    cleaned = [str(value).strip() for value in values.tolist() if str(value).strip()]
    if not cleaned:
        return ""
    counts = pd.Series(cleaned).value_counts()
    if len(counts) > 1 and counts.iloc[0] == counts.iloc[1]:
        return ""
    return str(counts.index[0])


def summarise_oracle_order(order_df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    rows = []
    for pair_id, pair_df in order_df.groupby("pair_id"):
        rows.append(
            {
                "pair_id": pair_id,
                f"{prefix}_n_trials": int(len(pair_df)),
                f"{prefix}_display_choice": order_mode(pair_df["choice_displayed"]),
                f"{prefix}_chosen_side": order_mode(pair_df["chosen_side"]),
                f"{prefix}_chosen_run_id": order_mode(pair_df["chosen_run_id"]),
                f"{prefix}_chosen_condition": order_mode(pair_df["chosen_condition"]),
                f"{prefix}_chosen_feature_set": order_mode(pair_df["chosen_feature_set"]),
                f"{prefix}_all_display_choices": "|".join(pair_df["choice_displayed"].astype(str).tolist()),
                f"{prefix}_all_chosen_run_ids": "|".join(pair_df["chosen_run_id"].astype(str).tolist()),
                f"{prefix}_unstable_within_order": len(set(pair_df["chosen_run_id"].astype(str))) > 1,
            }
        )
    return pd.DataFrame(rows)


def h3_status(
    agreement_bias_controlled: float,
    kappa_bias_controlled: float,
    position_bias_evidence: bool,
) -> str:
    if position_bias_evidence:
        return "not_supported"
    if (
        not pd.isna(agreement_bias_controlled)
        and agreement_bias_controlled >= 0.75
        and not pd.isna(kappa_bias_controlled)
        and kappa_bias_controlled >= 0.40
    ):
        return "supported"
    if not pd.isna(agreement_bias_controlled) and agreement_bias_controlled >= 0.60:
        return "partially_supported"
    return "not_supported"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human", default="runs/h3/human/ratings_wide.csv")
    parser.add_argument("--metadata", default="runs/h3/metadata.csv")
    parser.add_argument("--oracle-long", default="runs/h3/oracle/ratings_long.csv")
    parser.add_argument("--out-majority", default="")
    parser.add_argument("--out-results", default="runs/h3/analysis/results_summary.csv")
    parser.add_argument("--out-pair-level", default="runs/h3/analysis/pair_level_results.csv")
    parser.add_argument("--out-plot", default="runs/h3/analysis/oracle_bias_diagnostic.svg")
    parser.add_argument("--write-plot", action="store_true")
    parser.add_argument("--write-pair-level", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    human_path = Path(args.human)
    metadata_path = Path(args.metadata)
    oracle_long_path = Path(args.oracle_long)
    out_majority = Path(args.out_majority) if args.out_majority else None
    out_results = Path(args.out_results)
    out_pair_level = Path(args.out_pair_level)
    out_plot = Path(args.out_plot)

    if not human_path.exists():
        raise FileNotFoundError(f"Missing human ratings: {human_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing H3 metadata: {metadata_path}")

    outputs = []
    if out_majority is not None:
        outputs.append(out_majority)
    if oracle_long_path.exists():
        outputs.append(out_results)
        if not args.write_pair_level:
            pass
        else:
            outputs.append(out_pair_level)
        if args.write_plot:
            outputs.append(out_plot)
    ensure_can_write(outputs, overwrite=args.overwrite)

    human_df = pd.read_csv(human_path)
    metadata_df = pd.read_csv(metadata_path)

    if len(human_df) != EXPECTED_PAIR_COUNT:
        raise ValueError(f"Expected {EXPECTED_PAIR_COUNT} human pairs, found {len(human_df)}.")
    if len(metadata_df) != EXPECTED_PAIR_COUNT:
        raise ValueError(f"Expected {EXPECTED_PAIR_COUNT} metadata rows, found {len(metadata_df)}.")

    rater_cols = [column for column in human_df.columns if column.startswith("rater_")]
    if len(rater_cols) != 5:
        raise ValueError(f"Expected 5 human rater columns, found {len(rater_cols)}.")

    for column in rater_cols:
        values = set(human_df[column].astype(str).str.strip().str.upper())
        if not values.issubset({"A", "B"}):
            raise ValueError(f"Invalid values in {column}: {sorted(values)}")

    alpha = nominal_krippendorff_alpha(human_df[rater_cols])
    human_majority_rows = []
    for _, row in human_df.iterrows():
        choices = [str(row[column]).strip().upper() for column in rater_cols]
        n_a = choices.count("A")
        n_b = choices.count("B")
        majority = "A" if n_a > n_b else "B" if n_b > n_a else "TIE"
        if majority == "TIE":
            raise ValueError(f"Tied human majority detected for {row['pair_id']}.")
        human_majority_rows.append(
            {
                "pair_id": row["pair_id"],
                "n_A": n_a,
                "n_B": n_b,
                "human_majority_displayed_choice": majority,
                "human_agreement_share": max(n_a, n_b) / len(choices),
                "n_raters": len(choices),
            }
        )

    majority_df = pd.DataFrame(human_majority_rows).merge(metadata_df, on="pair_id", how="left")
    majority_df["human_majority_side"] = majority_df.apply(
        lambda row: row["option_A_side"]
        if row["human_majority_displayed_choice"] == "A"
        else row["option_B_side"],
        axis=1,
    )
    majority_df["human_majority_run_id"] = majority_df.apply(
        lambda row: row["option_A_run_id"]
        if row["human_majority_displayed_choice"] == "A"
        else row["option_B_run_id"],
        axis=1,
    )
    if out_majority is not None:
        out_majority.parent.mkdir(parents=True, exist_ok=True)
        majority_df.to_csv(out_majority, index=False)
        print(f"Wrote {out_majority}")

    if not oracle_long_path.exists():
        print(f"Oracle long-form ratings not found: {oracle_long_path}")
        print("Human side is ready. Run scripts/run_h3_oracle_eval.py, then rerun this script.")
        return

    oracle_long = pd.read_csv(oracle_long_path)
    if oracle_long.empty:
        raise ValueError(f"Oracle long-form file is empty: {oracle_long_path}")
    required_long_columns = {
        "pair_id",
        "order",
        "choice_displayed",
        "chosen_side",
        "chosen_run_id",
        "chosen_condition",
        "chosen_feature_set",
    }
    missing_columns = sorted(required_long_columns - set(oracle_long.columns))
    if missing_columns:
        raise ValueError(
            f"Oracle long-form ratings are missing required columns: {missing_columns}"
        )

    oracle_original = oracle_long.loc[oracle_long["order"] == "original"].copy()
    if oracle_original.empty:
        raise ValueError("No original-order oracle rows found in long-form oracle ratings.")
    original_summary = summarise_oracle_order(oracle_original, "oracle_original")
    pair_level_df = majority_df.merge(original_summary, on="pair_id", how="left")

    oracle_swapped = oracle_long.loc[oracle_long["order"] == "swapped"].copy()
    swapped_available = not oracle_swapped.empty
    if swapped_available:
        swapped_summary = summarise_oracle_order(oracle_swapped, "oracle_swapped")
        pair_level_df = pair_level_df.merge(swapped_summary, on="pair_id", how="left")
    else:
        pair_level_df["oracle_swapped_display_choice"] = ""
        pair_level_df["oracle_swapped_chosen_side"] = ""
        pair_level_df["oracle_swapped_chosen_run_id"] = ""
        pair_level_df["oracle_swapped_unstable_within_order"] = False

    pair_level_df["oracle_matches_human_original_displayed"] = (
        pair_level_df["oracle_original_display_choice"] == pair_level_df["human_majority_displayed_choice"]
    )

    if swapped_available:
        pair_level_df["oracle_same_underlying_choice_after_swap"] = (
            pair_level_df["oracle_original_chosen_run_id"] == pair_level_df["oracle_swapped_chosen_run_id"]
        ) & pair_level_df["oracle_original_chosen_run_id"].astype(str).ne("")
        pair_level_df["oracle_same_display_label_after_swap"] = (
            pair_level_df["oracle_original_display_choice"] == pair_level_df["oracle_swapped_display_choice"]
        ) & pair_level_df["oracle_original_display_choice"].astype(str).ne("")
        pair_level_df["oracle_position_bias_flag"] = (
            pair_level_df["oracle_same_display_label_after_swap"]
            & ~pair_level_df["oracle_same_underlying_choice_after_swap"]
        )
        pair_level_df["oracle_bias_controlled_side"] = pair_level_df.apply(
            lambda row: row["oracle_original_chosen_side"]
            if (
                row["oracle_original_chosen_side"]
                and row["oracle_original_chosen_side"] == row["oracle_swapped_chosen_side"]
            )
            else "",
            axis=1,
        )
        pair_level_df["oracle_bias_controlled_run_id"] = pair_level_df.apply(
            lambda row: row["oracle_original_chosen_run_id"]
            if (
                row["oracle_original_chosen_run_id"]
                and row["oracle_original_chosen_run_id"] == row["oracle_swapped_chosen_run_id"]
            )
            else "",
            axis=1,
        )
    else:
        pair_level_df["oracle_same_underlying_choice_after_swap"] = False
        pair_level_df["oracle_same_display_label_after_swap"] = False
        pair_level_df["oracle_position_bias_flag"] = False
        pair_level_df["oracle_bias_controlled_side"] = ""
        pair_level_df["oracle_bias_controlled_run_id"] = ""

    pair_level_df["oracle_bias_controlled_matches_human_run"] = (
        pair_level_df["oracle_bias_controlled_run_id"] == pair_level_df["human_majority_run_id"]
    ) & pair_level_df["oracle_bias_controlled_run_id"].astype(str).ne("")

    if args.write_pair_level:
        pair_level_df.to_csv(out_pair_level, index=False)
        print(f"Wrote {out_pair_level}")

    original_eval_df = pair_level_df.loc[
        pair_level_df["oracle_original_display_choice"].astype(str).isin(["A", "B"])
    ].copy()
    if original_eval_df.empty:
        raise ValueError("No valid original-order oracle choices found for analysis.")

    human_original_binary = encode_ab(original_eval_df["human_majority_displayed_choice"])
    oracle_original_binary = encode_ab(original_eval_df["oracle_original_display_choice"])
    original_agreement_share = float(
        original_eval_df["oracle_matches_human_original_displayed"].mean()
    )
    original_agreement_count = int(
        original_eval_df["oracle_matches_human_original_displayed"].sum()
    )
    original_kappa = safe_kappa(human_original_binary, oracle_original_binary)
    original_rho, original_rho_p = safe_spearman(human_original_binary, oracle_original_binary)

    bias_eval_df = pair_level_df.loc[
        pair_level_df["oracle_bias_controlled_run_id"].astype(str).ne("")
    ].copy()
    excluded_pairs = int(len(pair_level_df) - len(bias_eval_df))

    if bias_eval_df.empty:
        bias_agreement_share = math.nan
        bias_agreement_count = 0
        bias_kappa = math.nan
        bias_rho = math.nan
        bias_rho_p = math.nan
    else:
        human_bias_binary = encode_side(bias_eval_df["human_majority_side"])
        oracle_bias_binary = encode_side(bias_eval_df["oracle_bias_controlled_side"])
        bias_agreement_share = float(
            bias_eval_df["oracle_bias_controlled_matches_human_run"].mean()
        )
        bias_agreement_count = int(
            bias_eval_df["oracle_bias_controlled_matches_human_run"].sum()
        )
        bias_kappa = safe_kappa(human_bias_binary, oracle_bias_binary)
        bias_rho, bias_rho_p = safe_spearman(human_bias_binary, oracle_bias_binary)

    position_bias_evidence = bool(pair_level_df["oracle_position_bias_flag"].any())
    status = h3_status(bias_agreement_share, bias_kappa, position_bias_evidence)

    if swapped_available:
        displayed_a_count = int(
            (oracle_original["choice_displayed"].astype(str).str.upper() == "A").sum()
            + (oracle_swapped["choice_displayed"].astype(str).str.upper() == "A").sum()
        )
        displayed_b_count = int(
            (oracle_original["choice_displayed"].astype(str).str.upper() == "B").sum()
            + (oracle_swapped["choice_displayed"].astype(str).str.upper() == "B").sum()
        )
    else:
        displayed_a_count = int((oracle_original["choice_displayed"].astype(str).str.upper() == "A").sum())
        displayed_b_count = int((oracle_original["choice_displayed"].astype(str).str.upper() == "B").sum())

    summary_row = {
        "n_pairs": int(len(pair_level_df)),
        "n_human_raters": int(len(rater_cols)),
        "krippendorff_alpha_humans": alpha,
        "human_majority_ties": 0,
        "oracle_original_agreement_count": original_agreement_count,
        "oracle_original_agreement_share": original_agreement_share,
        "oracle_original_cohen_kappa": original_kappa,
        "oracle_original_spearman_rho": original_rho,
        "oracle_original_spearman_p": original_rho_p,
        "oracle_bias_controlled_pairs_used": int(len(bias_eval_df)),
        "oracle_bias_controlled_pairs_excluded": excluded_pairs,
        "oracle_bias_controlled_agreement_count": bias_agreement_count,
        "oracle_bias_controlled_agreement_share": bias_agreement_share,
        "oracle_bias_controlled_cohen_kappa": bias_kappa,
        "oracle_bias_controlled_spearman_rho": bias_rho,
        "oracle_bias_controlled_spearman_p": bias_rho_p,
        "oracle_selected_displayed_A_count": displayed_a_count,
        "oracle_selected_displayed_B_count": displayed_b_count,
        "oracle_same_underlying_choice_after_swap_count": int(
            pair_level_df["oracle_same_underlying_choice_after_swap"].sum()
        ),
        "oracle_same_display_label_after_swap_count": int(
            pair_level_df["oracle_same_display_label_after_swap"].sum()
        ),
        "oracle_position_bias_pair_count": int(pair_level_df["oracle_position_bias_flag"].sum()),
        "position_bias_evidence": position_bias_evidence,
        "h3_status": status,
    }

    pd.DataFrame([summary_row]).to_csv(out_results, index=False)
    print(f"Wrote {out_results}")

    if args.write_plot:
        human_counts = pair_level_df["human_majority_displayed_choice"].value_counts()
        original_counts = pair_level_df["oracle_original_display_choice"].value_counts()
        swapped_counts = (
            pair_level_df["oracle_swapped_display_choice"].value_counts()
            if swapped_available
            else pd.Series(dtype=int)
        )

        labels = ["A", "B"]
        human_values = [int(human_counts.get(label, 0)) for label in labels]
        original_values = [int(original_counts.get(label, 0)) for label in labels]
        swapped_values = [int(swapped_counts.get(label, 0)) for label in labels]

        diagnostic_labels = [
            "Same underlying\nafter swap",
            "Same displayed\nlabel after swap",
            "Position bias\nflagged",
        ]
        diagnostic_values = [
            int(pair_level_df["oracle_same_underlying_choice_after_swap"].sum()),
            int(pair_level_df["oracle_same_display_label_after_swap"].sum()),
            int(pair_level_df["oracle_position_bias_flag"].sum()),
        ]
        out_plot.parent.mkdir(parents=True, exist_ok=True)

        def bar_svg(
            title: str,
            series: list[tuple[str, list[int], str]],
            max_value: int,
            origin_x: int,
            origin_y: int,
            panel_width: int,
            panel_height: int,
            category_labels: list[str],
        ) -> str:
            parts: list[str] = []
            chart_left = origin_x + 50
            chart_bottom = origin_y + panel_height - 40
            chart_top = origin_y + 25
            chart_height = chart_bottom - chart_top
            category_gap = 55
            bar_width = 18

            parts.append(f'<text x="{origin_x + panel_width / 2:.0f}" y="{origin_y + 18}" text-anchor="middle" font-size="15" font-family="Arial">{html.escape(title)}</text>')
            parts.append(f'<line x1="{chart_left}" y1="{chart_bottom}" x2="{origin_x + panel_width - 20}" y2="{chart_bottom}" stroke="#555" stroke-width="1"/>')
            parts.append(f'<line x1="{chart_left}" y1="{chart_top}" x2="{chart_left}" y2="{chart_bottom}" stroke="#555" stroke-width="1"/>')

            scale = chart_height / max(1, max_value)
            for tick in range(0, max_value + 1, 5):
                y = chart_bottom - tick * scale
                parts.append(f'<line x1="{chart_left - 4}" y1="{y:.1f}" x2="{chart_left}" y2="{y:.1f}" stroke="#555" stroke-width="1"/>')
                parts.append(f'<text x="{chart_left - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="10" font-family="Arial">{tick}</text>')

            for cat_index, category in enumerate(category_labels):
                base_x = chart_left + 35 + cat_index * category_gap
                for series_index, (_, values, color) in enumerate(series):
                    x = base_x + series_index * (bar_width + 4) - ((len(series) - 1) * (bar_width + 4) / 2)
                    height = values[cat_index] * scale
                    y = chart_bottom - height
                    parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width}" height="{height:.1f}" fill="{color}"/>')
                parts.append(f'<text x="{base_x + 10:.1f}" y="{chart_bottom + 16}" text-anchor="middle" font-size="11" font-family="Arial">{html.escape(category)}</text>')

            legend_x = origin_x + panel_width - 150
            legend_y = origin_y + 28
            for idx, (name, _, color) in enumerate(series):
                y = legend_y + idx * 16
                parts.append(f'<rect x="{legend_x}" y="{y - 10}" width="10" height="10" fill="{color}"/>')
                parts.append(f'<text x="{legend_x + 16}" y="{y - 1}" font-size="10" font-family="Arial">{html.escape(name)}</text>')
            return "".join(parts)

        series_left = [
            ("Human majority", human_values, "#4C78A8"),
            ("Oracle original", original_values, "#F58518"),
        ]
        if swapped_available:
            series_left.append(("Oracle swapped", swapped_values, "#54A24B"))
        series_right = [
            ("Count", diagnostic_values, "#E45756"),
        ]

        max_left = max(human_values + original_values + swapped_values + [20])
        max_right = max(diagnostic_values + [20])
        right_labels = ["Underlying", "Same label", "Bias flag"]

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="360" viewBox="0 0 920 360">
<rect width="920" height="360" fill="white"/>
<text x="460" y="22" text-anchor="middle" font-size="18" font-family="Arial" font-weight="bold">H3 Oracle Bias Diagnostic</text>
{bar_svg("Displayed-choice distribution", series_left, max_left, 20, 40, 420, 280, labels)}
{bar_svg("Swap diagnostic", series_right, max_right, 470, 40, 420, 280, right_labels)}
</svg>'''
        out_plot.write_text(svg, encoding="utf-8")
        print(f"Wrote {out_plot}")

    print("H3 summary")
    print(f"  Human Krippendorff alpha: {alpha:.3f}")
    print(
        f"  Oracle-human agreement (original order): "
        f"{original_agreement_count}/{len(original_eval_df)} = {original_agreement_share:.3f}"
    )
    if bias_eval_df.empty:
        print("  Bias-controlled agreement: nan (no stable oracle underlying choices available)")
    else:
        print(
            f"  Bias-controlled agreement: "
            f"{bias_agreement_count}/{len(bias_eval_df)} = {bias_agreement_share:.3f}"
        )
    print(f"  Position bias evidence: {position_bias_evidence}")
    print(f"  H3 status: {status}")


if __name__ == "__main__":
    main()
