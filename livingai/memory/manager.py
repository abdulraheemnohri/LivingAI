# LivingAI Memory Manager
# ======================
# This module manages all memory operations for the LivingAI system.

import logging
import time
from typing import Dict, Any, Optional, List

# Local imports
from .database import MemoryDatabase
from .models import Memory, MemoryType, MemoryStatus, MemoryImportance, MemoryStats
from ..config import ConfigManager
from ..security.audit import AuditLogger


class MemoryManager:
    """
    Manages all memory operations for the LivingAI system.
    
    Responsibilities:
    - CRUD operations for memories
    - Memory search and retrieval
    - Memory ranking and scoring
    - Memory consolidation
    - Memory statistics
    """
    
    def __init__(
        self,
        db_path: str,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the MemoryManager.
        
        Args:
            db_path: Path to the SQLite database file.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.db_path = db_path
        self.config = config
        self.audit_logger = audit_logger
        
        # Initialize database
        self.database = MemoryDatabase(db_path)
        
        # Memory state
        self._memory_cache: Dict[int, Memory] = {}
        self._last_consolidation = time.time()
        
        logging.info(f"MemoryManager initialized at {db_path}")
    
    def add(self, memory_data: Dict[str, Any]) -> int:
        """
        Add a new memory.
        
        Args:
            memory_data: Dictionary with memory data.
            
        Returns:
            int: ID of the created memory.
        """
        # Convert dict to Memory object
        memory = Memory.from_dict(memory_data)
        
        # Set default values if not provided
        if not memory.memory_type:
            memory.memory_type = MemoryType.WORKING
        if not memory.importance:
            memory.importance = MemoryImportance.MEDIUM
        if memory.relevance == 0:
            memory.relevance = 0.5
        if memory.recency == 0:
            memory.recency = 1.0
        if memory.confidence == 0:
            memory.confidence = 0.5
        if memory.frequency == 0:
            memory.frequency = 1
        if not memory.status:
            memory.status = MemoryStatus.ACTIVE
        
        # Create in database
        memory_id = self.database.create(memory)
        
        # Add to cache
        self._memory_cache[memory_id] = memory
        
        self.audit_logger.log(
            "MEMORY_ADD",
            f"Added memory {memory_id} of type {memory.memory_type.value}"
        )
        
        return memory_id
    
    def get(self, memory_id: int) -> Optional[Memory]:
        """
        Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve.
            
        Returns:
            Optional[Memory]: The memory, or None if not found.
        """
        # Check cache first
        if memory_id in self._memory_cache:
            return self._memory_cache[memory_id]
        
        # Get from database
        memory = self.database.read(memory_id)
        
        if memory:
            # Add to cache
            self._memory_cache[memory_id] = memory
        
        return memory
    
    def update(self, memory: Memory) -> bool:
        """
        Update a memory.
        
        Args:
            memory: Memory to update.
            
        Returns:
            bool: True if update succeeded, False otherwise.
        """
        if memory.id is None:
            return False
        
        # Update in database
        success = self.database.update(memory)
        
        if success:
            # Update in cache
            self._memory_cache[memory.id] = memory
            
            self.audit_logger.log(
                "MEMORY_UPDATE",
                f"Updated memory {memory.id}"
            )
        
        return success
    
    def delete(self, memory_id: int) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: ID of the memory to delete.
            
        Returns:
            bool: True if deletion succeeded, False otherwise.
        """
        # Remove from cache
        if memory_id in self._memory_cache:
            del self._memory_cache[memory_id]
        
        # Delete from database
        success = self.database.delete(memory_id)
        
        if success:
            self.audit_logger.log(
                "MEMORY_DELETE",
                f"Deleted memory {memory_id}"
            )
        
        return success
    
    def list_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Memory]:
        """
        List all memories.
        
        Args:
            limit: Maximum number of memories to return.
            offset: Offset for pagination.
            
        Returns:
            List[Memory]: List of memories.
        """
        return self.database.list_all(limit, offset)
    
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
        # Get matching memories from database
        memories = self.database.search(query, memory_type, limit)
        
        # Rank the memories
        ranked_memories = self._rank_memories(memories, query)
        
        # Update recency for accessed memories
        for memory in ranked_memories:
            memory.update_recency()
            self.update(memory)
        
        self.audit_logger.log(
            "MEMORY_SEARCH",
            f"Searched for '{query}' - found {len(ranked_memories)} results"
        )
        
        return ranked_memories
    
    def _rank_memories(
        self,
        memories: List[Memory],
        query: str
    ) -> List[Memory]:
        """
        Rank memories by relevance to the query.
        
        Args:
            memories: List of memories to rank.
            query: Search query.
            
        Returns:
            List[Memory]: Ranked list of memories.
        """
        # Calculate ranking score for each memory
        scored_memories = []
        for memory in memories:
            # Base score from memory's ranking
            base_score = memory.get_ranking_score()
            
            # Query-specific relevance
            query_relevance = self._calculate_query_relevance(memory, query)
            
            # Combined score
            combined_score = base_score * 0.7 + query_relevance * 0.3
            
            scored_memories.append((memory, combined_score))
        
        # Sort by combined score (descending)
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the memories (without scores)
        return [memory for memory, score in scored_memories]
    
    def _calculate_query_relevance(self, memory: Memory, query: str) -> float:
        """
        Calculate how relevant a memory is to a query.
        
        Args:
            memory: The memory to score.
            query: The search query.
            
        Returns:
            float: Relevance score (0.0 to 1.0).
        """
        # Simple implementation: count query term matches
        query_terms = query.lower().split()
        content = memory.content.lower()
        
        matches = sum(1 for term in query_terms if term in content)
        
        if len(query_terms) == 0:
            return 0.0
        
        return min(matches / len(query_terms), 1.0)
    
    def consolidate(self) -> Dict[str, Any]:
        """
        Consolidate memories (deduplicate, merge, archive).
        
        Returns:
            Dict[str, Any]: Consolidation results.
        """
        self.audit_logger.log("MEMORY_CONSOLIDATE_START", "Starting memory consolidation")
        start_time = time.time()
        
        results = {
            "deduplicated": 0,
            "merged": 0,
            "archived": 0,
            "deleted": 0,
        }
        
        try:
            # Get all memories
            memories = self.list_all()
            
            # Group by similarity
            groups = self._group_similar_memories(memories)
            
            for group in groups:
                if len(group) > 1:
                    # Merge similar memories
                    merged_memory = self._merge_memories(group)
                    
                    # Save merged memory
                    merged_id = self.add(merged_memory.to_dict())
                    
                    # Delete originals
                    for memory in group:
                        if memory.id is not None:
                            self.delete(memory.id)
                    
                    results["merged"] += 1
                    results["deleted"] += len(group)
            
            # Archive old memories
            archived = self._archive_old_memories()
            results["archived"] += archived
            
            # Update last consolidation time
            self._last_consolidation = time.time()
            
            results["duration"] = time.time() - start_time
            
            self.audit_logger.log(
                "MEMORY_CONSOLIDATE_SUCCESS",
                f"Consolidated in {results['duration']:.2f}s"
            )
            
            return results
        
        except Exception as e:
            self.audit_logger.log("MEMORY_CONSOLIDATE_FAIL", str(e))
            logging.error(f"Memory consolidation failed: {e}")
            return {"error": str(e), **results}
    
    def _group_similar_memories(self, memories: List[Memory]) -> List[List[Memory]]:
        """
        Group similar memories together.
        
        Args:
            memories: List of memories to group.
            
        Returns:
            List[List[Memory]]: Groups of similar memories.
        """
        # Simple implementation: group by content similarity
        groups = []
        used_indices = set()
        
        for i, memory1 in enumerate(memories):
            if i in used_indices:
                continue
            
            # Find similar memories
            group = [memory1]
            for j, memory2 in enumerate(memories[i+1:], i+1):
                if j in used_indices:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(memory1, memory2)
                
                if similarity > 0.8:  # Threshold for similarity
                    group.append(memory2)
                    used_indices.add(j)
            
            groups.append(group)
        
        return groups
    
    def _calculate_similarity(self, memory1: Memory, memory2: Memory) -> float:
        """
        Calculate similarity between two memories.
        
        Args:
            memory1: First memory.
            memory2: Second memory.
            
        Returns:
            float: Similarity score (0.0 to 1.0).
        """
        # Simple implementation: compare content
        content1 = memory1.content.lower()
        content2 = memory2.content.lower()
        
        # Count common words
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1 & words2
        
        # Jaccard similarity
        return len(common_words) / len(words1 | words2)
    
    def _merge_memories(self, memories: List[Memory]) -> Memory:
        """
        Merge multiple similar memories into one.
        
        Args:
            memories: List of memories to merge.
            
        Returns:
            Memory: Merged memory.
        """
        if not memories:
            raise ValueError("No memories to merge")
        
        # Use the first memory as base
        base_memory = memories[0]
        
        # Combine content
        combined_content = base_memory.content
        for memory in memories[1:]:
            combined_content += f"\n\n---\n\n{memory.content}"
        
        # Create new memory with combined content
        merged_memory = Memory(
            content=combined_content,
            memory_type=base_memory.memory_type,
            importance=base_memory.importance,
            relevance=base_memory.relevance,
            recency=base_memory.recency,
            confidence=base_memory.confidence,
            frequency=sum(m.frequency for m in memories),
            status=MemoryStatus.CONSOLIDATED,
            metadata={
                "merged_from": [m.id for m in memories if m.id is not None],
                "merged_at": time.time(),
            },
        )
        
        return merged_memory
    
    def _archive_old_memories(self) -> int:
        """
        Archive old memories that haven't been accessed recently.
        
        Returns:
            int: Number of memories archived.
        """
        # Get all memories
        memories = self.list_all()
        
        archived_count = 0
        
        for memory in memories:
            # Check if memory is old (recency < 0.2)
            if memory.recency < 0.2 and memory.status == MemoryStatus.ACTIVE:
                memory.status = MemoryStatus.ARCHIVED
                self.update(memory)
                archived_count += 1
        
        return archived_count
    
    def get_stats(self) -> MemoryStats:
        """
        Get statistics about the memories.
        
        Returns:
            MemoryStats: Memory statistics.
        """
        return self.database.get_stats()
    
    def forget(self, memory_id: int) -> bool:
        """
        Mark a memory as forgotten (soft delete).
        
        Args:
            memory_id: ID of the memory to forget.
            
        Returns:
            bool: True if forget succeeded, False otherwise.
        """
        memory = self.get(memory_id)
        
        if not memory:
            return False
        
        memory.status = MemoryStatus.FORGOTTEN
        return self.update(memory)
    
    def doctor(self) -> Dict[str, Any]:
        """
        Run memory system diagnostics.
        
        Returns:
            Dict[str, Any]: Diagnostic results.
        """
        return {
            "database": self.database.doctor(),
            "cache_size": len(self._memory_cache),
            "last_consolidation": self._last_consolidation,
        }
    
    def clear_cache(self) -> None:
        """Clear the memory cache."""
        self._memory_cache = {}
    
    def export_memories(self, format: str = "json") -> str:
        """
        Export all memories in a specified format.
        
        Args:
            format: Export format ("json" or "markdown").
            
        Returns:
            str: Exported memories in the specified format.
        """
        memories = self.list_all()
        
        if format == "json":
            import json
            return json.dumps(
                [memory.to_dict() for memory in memories],
                indent=2
            )
        elif format == "markdown":
            markdown = "# Memory Export\n\n"
            markdown += f"Total memories: {len(memories)}\n\n"
            
            for memory in memories:
                markdown += f"## Memory {memory.id}\n\n"
                markdown += f"- **Type**: {memory.memory_type.value}\n"
                markdown += f"- **Importance**: {memory.importance.value}\n"
                markdown += f"- **Relevance**: {memory.relevance:.2f}\n"
                markdown += f"- **Recency**: {memory.recency:.2f}\n"
                markdown += f"- **Confidence**: {memory.confidence:.2f}\n"
                markdown += f"- **Status**: {memory.status.value}\n"
                markdown += f"- **Created**: {time.ctime(memory.created_at)}\n"
                markdown += f"- **Updated**: {time.ctime(memory.updated_at)}\n\n"
                markdown += f"{memory.content}\n\n"
                markdown += "---\n\n"
            
            return markdown
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_memories(self, data: str, format: str = "json") -> int:
        """
        Import memories from a specified format.
        
        Args:
            data: Data to import.
            format: Import format ("json" or "markdown").
            
        Returns:
            int: Number of memories imported.
        """
        if format == "json":
            import json
            memories_data = json.loads(data)
            
            for memory_data in memories_data:
                self.add(memory_data)
            
            return len(memories_data)
        else:
            raise ValueError(f"Unsupported import format: {format}")
