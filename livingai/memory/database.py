# LivingAI Memory Database
# ========================
# This module handles SQLite database operations for the memory system.

import os
import sqlite3
import logging
from typing import Dict, Any, Optional, List, Tuple

# Local imports
from .models import Memory, MemoryType, MemoryStatus, MemoryImportance, MemoryStats


class MemoryDatabase:
    """
    Handles SQLite database operations for the memory system.
    """
    
    SCHEMA_VERSION = 1
    
    CREATE_MEMORIES_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        memory_type TEXT NOT NULL DEFAULT 'working',
        importance TEXT NOT NULL DEFAULT 'medium',
        relevance REAL NOT NULL DEFAULT 0.5,
        recency REAL NOT NULL DEFAULT 1.0,
        confidence REAL NOT NULL DEFAULT 0.5,
        frequency INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'active',
        metadata TEXT NOT NULL DEFAULT '{}',
        created_at REAL NOT NULL DEFAULT (strftime('%s', 'now')),
        updated_at REAL NOT NULL DEFAULT (strftime('%s', 'now'))
    );
    """
    
    CREATE_SCHEMA_VERSION_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at REAL NOT NULL DEFAULT (strftime('%s', 'now'))
    );
    """

    ALL_TABLES_SQL = [
        CREATE_MEMORIES_TABLE_SQL,
        CREATE_SCHEMA_VERSION_TABLE_SQL,
        "CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT, predicate TEXT, object TEXT, confidence REAL DEFAULT 0.9, created_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS preferences (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE NOT NULL, value TEXT NOT NULL, created_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS episodes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, summary TEXT, created_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS experiences (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, outcome TEXT, created_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, source TEXT, importance REAL DEFAULT 0.5, created_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS skills (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, description TEXT, instructions TEXT, enabled BOOLEAN DEFAULT 1, created_at REAL DEFAULT (strftime('%s', 'now')), updated_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT, status TEXT DEFAULT 'PLANNED', priority INTEGER DEFAULT 1, created_at REAL DEFAULT (strftime('%s', 'now')), updated_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, goal_id INTEGER, description TEXT NOT NULL, status TEXT DEFAULT 'PENDING', created_at REAL DEFAULT (strftime('%s', 'now')), FOREIGN KEY(goal_id) REFERENCES goals(id));",
        "CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, created_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id INTEGER, role TEXT NOT NULL, content TEXT NOT NULL, created_at REAL DEFAULT (strftime('%s', 'now')), FOREIGN KEY(conversation_id) REFERENCES conversations(id));",
        "CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT NOT NULL, risk TEXT DEFAULT 'LOW', status TEXT DEFAULT 'EXECUTED', result TEXT, created_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS observations (id INTEGER PRIMARY KEY AUTOINCREMENT, action_id INTEGER, observation TEXT, created_at REAL DEFAULT (strftime('%s', 'now')), FOREIGN KEY(action_id) REFERENCES actions(id));",
        "CREATE TABLE IF NOT EXISTS reflections (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, insight TEXT, created_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS state_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, energy INTEGER, focus INTEGER, confidence INTEGER, activity TEXT, created_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS model_events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT, details TEXT, created_at REAL DEFAULT (strftime('%s', 'now')));",
        "CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT DEFAULT (strftime('%s', 'now')), event TEXT NOT NULL, action TEXT, risk TEXT, permission TEXT, result TEXT, error TEXT);"
    ]
    
    def __init__(self, db_path: str):
        self.db_path = os.path.expanduser(db_path)
        self._connection: Optional[sqlite3.Connection] = None
        if os.path.dirname(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_database()
        logging.info(f"MemoryDatabase initialized at {self.db_path}")

    def initialize(self) -> None:
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for sql in self.ALL_TABLES_SQL:
                    cursor.execute(sql)
                
                cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
                result = cursor.fetchone()
                if result is None:
                    cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (self.SCHEMA_VERSION,))
                else:
                    current_version = result[0]
                    if current_version < self.SCHEMA_VERSION:
                        self._migrate_database(cursor, current_version)
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            raise
    
    def _migrate_database(self, cursor: sqlite3.Cursor, current_version: int) -> None:
        cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (self.SCHEMA_VERSION,))
    
    def _get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, timeout=10)
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection
    
    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def create(self, memory: Memory) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO memories (
                    content, memory_type, importance, relevance, recency, 
                    confidence, frequency, status, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.content,
                    memory.memory_type.value,
                    memory.importance.value,
                    memory.relevance,
                    memory.recency,
                    memory.confidence,
                    memory.frequency,
                    memory.status.value,
                    self._serialize_metadata(memory.metadata),
                    memory.created_at,
                    memory.updated_at,
                ))
                memory.id = cursor.lastrowid
                conn.commit()
                return memory.id
        except Exception as e:
            logging.error(f"Failed to create memory: {e}")
            raise
    
    def read(self, memory_id: int) -> Optional[Memory]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT id, content, memory_type, importance, relevance, recency, 
                       confidence, frequency, status, metadata, created_at, updated_at
                FROM memories WHERE id = ?
                """, (memory_id,))
                row = cursor.fetchone()
                if row is None:
                    return None
                return Memory(
                    id=row[0],
                    content=row[1],
                    memory_type=MemoryType(row[2]),
                    importance=MemoryImportance(row[3]),
                    relevance=row[4],
                    recency=row[5],
                    confidence=row[6],
                    frequency=row[7],
                    status=MemoryStatus(row[8]),
                    metadata=self._deserialize_metadata(row[9]),
                    created_at=row[10],
                    updated_at=row[11],
                )
        except Exception as e:
            logging.error(f"Failed to read memory {memory_id}: {e}")
            raise
    
    def update(self, memory: Memory) -> bool:
        if memory.id is None:
            return False
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE memories SET
                    content = ?, memory_type = ?, importance = ?, relevance = ?,
                    recency = ?, confidence = ?, frequency = ?, status = ?,
                    metadata = ?, updated_at = ?
                WHERE id = ?
                """, (
                    memory.content,
                    memory.memory_type.value,
                    memory.importance.value,
                    memory.relevance,
                    memory.recency,
                    memory.confidence,
                    memory.frequency,
                    memory.status.value,
                    self._serialize_metadata(memory.metadata),
                    memory.updated_at,
                    memory.id,
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Failed to update memory {memory.id}: {e}")
            return False
    
    def delete(self, memory_id: int) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Memory]:
        memories = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT id, content, memory_type, importance, relevance, recency, confidence, frequency, status, metadata, created_at, updated_at FROM memories"
                params = []
                if limit is not None:
                    query += " LIMIT ? OFFSET ?"
                    params.extend([limit, offset])
                cursor.execute(query, params)
                for row in cursor.fetchall():
                    memories.append(Memory(
                        id=row[0],
                        content=row[1],
                        memory_type=MemoryType(row[2]),
                        importance=MemoryImportance(row[3]),
                        relevance=row[4],
                        recency=row[5],
                        confidence=row[6],
                        frequency=row[7],
                        status=MemoryStatus(row[8]),
                        metadata=self._deserialize_metadata(row[9]),
                        created_at=row[10],
                        updated_at=row[11],
                    ))
        except Exception as e:
            logging.error(f"Failed to list memories: {e}")
        return memories
    
    def search(self, query: str, memory_type: Optional[MemoryType] = None, limit: int = 10) -> List[Memory]:
        memories = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query_sql = "SELECT id, content, memory_type, importance, relevance, recency, confidence, frequency, status, metadata, created_at, updated_at FROM memories WHERE content LIKE ?"
                params = [f"%{query}%"]
                if memory_type is not None:
                    query_sql += " AND memory_type = ?"
                    params.append(memory_type.value)
                query_sql += " ORDER BY relevance DESC, recency DESC LIMIT ?"
                params.append(limit)
                cursor.execute(query_sql, params)
                for row in cursor.fetchall():
                    memories.append(Memory(
                        id=row[0],
                        content=row[1],
                        memory_type=MemoryType(row[2]),
                        importance=MemoryImportance(row[3]),
                        relevance=row[4],
                        recency=row[5],
                        confidence=row[6],
                        frequency=row[7],
                        status=MemoryStatus(row[8]),
                        metadata=self._deserialize_metadata(row[9]),
                        created_at=row[10],
                        updated_at=row[11],
                    ))
        except Exception as e:
            logging.error(f"Failed to search memories: {e}")
        return memories
    
    def count(self) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM memories")
                return cursor.fetchone()[0]
        except Exception as e:
            logging.error(f"Failed to count memories: {e}")
            return 0
    
    def get_stats(self) -> MemoryStats:
        stats = MemoryStats()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM memories")
                stats.total_memories = cursor.fetchone()[0]
                cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
                for row in cursor.fetchall():
                    stats.by_type[row[0]] = row[1]
                cursor.execute("SELECT status, COUNT(*) FROM memories GROUP BY status")
                for row in cursor.fetchall():
                    stats.by_status[row[0]] = row[1]
                cursor.execute("SELECT importance, COUNT(*) FROM memories GROUP BY importance")
                for row in cursor.fetchall():
                    stats.by_importance[row[0]] = row[1]
                cursor.execute("SELECT AVG(relevance) FROM memories")
                res = cursor.fetchone()
                stats.avg_relevance = res[0] if res[0] is not None else 0.0
                cursor.execute("SELECT AVG(confidence) FROM memories")
                res = cursor.fetchone()
                stats.avg_confidence = res[0] if res[0] is not None else 0.0
        except Exception as e:
            logging.error(f"Failed to get memory stats: {e}")
        return stats
    
    def _serialize_metadata(self, metadata: Dict[str, Any]) -> str:
        import json
        return json.dumps(metadata)
    
    def _deserialize_metadata(self, metadata_str: str) -> Dict[str, Any]:
        import json
        try:
            return json.loads(metadata_str)
        except json.JSONDecodeError:
            return {}

    def doctor(self) -> Dict[str, Any]:
        diagnostics = {"database_exists": os.path.exists(self.db_path), "database_size": 0, "table_exists": False, "row_count": 0}
        try:
            if diagnostics["database_exists"]:
                diagnostics["database_size"] = os.path.getsize(self.db_path)
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
                    diagnostics["table_exists"] = cursor.fetchone() is not None
                    if diagnostics["table_exists"]:
                        cursor.execute("SELECT COUNT(*) FROM memories")
                        diagnostics["row_count"] = cursor.fetchone()[0]
        except Exception as e:
            diagnostics["error"] = str(e)
        return diagnostics


DatabaseManager = MemoryDatabase
