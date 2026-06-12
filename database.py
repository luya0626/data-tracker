import sqlite3
import os
from flask import g
from config import DATABASE_PATH, DATA_DIR


def get_db():
    """Get a database connection for the current request (stored in g)."""
    if 'db' not in g:
        os.makedirs(DATA_DIR, exist_ok=True)
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        g.db = conn
    return g.db


def close_db(exception=None):
    """Close the database connection at the end of a request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS lines (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL UNIQUE,
            color      TEXT    NOT NULL DEFAULT '#5470C6',
            visible    INTEGER NOT NULL DEFAULT 1,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS data_points (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            line_id    INTEGER NOT NULL,
            date       TEXT    NOT NULL,
            value      REAL    NOT NULL,
            tag        TEXT    NOT NULL DEFAULT '',
            created_at TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (line_id) REFERENCES lines(id) ON DELETE CASCADE
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_data_points_line_date
            ON data_points(line_id, date);

        CREATE INDEX IF NOT EXISTS idx_data_points_date
            ON data_points(date);

        CREATE INDEX IF NOT EXISTS idx_lines_sort
            ON lines(sort_order);
    """)
    # Migration: add tag column if table was created before it existed
    try:
        conn.execute("ALTER TABLE data_points ADD COLUMN tag TEXT NOT NULL DEFAULT ''")
    except:
        pass  # column already exists
