"""
run_logger.py — Database helpers for logging agent runs and their steps.

Tables:
  agent_runs  — one row per orchestration run (status: running | completed | failed)
  agent_steps — one row per meaningful step inside a run (tool calls, classify, etc.)
"""

import sqlite3
import json
import uuid
from datetime import datetime, timezone

DB_PATH = "database/inventory.db"


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Public API ──────────────────────────────────────────────────────────────

def start_run(domain: str, agent_name: str, input_text: str) -> str:
    """
    Insert a new row into agent_runs with status='running'.
    Returns the generated run_id (uuid4 string).
    """
    run_id = str(uuid.uuid4())
    conn = _conn()
    try:
        conn.execute(
            """
            INSERT INTO agent_runs (run_id, agent_name, domain, input, status)
            VALUES (?, ?, ?, ?, 'running')
            """,
            (run_id, agent_name, domain, input_text),
        )
        conn.commit()
    finally:
        conn.close()
    return run_id


def log_step(
    run_id: str,
    step_order: int,
    step_type: str,
    description: str,
    payload_dict: dict | None = None,
) -> None:
    """
    Insert a step row into agent_steps.
    payload_dict is serialised to JSON; pass None to store NULL.
    """
    payload_json = json.dumps(payload_dict) if payload_dict is not None else None
    conn = _conn()
    try:
        conn.execute(
            """
            INSERT INTO agent_steps (run_id, step_order, step_type, description, payload)
            VALUES (?, ?, ?, ?, ?)
            """,
            (run_id, step_order, step_type, description, payload_json),
        )
        conn.commit()
    finally:
        conn.close()


def finish_run(run_id: str, response_text: str = "", error_str: str = "", domain: str = "") -> None:
    """
    Mark a run as completed or failed, storing the final response / error.
    Optionally updates the domain if the classifier resolved it.
    """
    status = "failed" if error_str else "completed"
    finished_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn = _conn()
    try:
        conn.execute(
            """
            UPDATE agent_runs
            SET status      = ?,
                response    = ?,
                error       = ?,
                finished_at = ?,
                domain      = CASE WHEN ? != '' THEN ? ELSE domain END
            WHERE run_id = ?
            """,
            (status, response_text, error_str or None, finished_at, domain, domain, run_id),
        )
        conn.commit()
    finally:
        conn.close()
