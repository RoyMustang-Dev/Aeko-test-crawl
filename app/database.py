"""
SQLite Persistence Layer.

FIXES:
• WAL enabled
• Single writer pattern
• Zero crawler blocking
"""

import sqlite3
from datetime import datetime

DB_PATH = "crawler_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS crawled_pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        url TEXT,
        title TEXT,
        content TEXT,
        depth INTEGER,
        status TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

def enable_wal():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.close()

def insert_page_async(session_id, url, title, content, depth, status):
    """
    Called ONLY by DB writer coroutine.
    Never from crawler workers.
    """

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    ts = datetime.now().isoformat()

    c.execute("""
    INSERT INTO crawled_pages
    (session_id, url, title, content, depth, status, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, url, title, content, depth, status, ts))

    conn.commit()
    conn.close()

def get_all_pages(session_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM crawled_pages WHERE session_id=?", (session_id,))
    rows = c.fetchall()
    conn.close()
    return rows
