# LivingAI Memory Consolidation
# ==============================
# This module handles memory consolidation during idle mode.

import logging
import time
from typing import Dict, Any, Optional, List, Tuple

# Local imports
from .models import Memory, MemoryType, MemoryStatus, MemoryImportance
from .manager import MemoryManager


class MemoryConsolidator:
    """
    Handles memory consolidation during idle mode.
    
    Responsibilities:
    - Deduplicate memories
    - Merge similar memories
    - Archive old memories
    - Promote important memories
    - Clean up forgotten memories
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the MemoryConsolidator.
        
        Args:
            memory_manager: Memory manager for accessing memories.
        """
        self.memory_manager = memory_manager
        
        # Consolidation state
        self._last_consolidation_time = time.time()
        self._consolidation_history: List[Dict[str, Any]] = []
        
        logging.info("MemoryConsolidator initialized")
    
    def consolidate(self) -> Dict[str, Any]:
        """
        Run the full memory consolidation process.
        
        Returns:
            Dict[str, Any]: Consolidation results.
        """
        logging.info("Starting memory consolidation")
        start_time = time.time()
        
        results = {
            "start_time": start_time,
            "deduplicated": 0,
            "merged": 0,
            "archived": 0,
            "promoted": 0,
            "cleaned": 0,
            "duration": 0.0,
        }
        
        try:
            # Step 1: Deduplicate memories
            dedup_results = self._deduplicate_memories()
            results["deduplicated"] = dedup_results
            
            # Step 2: Merge similar memories
            merge_results = self._merge_similar_memories()
            results["merged"] = merge_results
            
            # Step 3: Archive old memories
            archive_results = self._archive_old_memories()
            results["archived"] = archive_results
            
            # Step 4: Promote important memories
            promote_results = self._promote_important_memories()
            results["promoted"] = promote_results
            
            # Step 5: Clean up forgotten memories
            clean_results = self._clean_forgotten_memories()
            results["cleaned"] = clean_results
            
            # Update last consolidation time
            self._last_consolidation_time = time.time()
            results["duration"] = time.time() - start_time
            
            # Add to history
            self._consolidation_history.append(results)
            
            logging.info(
                f"Memory consolidation completed in {results['duration']:.2f}s: "
                f"deduplicated={results['deduplicated']}, merged={results['merged']}, "
                f"archived={results['archived']}, promoted={results['promoted']}, "
                f"cleaned={results['cleaned']}"
            )
            
            return results
        
        except Exception as e:
            logging.error(f"Memory consolidation failed: {e}")
            results["error"] = str(e)
            results["duration"] = time.time() - start_time
            return results
    
    def _deduplicate_memories(self) -> int:
        """
        Deduplicate memories with identical content.
        
        Returns:
            int: Number of duplicates removed.
        """
        # Get all memories
        memories = self.memory_manager.list_all()
        
        # Group by content
        content_groups = self._group_by_content(memories)
        
        duplicates_removed = 0
        
        for content, group in content_groups.items():
            if len(group) > 1:
                # Keep the first memory (highest ID or most recent)
                keep_memory = max(group, key=lambda m: m.id or 0)
                
                # Delete the others
                for memory in group:
                    if memory.id != keep_memory.id:
                        self.memory_manager.delete(memory.id)
                        duplicates_removed += 1
                
                # Update the kept memory's frequency
                total_frequency = sum(m.frequency for m in group)
                keep_memory.frequency = total_frequency
                self.memory_manager.update(keep_memory)
        
        return duplicates_removed
    
    def _group_by_content(self, memories: List[Memory]) -> Dict[str, List[Memory]]:
        """
        Group memories by their content.
        
        Args:
            memories: List of memories to group.
            
        Returns:
            Dict[str, List[Memory]]: Groups of memories with identical content.
        """
        groups = {}
        
        for memory in memories:
            content = memory.content.strip()
            if content not in groups:
                groups[content] = []
            groups[content].append(memory)
        
        return groups
    
    def _merge_similar_memories(self) -> int:
        """
        Merge similar memories.
        
        Returns:
            int: Number of merges performed.
        """
        # Get all memories
        memories = self.memory_manager.list_all()
        
        # Group by similarity
        similarity_groups = self._group_by_similarity(memories)
        
        merges_performed = 0
        
        for group in similarity_groups:
            if len(group) > 1:
                # Merge the group
                merged_memory = self._merge_memory_group(group)
                
                # Save the merged memory
                merged_id = self.memory_manager.add(merged_memory.to_dict())
                
                # Delete the originals
                for memory in group:
                    if memory.id is not None:
                        self.memory_manager.delete(memory.id)
                
                merges_performed += 1
        
        return merges_performed
    
    def _group_by_similarity(self, memories: List[Memory]) -> List[List[Memory]]:
        """
        Group memories by similarity.
        
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
                
                if similarity > 0.7:  # Threshold for similarity
                    group.append(memory2)
                    used_indices.add(j)
            
            if len(group) > 1:
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
        content1 = memory1.content.lower()
        content2 = memory2.content.lower()
        
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1 & words2
        return len(common_words) / len(words1 | words2)
    
    def _merge_memory_group(self, memories: List[Memory]) -> Memory:
        """
        Merge a group of similar memories into one.
        
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
            importance=self._get_highest_importance(memories),
            relevance=max(m.relevance for m in memories),
            recency=max(m.recency for m in memories),
            confidence=max(m.confidence for m in memories),
            frequency=sum(m.frequency for m in memories),
            status=MemoryStatus.CONSOLIDATED,
            metadata={
                "merged_from": [m.id for m in memories if m.id is not None],
                "merged_at": time.time(),
                "original_count": len(memories),
            },
        )
        
        return merged_memory
    
    def _get_highest_importance(self, memories: List[Memory]) -> MemoryImportance:
        """
        Get the highest importance level from a list of memories.
        
        Args:
            memories: List of memories.
            
        Returns:
            MemoryImportance: Highest importance level.
        """
        importance_order = {
            MemoryImportance.CRITICAL: 4,
            MemoryImportance.HIGH: 3,
            MemoryImportance.MEDIUM: 2,
            MemoryImportance.LOW: 1,
        }
        
        return max(memories, key=lambda m: importance_order.get(m.importance, 0)).importance
    
    def _archive_old_memories(self) -> int:
        """
        Archive old memories that haven't been accessed recently.
        
        Returns:
            int: Number of memories archived.
        """
        # Get all memories
        memories = self.memory_manager.list_all()
        
        archived_count = 0
        
        for memory in memories:
            # Check if memory is old (recency < 0.3) and not already archived
            if memory.recency < 0.3 and memory.status == MemoryStatus.ACTIVE:
                memory.status = MemoryStatus.ARCHIVED
                self.memory_manager.update(memory)
                archived_count += 1
        
        return archived_count
    
    def _promote_important_memories(self) -> int:
        """
        Promote important memories to long-term memory.
        
        Returns:
            int: Number of memories promoted.
        """
        # Get all memories
        memories = self.memory_manager.list_all()
        
        promoted_count = 0
        
        for memory in memories:
            # Check if memory is important and frequently accessed
            if (
                memory.importance in [MemoryImportance.CRITICAL, MemoryImportance.HIGH] and
                memory.frequency >= 3 and
                memory.memory_type != MemoryType.LONG_TERM and
                memory.status == MemoryStatus.ACTIVE
            ):
                memory.memory_type = MemoryType.LONG_TERM
                memory.recency = 1.0  # Reset recency
                self.memory_manager.update(memory)
                promoted_count += 1
        
        return promoted_count
    
    def _clean_forgotten_memories(self) -> int:
        """
        Clean up memories marked as forgotten.
        
        Returns:
            int: Number of memories cleaned up.
        """
        # Get all memories
        memories = self.memory_manager.list_all()
        
        cleaned_count = 0
        
        for memory in memories:
            if memory.status == MemoryStatus.FORGOTTEN:
                # Check if it's been forgotten for a while
                # In a real implementation, we'd check the updated_at timestamp
                self.memory_manager.delete(memory.id)
                cleaned_count += 1
        
        return cleaned_count
    
    def get_consolidation_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of consolidation operations.
        
        Returns:
            List[Dict[str, Any]]: Consolidation history.
        """
        return self._consolidation_history.copy()
    
    def get_last_consolidation_time(self) -> float:
        """
        Get the timestamp of the last consolidation.
        
        Returns:
            float: Timestamp of last consolidation.
        """
        return self._last_consolidation_time
    
    def clear_history(self) -> None:
        """Clear the consolidation history."""
        self._consolidation_history = []
    
    def get_consolidation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about consolidation operations.
        
        Returns:
            Dict[str, Any]: Consolidation statistics.
        """
        if not self._consolidation_history:
            return {
                "total_operations": 0,
                "total_deduplicated": 0,
                "total_merged": 0,
                "total_archived": 0,
                "total_promoted": 0,
                "total_cleaned": 0,
                "avg_duration": 0.0,
            }
        
        total_operations = len(self._consolidation_history)
        total_deduplicated = sum(op.get("deduplicated", 0) for op in self._consolidation_history)
        total_merged = sum(op.get("merged", 0) for op in self._consolidation_history)
        total_archived = sum(op.get("archived", 0) for op in self._consolidation_history)
        total_promoted = sum(op.get("promoted", 0) for op in self._consolidation_history)
        total_cleaned = sum(op.get("cleaned", 0) for op in self._consolidation_history)
        avg_duration = sum(op.get("duration", 0) for op in self._consolidation_history) / total_operations
        
        return {
            "total_operations": total_operations,
            "total_deduplicated": total_deduplicated,
            "total_merged": total_merged,
            "total_archived": total_archived,
            "total_promoted": total_promoted,
            "total_cleaned": total_cleaned,
            "avg_duration": avg_duration,
        }
