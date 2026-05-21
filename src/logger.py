"""
src/logger.py
-------------
Structured JSONL logging for the conversational clustering study.

Every completed run appends exactly ONE record to run_log.jsonl.
Every record includes:
    run_id, condition, feature_set, K, seed,
    config_hash, prompt_hashes,
    model_version, timestamp_start/end,
    silhouette_final, davies_bouldin_final,
    n_turns_completed, turns[],
    errors[], status

'status' values:
    "complete"  — all turns finished, metrics recorded
    "refused"   — LLM returned a safety refusal; logged as data loss
    "error"     — unrecoverable error (logged with traceback fragment)
    "partial"   — run started but not all turns completed (e.g. KeyboardInterrupt)

Public API:
    RunLogger(log_path, config, prompt_paths)  — context manager per run
        .log_turn(turn_n, instruction, parsed_params, silhouette, db, tokens)
        .finish(result)         — writes the complete record
        .refuse(reason)         — writes a refused record
        .fail(exc)              — writes an error record
"""

from __future__ import annotations

import hashlib
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonlines


# ── Helpers ───────────────────────────────────────────────────────────────

def _sha7(path: str | Path) -> str | None:
    """Return the first 7 hex chars of the SHA-256 of a file's contents.
    Returns None if the file does not exist or path is empty/a directory."""
    if not path:
        return None
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    return h[:7]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── RunLogger ─────────────────────────────────────────────────────────────

class RunLogger:
    """
    Context manager that accumulates per-turn data and writes a single
    JSONL record at the end of each run.

    Usage
    -----
        with RunLogger(log_path, cfg, prompt_paths) as run:
            run.log_turn(1, instruction, params, sil, db, tokens)
            run.log_turn(2, ...)
            run.finish(cluster_result)

    If an exception propagates out of the with-block, the run is logged
    with status="error" automatically.
    """

    def __init__(
        self,
        log_path: str | Path,
        config: dict[str, Any],
        prompt_paths: dict[str, str | None] | None = None,
    ) -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        self.config = config
        self.prompt_paths = prompt_paths or {}

        self._turns: list[dict] = []
        self._errors: list[str] = []
        self._ts_start = _now_iso()
        self._status = "partial"

        # Build stable run_id from condition/feature_set/seed
        cond = config.get("condition", "?")
        fs   = config.get("feature_set", "?")
        seed = config.get("seed", 0)
        self.run_id = f"{cond}_{fs}_seed{seed:03d}"

    # ── Context manager protocol ──────────────────────────────────────────

    def __enter__(self) -> "RunLogger":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            tb_str = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
            self.fail(tb_str)
            return False   # re-raise
        return False

    # ── Turn logging ──────────────────────────────────────────────────────

    def log_turn(
        self,
        turn_n: int,
        instruction: str,
        parsed_params: dict[str, Any],
        silhouette: float,
        db_index: float,
        llm_tokens_used: int = 0,
    ) -> None:
        self._turns.append({
            "turn":            turn_n,
            "instruction":     instruction,
            "parsed_params":   parsed_params,
            "silhouette":      round(silhouette, 6),
            "db_index":        round(db_index, 6),
            "timestamp":       _now_iso(),
            "llm_tokens_used": llm_tokens_used,
        })

    def log_error(self, message: str) -> None:
        self._errors.append(message)

    # ── Finalisation ──────────────────────────────────────────────────────

    def finish(self, cluster_result) -> None:
        """Write a complete record. Call after the last turn."""
        self._status = "complete"
        self._write({
            "silhouette_final":      round(cluster_result.silhouette, 6),
            "davies_bouldin_final":  round(cluster_result.davies_bouldin, 6),
            "n_turns_completed":     len(self._turns),
        })

    def refuse(self, reason: str) -> None:
        """Write a refused record (LLM safety filter triggered)."""
        self._status = "refused"
        self._errors.append(f"refused: {reason}")
        self._write({"silhouette_final": None, "davies_bouldin_final": None,
                     "n_turns_completed": len(self._turns)})

    def fail(self, exc_info: str) -> None:
        """Write an error record (unrecoverable failure)."""
        self._status = "error"
        self._errors.append(exc_info[:500])   # cap traceback length in log
        self._write({"silhouette_final": None, "davies_bouldin_final": None,
                     "n_turns_completed": len(self._turns)})

    # ── Internal ──────────────────────────────────────────────────────────

    def _write(self, extra: dict) -> None:
        record = {
            "run_id":        self.run_id,
            "condition":     self.config.get("condition"),
            "feature_set":   self.config.get("feature_set"),
            "K":             self.config.get("K"),
            "seed":          self.config.get("seed"),
            "config_hash":   _sha7(self.config.get("_config_path", "")),
            "prompt_hashes": {
                k: _sha7(v) for k, v in self.prompt_paths.items()
            },
            "model_version":    self.config.get("model"),
            "timestamp_start":  self._ts_start,
            "timestamp_end":    _now_iso(),
            "turns":            self._turns,
            "errors":           self._errors,
            "status":           self._status,
        }
        record.update(extra)

        with jsonlines.open(self.log_path, mode="a") as writer:
            writer.write(record)
