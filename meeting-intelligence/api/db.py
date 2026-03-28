import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = "tasks.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id                TEXT PRIMARY KEY,
            thread_id         TEXT NOT NULL,
            description       TEXT,
            owner             TEXT,
            deadline          TEXT,
            priority          TEXT,
            status            TEXT DEFAULT 'open',
            escalation_level  INT  DEFAULT 0,
            jira_url          TEXT DEFAULT '',
            last_updated_at   TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id          TEXT PRIMARY KEY,
            thread_id   TEXT NOT NULL,
            stage       TEXT,
            event       TEXT,
            reasoning   TEXT,
            ts          TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def save_tasks(thread_id: str, tasks: list):
    conn = sqlite3.connect(DB_PATH)
    for t in tasks:
        conn.execute("""
            INSERT INTO tasks
              (id, thread_id, description, owner, deadline, priority, jira_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), thread_id,
            t.get("description", ""), t.get("owner", ""),
            t.get("deadline", ""),    t.get("priority", "medium"),
            t.get("jira_url", "")
        ))
    conn.commit()
    conn.close()


def append_audit(thread_id: str, entry: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO audit_log (id, thread_id, stage, event, reasoning, ts)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()), thread_id,
        entry.get("stage", ""),     entry.get("event", ""),
        entry.get("reasoning", ""), entry.get("ts", datetime.now(timezone.utc).isoformat())
    ))
    conn.commit()
    conn.close()


def get_audit(thread_id: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT stage, event, reasoning, ts
        FROM audit_log WHERE thread_id = ?
        ORDER BY ts ASC
    """, (thread_id,)).fetchall()
    conn.close()
    return [{"stage": r[0], "event": r[1], "reasoning": r[2], "ts": r[3]} for r in rows]


def get_stale_tasks(stale_after_hours: int = 48) -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(f"""
        SELECT id, thread_id, description, owner, deadline,
               escalation_level, last_updated_at
        FROM tasks
        WHERE status = 'open'
          AND last_updated_at < datetime('now', '-{stale_after_hours} hours')
        ORDER BY escalation_level ASC, last_updated_at ASC
    """).fetchall()
    conn.close()
    return [
        dict(zip(["id","thread_id","description","owner",
                  "deadline","escalation_level","last_updated_at"], r))
        for r in rows
    ]


def update_escalation(task_id: str, new_level: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        UPDATE tasks
        SET escalation_level = ?, last_updated_at = datetime('now')
        WHERE id = ?
    """, (new_level, task_id))
    conn.commit()
    conn.close()


def mark_task_complete(task_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        UPDATE tasks SET status='done', last_updated_at=datetime('now')
        WHERE id = ?
    """, (task_id,))
    conn.commit()
    conn.close()