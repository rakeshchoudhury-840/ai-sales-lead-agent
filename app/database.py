import json
import sqlite3
from pathlib import Path

DB_PATH = Path("data/leads.db")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                lead_json TEXT NOT NULL
            )
            """
        )


def save_lead(session_id: str, lead: dict) -> int:
    init_db()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO leads(session_id, lead_json) VALUES (?, ?)",
            (session_id, json.dumps(lead)),
        )
        return int(cursor.lastrowid)
