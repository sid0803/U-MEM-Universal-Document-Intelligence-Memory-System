# app/core/user_store.py

import sqlite3
import uuid
from datetime import datetime, UTC
from pathlib import Path
from typing import Optional, Dict

DB_PATH = Path("data/users.db")


# -------------------------
# Connection & Init
# -------------------------

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
    )

    conn.row_factory = sqlite3.Row
    init_users_db(conn)

    return conn


def init_users_db(conn: sqlite3.Connection) -> None:
    # Enable WAL mode once
    conn.execute("PRAGMA journal_mode=WAL;")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email
        ON users(email)
    """)

    conn.commit()


# -------------------------
# Write Operations
# -------------------------

def create_user(email: str, password_hash: str) -> str:
    user_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()

    conn = get_connection()

    try:
        conn.execute("""
            INSERT INTO users (user_id, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, email, password_hash, now))
        conn.commit()

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Email already registered")
        raise

    finally:
        conn.close()

    return user_id


# -------------------------
# Read Operations
# -------------------------

def get_user_by_email(email: str) -> Optional[Dict[str, str]]:
    conn = get_connection()

    try:
        cursor = conn.execute(
            "SELECT user_id, email, password_hash FROM users WHERE email = ?",
            (email,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    finally:
        conn.close()


def get_user_by_id(user_id: str) -> Optional[Dict[str, str]]:
    conn = get_connection()

    try:
        cursor = conn.execute(
            "SELECT user_id, email FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    finally:
        conn.close()
