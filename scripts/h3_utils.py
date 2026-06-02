from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


EXPECTED_PAIR_COUNT = 20


def run_id(condition: str, feature_set: str, seed: int) -> str:
    return f"{condition}_{feature_set}_seed{int(seed):03d}"


def side_payload(pair: dict, side: str) -> dict:
    payload = pair[side]
    return {
        "condition": str(payload["condition"]),
        "feature_set": str(payload["feature_set"]),
        "seed": int(pair["seed"]),
        "run_id": run_id(payload["condition"], payload["feature_set"], int(pair["seed"])),
    }


def ensure_can_write(paths: Iterable[Path], overwrite: bool) -> None:
    existing = sorted(str(path) for path in paths if path.exists())
    if existing and not overwrite:
        joined = "\n  ".join(existing)
        raise FileExistsError(
            "Refusing to overwrite existing outputs without --overwrite:\n"
            f"  {joined}"
        )


def load_json(path: Path, description: str) -> object:
    if not path.exists():
        raise FileNotFoundError(f"Missing {description}: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_pairs_and_randomization(
    pairs_path: Path,
    randomization_path: Path,
) -> tuple[list[dict], list[dict]]:
    pairs = load_json(pairs_path, "pairs JSON")
    randomization = load_json(randomization_path, "randomization JSON")

    if not isinstance(pairs, list) or not isinstance(randomization, list):
        raise ValueError("pairs.json and randomization_log.json must both contain JSON arrays.")

    if len(pairs) != EXPECTED_PAIR_COUNT or len(randomization) != EXPECTED_PAIR_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_PAIR_COUNT} pairs and {EXPECTED_PAIR_COUNT} randomization rows, "
            f"got {len(pairs)} and {len(randomization)}."
        )

    metadata_rows = build_pair_metadata_rows(pairs, randomization)
    seen_pair_ids = {row["pair_id"] for row in metadata_rows}
    if len(seen_pair_ids) != EXPECTED_PAIR_COUNT:
        raise ValueError("Duplicate pair_id detected while building H3 metadata.")

    return pairs, randomization


def build_pair_metadata_rows(pairs: list[dict], randomization: list[dict]) -> list[dict]:
    rows: list[dict] = []

    for index, (pair, randomized) in enumerate(zip(pairs, randomization), start=1):
        pair_num = int(randomized.get("pair"))
        if pair_num != index:
            raise ValueError(
                f"Randomization pair mismatch at position {index}: expected {index}, got {pair_num}."
            )

        option_a_side = str(randomized.get("option_A_is"))
        if option_a_side not in {"left", "right"}:
            raise ValueError(f"Invalid option_A_is for pair {index}: {option_a_side!r}")
        option_b_side = "right" if option_a_side == "left" else "left"

        left = side_payload(pair, "left")
        right = side_payload(pair, "right")
        option_a = side_payload(pair, option_a_side)
        option_b = side_payload(pair, option_b_side)

        rows.append(
            {
                "pair_id": f"pair_{index:02d}",
                "group": str(pair["group"]),
                "seed": int(pair["seed"]),
                "left_side": "left",
                "left_run_id": left["run_id"],
                "left_condition": left["condition"],
                "left_feature_set": left["feature_set"],
                "right_side": "right",
                "right_run_id": right["run_id"],
                "right_condition": right["condition"],
                "right_feature_set": right["feature_set"],
                "option_A_side": option_a_side,
                "option_A_run_id": option_a["run_id"],
                "option_A_condition": option_a["condition"],
                "option_A_feature_set": option_a["feature_set"],
                "option_B_side": option_b_side,
                "option_B_run_id": option_b["run_id"],
                "option_B_condition": option_b["condition"],
                "option_B_feature_set": option_b["feature_set"],
            }
        )

    return rows


def validate_pair_text_files(pair_dir: Path) -> None:
    missing: list[str] = []
    for pair_num in range(1, EXPECTED_PAIR_COUNT + 1):
        for side in ("left", "right"):
            path = pair_dir / f"pair_{pair_num:02d}_{side}.txt"
            if not path.exists():
                missing.append(str(path))

    if missing:
        joined = "\n  ".join(missing)
        raise FileNotFoundError(f"Missing H3 pair text files:\n  {joined}")
