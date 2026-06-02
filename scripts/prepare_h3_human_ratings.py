#!/usr/bin/env python
"""
Prepare H3 human-rating inputs.

Reads a Google Forms CSV export and H3 pair metadata, then writes:
  - runs/h3/human/ratings_wide.csv
  - runs/h3/metadata.csv

Run from the repository root:
  python scripts/prepare_h3_human_ratings.py --input "Conflict Event Clustering - Rating Task.csv" --overwrite
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

from h3_utils import (
    EXPECTED_PAIR_COUNT,
    build_pair_metadata_rows,
    ensure_can_write,
    load_pairs_and_randomization,
    validate_pair_text_files,
)


PAIR_COL_RE = re.compile(r"Pair\s+(\d{1,2})", re.IGNORECASE)


def normalise_choice(value: object) -> str:
    if pd.isna(value):
        return ""

    text = re.sub(r"\s+", " ", str(value).strip().upper())
    if re.fullmatch(r"(OPTION\s+)?A\b.*", text):
        return "A"
    if re.fullmatch(r"(OPTION\s+)?B\b.*", text):
        return "B"
    raise ValueError(f"Unexpected rating value: {value!r}. Expected Option A / Option B.")


def derive_human_summary(human_df: pd.DataFrame) -> pd.DataFrame:
    rater_cols = [column for column in human_df.columns if column.startswith("rater_")]
    rows = []

    for _, row in human_df.iterrows():
        choices = row[rater_cols].tolist()
        n_a = choices.count("A")
        n_b = choices.count("B")
        rows.append(
            {
                "pair_id": row["pair_id"],
                "n_A": n_a,
                "n_B": n_b,
                "majority": "A" if n_a > n_b else "B" if n_b > n_a else "TIE",
                "agreement_share": max(n_a, n_b) / len(choices),
                "n_raters": len(choices),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Google Forms CSV export path.")
    parser.add_argument("--pairs-json", default="runs/h3_pairs/pairs.json")
    parser.add_argument("--randomization-json", default="runs/h3_pairs/randomization_log.json")
    parser.add_argument("--pair-dir", default="runs/h3_pairs")
    parser.add_argument("--out-human", default="runs/h3/human/ratings_wide.csv")
    parser.add_argument("--out-summary", default="")
    parser.add_argument("--out-metadata", default="runs/h3/metadata.csv")
    parser.add_argument("--expected-raters", type=int, default=5)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    pairs_path = Path(args.pairs_json)
    randomization_path = Path(args.randomization_json)
    pair_dir = Path(args.pair_dir)
    out_human = Path(args.out_human)
    out_summary = Path(args.out_summary) if args.out_summary else None
    out_metadata = Path(args.out_metadata)

    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    outputs_to_check = [out_human, out_metadata]
    if out_summary is not None:
        outputs_to_check.append(out_summary)
    ensure_can_write(outputs_to_check, overwrite=args.overwrite)
    validate_pair_text_files(pair_dir)
    pairs, randomization = load_pairs_and_randomization(pairs_path, randomization_path)

    raw = pd.read_csv(input_path).dropna(axis=0, how="all")
    if raw.empty:
        raise ValueError(f"No rows found in human ratings CSV: {input_path}")

    pair_cols: list[tuple[int, str]] = []
    for col in raw.columns:
        match = PAIR_COL_RE.search(col)
        if match:
            pair_cols.append((int(match.group(1)), col))
    pair_cols = sorted(pair_cols, key=lambda item: item[0])

    if len(pair_cols) != EXPECTED_PAIR_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_PAIR_COUNT} pair columns, found {len(pair_cols)}: {pair_cols}"
        )

    expected_pair_numbers = list(range(1, EXPECTED_PAIR_COUNT + 1))
    actual_pair_numbers = [pair_num for pair_num, _ in pair_cols]
    if actual_pair_numbers != expected_pair_numbers:
        raise ValueError(f"Expected pair numbers 1..20, found {actual_pair_numbers}")

    if len(raw) != args.expected_raters:
        raise ValueError(
            f"Expected exactly {args.expected_raters} raters, found {len(raw)}. "
            "If this is intentional, rerun with --expected-raters."
        )

    human_rows = []
    for pair_num, col in pair_cols:
        values = [normalise_choice(value) for value in raw[col].tolist()]
        if any(value == "" for value in values):
            raise ValueError(f"Missing answer detected in pair {pair_num:02d}")

        row = {"pair_id": f"pair_{pair_num:02d}"}
        for index, choice in enumerate(values, start=1):
            row[f"rater_{index}"] = choice
        human_rows.append(row)

    human_df = pd.DataFrame(human_rows)
    rater_cols = [column for column in human_df.columns if column.startswith("rater_")]
    invalid_values = set()
    for column in rater_cols:
        invalid_values.update(
            value
            for value in human_df[column].astype(str).str.strip().str.upper().unique().tolist()
            if value not in {"A", "B"}
        )
    if invalid_values:
        raise ValueError(f"Invalid normalized human choices found: {sorted(invalid_values)}")

    summary_df = derive_human_summary(human_df)
    if (summary_df["majority"] == "TIE").any():
        tied_pairs = summary_df.loc[summary_df["majority"] == "TIE", "pair_id"].tolist()
        raise ValueError(f"Tied majority vote detected for pairs: {tied_pairs}")

    metadata_df = pd.DataFrame(build_pair_metadata_rows(pairs, randomization))
    if not metadata_df["pair_id"].is_unique:
        raise ValueError("Duplicate pair_id detected in H3 pair metadata.")

    metadata_df = metadata_df.merge(summary_df[["pair_id", "majority", "agreement_share"]], on="pair_id", how="left")
    metadata_df["human_majority_displayed_choice"] = metadata_df["majority"]
    metadata_df["human_majority_side"] = metadata_df.apply(
        lambda row: row["option_A_side"] if row["majority"] == "A" else row["option_B_side"],
        axis=1,
    )
    metadata_df["human_majority_run_id"] = metadata_df.apply(
        lambda row: row["option_A_run_id"] if row["majority"] == "A" else row["option_B_run_id"],
        axis=1,
    )

    out_human.parent.mkdir(parents=True, exist_ok=True)
    human_df.to_csv(out_human, index=False)
    if out_summary is not None:
        out_summary.parent.mkdir(parents=True, exist_ok=True)
        summary_df.to_csv(out_summary, index=False)
    metadata_df.to_csv(out_metadata, index=False)

    print(f"Wrote {out_human} ({len(human_df)} pairs, {len(rater_cols)} raters)")
    if out_summary is not None:
        print(f"Wrote {out_summary}")
    print(f"Wrote {out_metadata}")


if __name__ == "__main__":
    main()
