# LivingAI Audit Logger
import os
import sqlite3
import datetime
import logging
from typing import Optional, List, Dict, Any


class AuditLogger:
    """Logs system events, actions, risk classifications, and outcomes for auditing."""

    def __init__(self, log_dir: str):
        self.log_dir = os.path.expanduser(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        self.db_path = os.path.join(self.log_dir, "audit.db")
        self._init_db()

    def _init_db(self) -> None:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event TEXT NOT NULL,
                    action TEXT,
                    risk TEXT,
                    permission TEXT,
                    result TEXT,
                    error TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Failed to initialize audit database: {e}")

    def log(
        self,
        event: str,
        action: Optional[str] = None,
        risk: Optional[str] = None,
        permission: Optional[str] = None,
        result: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_logs (timestamp, event, action, risk, permission, result, error) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (timestamp, event, action, risk, permission, result, error)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Audit log failed: {e}")

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            logs = [dict(row) for row in rows]
            conn.close()
            return logs
        except Exception as e:
            logging.error(f"Failed to fetch audit logs: {e}")
            return []
