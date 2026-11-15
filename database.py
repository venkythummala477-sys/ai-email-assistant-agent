
import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).parent / "email_assistant.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_text TEXT NOT NULL,
                subject TEXT,
                body TEXT,
                category TEXT,
                reason TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def normalize_text(value):
    return " ".join((value or "").lower().split())


def save_draft(
    source_text,
    subject,
    body,
    category,
    reason,
    draft_id=None
):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:

        # If editing an existing draft, update that same ID
        if draft_id is not None:
            cursor = conn.execute("""
                UPDATE drafts
                SET source_text = ?,
                    subject = ?,
                    body = ?,
                    category = ?,
                    reason = ?,
                    created_at = ?
                WHERE id = ?
            """, (
                source_text,
                subject,
                body,
                category,
                reason,
                created_at,
                draft_id
            ))

            if cursor.rowcount > 0:
                conn.commit()
                return draft_id

        # Check whether the same request and subject already exist
        rows = conn.execute(
            "SELECT id, source_text, subject FROM drafts ORDER BY id DESC"
        ).fetchall()

        normalized_source = normalize_text(source_text)
        normalized_subject = normalize_text(subject)

        for row in rows:
            if (
                normalize_text(row["source_text"]) == normalized_source
                and normalize_text(row["subject"]) == normalized_subject
            ):
                # Update existing draft instead of creating duplicate
                conn.execute("""
                    UPDATE drafts
                    SET body = ?,
                        category = ?,
                        reason = ?,
                        created_at = ?
                    WHERE id = ?
                """, (
                    body,
                    category,
                    reason,
                    created_at,
                    row["id"]
                ))

                conn.commit()
                return row["id"]

        # Create a new draft only if no duplicate exists
        cursor = conn.execute("""
            INSERT INTO drafts
            (source_text, subject, body, category, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            source_text,
            subject,
            body,
            category,
            reason,
            created_at
        ))

        conn.commit()
        return cursor.lastrowid


def get_all_drafts():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM drafts ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]


def get_draft(draft_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM drafts WHERE id = ?",
            (draft_id,)
        ).fetchone()

        return dict(row) if row else None
