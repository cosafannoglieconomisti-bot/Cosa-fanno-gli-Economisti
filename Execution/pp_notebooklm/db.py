import sqlite3
import os
from pathlib import Path
from typing import List, Optional
from .models import Notebook, Source, Asset

DB_PATH = Path.home() / ".notebooklm-mcp" / "mirror.db"

def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notebooks (
                id TEXT PRIMARY KEY,
                title TEXT,
                source_count INTEGER,
                created_at TEXT,
                modified_at TEXT,
                is_owned INTEGER,
                last_synced TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                notebook_id TEXT,
                title TEXT,
                type TEXT,
                char_count INTEGER,
                FOREIGN KEY(notebook_id) REFERENCES notebooks(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                notebook_id TEXT,
                type TEXT,
                status TEXT,
                url TEXT,
                created_at TEXT,
                metadata TEXT,
                FOREIGN KEY(notebook_id) REFERENCES notebooks(id)
            )
        """)
        conn.commit()

def upsert_notebook(nb: Notebook):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO notebooks (id, title, source_count, created_at, modified_at, is_owned, last_synced)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                source_count=excluded.source_count,
                modified_at=excluded.modified_at,
                last_synced=datetime('now')
        """, (nb.id, nb.title, nb.source_count, nb.created_at, nb.modified_at, int(nb.is_owned)))

def upsert_source(s: Source):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO sources (id, notebook_id, title, type, char_count)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                type=excluded.type,
                char_count=excluded.char_count
        """, (s.id, s.notebook_id, s.title, s.type, s.char_count))

def upsert_asset(a: Asset):
    import json
    print(f"DEBUG: upsert_asset values: {(a.id, a.notebook_id, a.type, a.status, a.url, a.created_at, a.metadata)}")
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO assets (id, notebook_id, type, status, url, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                type=excluded.type,
                status=excluded.status,
                url=excluded.url,
                metadata=excluded.metadata
        """, (a.id, a.notebook_id, a.type, a.status, a.url, a.created_at, json.dumps(a.metadata)))

def get_notebooks() -> List[Notebook]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM notebooks").fetchall()
        return [Notebook(id=r['id'], title=r['title'], source_count=r['source_count'], 
                         created_at=r['created_at'], modified_at=r['modified_at'], 
                         is_owned=bool(r['is_owned'])) for r in rows]

def get_assets(notebook_id: str) -> List[Asset]:
    import json
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM assets WHERE notebook_id=?", (notebook_id,)).fetchall()
        return [Asset(id=r['id'], notebook_id=r['notebook_id'], type=r['type'], 
                      status=r['status'], url=r['url'], created_at=r['created_at'], 
                      metadata=json.loads(r['metadata'] or '{}')) for r in rows]
