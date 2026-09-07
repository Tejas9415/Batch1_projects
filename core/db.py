import os
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from datetime import datetime

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
os.makedirs(STORAGE_DIR, exist_ok= True)
CHECKPOINT_DB_PATH = os.path.join(STORAGE_DIR, "checkpoints.db")

_connection = None

#langgraph_checkpointer

def get_checkpointer() -> SqliteSaver:
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(CHECKPOINT_DB_PATH, check_same_thread= False)
    
    return SqliteSaver(_connection)

# session index

INDEX_DB_PATH = os.path.join(STORAGE_DIR, "session_index.db")
def _index_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(INDEX_DB_PATH, check_same_thread= False)
    conn.row_factory = sqlite3.Row #("id1", Google) -> row["Company_name"]
    return conn

def init_index_db() -> None:
    conn = _index_conn()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS sessions(
        thread_id TEXT PRIMARY KEY,
        company_name TEXT,
        mode TEXT,
        status TEXT,
        create_at TEXT,
     )
"""
    )
    conn.commit()
    conn.close()

def create_session(thread_id: str, company_name: str, mode: str) -> None:
    conn = _index_conn()
    conn.execute(
        "INSERT OR IGNORE INTO sessions(thread_id, company_name, mode, status, created_at)"
        "VALUES(?,?,?,?,?,)",
        (thread_id, company_name, mode,"in_progress",datetime.now().isoformat(timespec= "seconds"))
    )
    conn.commit()
    conn.close()

def update_session_status(thread_id: str, status: str)-> None:
    conn = _index_conn()
    conn.execute("UPDATE sessions SET status = ? WHERE thread_id = ?",(status, thread_id))
    conn.commit()
    conn.close()

def list_sessions() -> list[dict]:
    conn = _index_conn()
    rows = conn.execute("SELECT * FROM sessions ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict[row] for row in rows]