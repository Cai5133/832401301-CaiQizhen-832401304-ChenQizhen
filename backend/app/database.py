"""SQLite connections and schema; no database is created at import time."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def default_database_path() -> Path:
    path = Path(os.getenv("ADDRESS_BOOK_DB", "data/contacts.sqlite3")).expanduser()
    return path if path.is_absolute() else BACKEND_ROOT / path


class Database:
    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.create_function("casefold", 1, lambda value: value.casefold())
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 100),
                    is_favorite INTEGER NOT NULL DEFAULT 0 CHECK(is_favorite IN (0, 1))
                );
                CREATE TABLE IF NOT EXISTS contact_methods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
                    type TEXT NOT NULL CHECK(type IN ('phone', 'email', 'social', 'address')),
                    label TEXT NOT NULL DEFAULT '',
                    value TEXT NOT NULL CHECK(length(value) BETWEEN 1 AND 2000)
                );
                CREATE INDEX IF NOT EXISTS idx_methods_contact ON contact_methods(contact_id);
                CREATE INDEX IF NOT EXISTS idx_contacts_favorite ON contacts(is_favorite);
            """)
