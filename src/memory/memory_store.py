"""
Memoria persistente: evita postular dos veces al mismo trabajo
Usa SQLite para garantizar integridad y concurrencia.
"""
import sqlite3
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'applied_jobs.db')

class MemoryStore:
    def __init__(self):
        os.makedirs(os.path.dirname(os.path.abspath(MEMORY_FILE)), exist_ok=True)
        self.conn = sqlite3.connect(MEMORY_FILE, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS applied_jobs (
                    url TEXT PRIMARY KEY,
                    title TEXT,
                    company TEXT,
                    applied_at TEXT
                )
            ''')

    def already_applied(self, url: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM applied_jobs WHERE url = ?", (url,))
        return cursor.fetchone() is not None

    def mark_applied(self, job: dict):
        url = job.get('url', '')
        if url:
            with self.conn:
                self.conn.execute('''
                    INSERT OR IGNORE INTO applied_jobs (url, title, company, applied_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    url,
                    job.get('title', ''),
                    job.get('company', ''),
                    datetime.now().isoformat()
                ))

    def get_all(self) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT url, title, company, applied_at FROM applied_jobs")
        result = {}
        for row in cursor.fetchall():
            result[row[0]] = {
                'title': row[1],
                'company': row[2],
                'applied_at': row[3]
            }
        return result

    def count(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM applied_jobs")
        return cursor.fetchone()[0]

    def close(self):
        self.conn.close()
