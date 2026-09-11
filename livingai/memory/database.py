# LivingAI Memory Database
# ========================
# This module handles SQLite database operations for the memory system.

import os
import sqlite3
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# Local imports
from .models import Memory, MemoryType, MemoryStatus, MemoryImportance, MemoryStats


class MemoryDatabase:
    """
    Handles SQLite database operations for the memory system.
    
    Responsibilities:
    - Initialize and maintain the SQLite database
    - CRUD operations for memories
    - Database migrations
    - Backup and restore
    """
    
    # Database schema version
    SCHEMA_VERSION = 1
    
    # SQL for creating the memories table
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
    
    # SQL for creating the schema version table
    CREATE_SCHEMA_VERSION_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at REAL NOT NULL DEFAULT (strftime('%s', 'now'))
    );
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the MemoryDatabase.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = os.path.expanduser(db_path)
        self._connection: Optional[sqlite3.Connection] = None
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize the database
        self._initialize_database()
        
        logging.info(f"MemoryDatabase initialized at {self.db_path}")
    
    def _initialize_database(self) -> None:
        """Initialize the database and tables."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create tables
                cursor.execute(self.CREATE_MEMORIES_TABLE_SQL)
                cursor.execute(self.CREATE_SCHEMA_VERSION_TABLE_SQL)
                
                # Check schema version
                cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
                result = cursor.fetchone()
                
                if result is None:
                    # First time - set schema version
                    cursor.execute(
                        "INSERT INTO schema_version (version) VALUES (?)",
                        (self.SCHEMA_VERSION,)
                    )
                else:
                    current_version = result[0]
                    if current_version < self.SCHEMA_VERSION:
                        # Need to migrate
                        self._migrate_database(cursor, current_version)
                
                conn.commit()
        
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            raise
    
    def _migrate_database(self, cursor: sqlite3.Cursor, current_version: int) -> None:
        """
        Migrate the database from an older schema version.
        
        Args:
            cursor: Database cursor.
            current_version: Current schema version.
        """
        logging.info(f"Migrating database from version {current_version} to {self.SCHEMA_VERSION}")
        
        # For now, we only have version 1, so no migrations are needed
        # In a real implementation, this would handle schema changes
        
        # Update schema version
        cursor.execute(
            "INSERT INTO schema_version (version) VALUES (?)",
            (self.SCHEMA_VERSION,)
        )
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.
        
        Returns:
            sqlite3.Connection: Database connection.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            # Enable foreign key support
            self._connection.execute("PRAGMA foreign_keys = ON")
            # Set timeout for busy database
            self._connection.set_timeout(10)
        
        return self._connection
    
    def close(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def create(self, memory: Memory) -> int:
        """
        Create a new memory in the database.
        
        Args:
            memory: Memory to create.
            
        Returns:
            int: ID of the created memory.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO memories (
                    content, memory_type, importance, relevance, recency, 
                    confidence, frequency, status, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        """
        Read a memory from the database.
        
        Args:
            memory_id: ID of the memory to read.
            
        Returns:
            Optional[Memory]: The memory, or None if not found.
        """
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
        """
        Update a memory in the database.
        
        Args:
            memory: Memory to update.
            
        Returns:
            bool: True if update succeeded, False otherwise.
        """
        if memory.id is None:
            logging.error("Cannot update memory without ID")
            return False
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                UPDATE memories SET
                    content = ?,
                    memory_type = ?,
                    importance = ?,
                    relevance = ?,
                    recency = ?,
                    confidence = ?,
                    frequency = ?,
                    status = ?,
                    metadata = ?,
                    updated_at = ?
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
        """
        Delete a memory from the database.
        
        Args:
            memory_id: ID of the memory to delete.
            
        Returns:
            bool: True if deletion succeeded, False otherwise.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                conn.commit()
                
                return cursor.rowcount > 0
        
        except Exception as e:
            logging.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    def list_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Memory]:
        """
        List all memories in the database.
        
        Args:
            limit: Maximum number of memories to return.
            offset: Offset for pagination.
            
        Returns:
            List[Memory]: List of memories.
        """
        memories = []
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT id, content, memory_type, importance, relevance, recency, 
                       confidence, frequency, status, metadata, created_at, updated_at
                FROM memories
                """
                
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
    
    def search(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[Memory]:
        """
        Search for memories matching a query.
        
        Args:
            query: Search query (text to match in content).
            memory_type: Optional memory type filter.
            limit: Maximum number of results to return.
            
        Returns:
            List[Memory]: List of matching memories.
        """
        memories = []
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query_sql = """
                SELECT id, content, memory_type, importance, relevance, recency, 
                       confidence, frequency, status, metadata, created_at, updated_at
                FROM memories
                WHERE content LIKE ?
                """
                
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
        """
        Count the total number of memories.
        
        Returns:
            int: Total number of memories.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM memories")
                return cursor.fetchone()[0]
        
        except Exception as e:
            logging.error(f"Failed to count memories: {e}")
            return 0
    
    def get_stats(self) -> MemoryStats:
        """
        Get statistics about the memories in the database.
        
        Returns:
            MemoryStats: Memory statistics.
        """
        stats = MemoryStats()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total count
                cursor.execute("SELECT COUNT(*) FROM memories")
                stats.total_memories = cursor.fetchone()[0]
                
                # By type
                cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
                for row in cursor.fetchall():
                    stats.by_type[row[0]] = row[1]
                
                # By status
                cursor.execute("SELECT status, COUNT(*) FROM memories GROUP BY status")
                for row in cursor.fetchall():
                    stats.by_status[row[0]] = row[1]
                
                # By importance
                cursor.execute("SELECT importance, COUNT(*) FROM memories GROUP BY importance")
                for row in cursor.fetchall():
                    stats.by_importance[row[0]] = row[1]
                
                # Average relevance
                cursor.execute("SELECT AVG(relevance) FROM memories")
                result = cursor.fetchone()
                stats.avg_relevance = result[0] if result[0] is not None else 0.0
                
                # Average confidence
                cursor.execute("SELECT AVG(confidence) FROM memories")
                result = cursor.fetchone()
                stats.avg_confidence = result[0] if result[0] is not None else 0.0
        
        except Exception as e:
            logging.error(f"Failed to get memory stats: {e}")
        
        return stats
    
    def _serialize_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Serialize metadata dictionary to JSON string.
        
        Args:
            metadata: Metadata dictionary.
            
        Returns:
            str: JSON string.
        """
        import json
        return json.dumps(metadata)
    
    def _deserialize_metadata(self, metadata_str: str) -> Dict[str, Any]:
        """
        Deserialize metadata JSON string to dictionary.
        
        Args:
            metadata_str: JSON string.
            
        Returns:
            Dict[str, Any]: Metadata dictionary.
        """
        import json
        try:
            return json.loads(metadata_str)
        except json.JSONDecodeError:
            return {}
    
    def backup(self, backup_path: str) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path to save the backup.
            
        Returns:
            bool: True if backup succeeded, False otherwise.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Copy the database file
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            logging.info(f"Database backup created at {backup_path}")
            return True
        
        except Exception as e:
            logging.error(f"Failed to create database backup: {e}")
            return False
    
    def restore(self, backup_path: str) -> bool:
        """
        Restore the database from a backup.
        
        Args:
            backup_path: Path to the backup file.
            
        Returns:
            bool: True if restore succeeded, False otherwise.
        """
        try:
            # Close current connection
            self.close()
            
            # Copy the backup file
            import shutil
            shutil.copy2(backup_path, self.db_path)
            
            logging.info(f"Database restored from {backup_path}")
            return True
        
        except Exception as e:
            logging.error(f"Failed to restore database: {e}")
            return False
    
    def doctor(self) -> Dict[str, Any]:
        """
        Run database diagnostics.
        
        Returns:
            Dict[str, Any]: Diagnostic results.
        """
        diagnostics = {
            "database_exists": os.path.exists(self.db_path),
            "database_size": 0,
            "table_exists": False,
            "row_count": 0,
        }
        
        try:
            if diagnostics["database_exists"]:
                diagnostics["database_size"] = os.path.getsize(self.db_path)
                
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Check if table exists
                    cursor.execute("""
                    SELECT name FROM sqlite_master WHERE type='table' AND name='memories'
                    """)
                    diagnostics["table_exists"] = cursor.fetchone() is not None
                    
                    # Count rows
                    if diagnostics["table_exists"]:
                        cursor.execute("SELECT COUNT(*) FROM memories")
                        diagnostics["row_count"] = cursor.fetchone()[0]
        
        except Exception as e:
            diagnostics["error"] = str(e)
        
        return diagnostics
