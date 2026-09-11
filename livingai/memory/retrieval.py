# LivingAI Memory Retrieval
# ==========================
# This module handles memory retrieval and search operations.

import logging
from typing import Dict, Any, Optional, List

# Local imports
from .models import Memory, MemoryType, MemorySearchResult
from .manager import MemoryManager


class MemoryRetriever:
    """
    Handles memory retrieval and search operations.
    
    Responsibilities:
    - Search for memories
    - Retrieve memories by various criteria
    - Rank and filter memories
    - Provide context for the cognitive engine
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize the MemoryRetriever.
        
        Args:
            memory_manager: Memory manager for accessing memories.
        """
        self.memory_manager = memory_manager
        
        logging.info("MemoryRetriever initialized")
    
    def search(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
        min_relevance: float = 0.0,
        min_confidence: float = 0.0
    ) -> List[MemorySearchResult]:
        """
        Search for memories matching a query.
        
        Args:
            query: Search query (text to match in content).
            memory_type: Optional memory type filter.
            limit: Maximum number of results to return.
            min_relevance: Minimum relevance score for results.
            min_confidence: Minimum confidence score for results.
            
        Returns:
            List[MemorySearchResult]: List of search results with scores.
        """
        # Search for memories
        memories = self.memory_manager.search(query, memory_type, limit * 2)  # Get extra for filtering
        
        # Filter and score results
        results = []
        for memory in memories:
            # Check minimum scores
            if memory.relevance < min_relevance or memory.confidence < min_confidence:
                continue
            
            # Calculate query-specific score
            query_score = self._calculate_query_score(memory, query)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(memory, query_score)
            
            results.append(MemorySearchResult(
                memory=memory,
                score=overall_score,
                matches=self._find_matches(memory.content, query)
            ))
        
        # Sort by score (descending)
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Return top results
        return results[:limit]
    
    def _calculate_query_score(self, memory: Memory, query: str) -> float:
        """
        Calculate a query-specific score for a memory.
        
        Args:
            memory: The memory to score.
            query: The search query.
            
        Returns:
            float: Query-specific score (0.0 to 1.0).
        """
        # Count exact matches
        query_terms = query.lower().split()
        content = memory.content.lower()
        
        exact_matches = sum(1 for term in query_terms if term in content)
        
        if len(query_terms) == 0:
            return 0.0
        
        # Normalize by query length
        return min(exact_matches / len(query_terms), 1.0)
    
    def _calculate_overall_score(self, memory: Memory, query_score: float) -> float:
        """
        Calculate an overall score for a memory.
        
        Args:
            memory: The memory to score.
            query_score: The query-specific score.
            
        Returns:
            float: Overall score (0.0 to 1.0).
        """
        # Weight factors
        weights = {
            "query": 0.4,
            "ranking": 0.3,
            "recency": 0.2,
            "confidence": 0.1,
        }
        
        # Calculate weighted score
        score = (
            weights["query"] * query_score +
            weights["ranking"] * memory.get_ranking_score() +
            weights["recency"] * memory.recency +
            weights["confidence"] * memory.confidence
        )
        
        return min(max(score, 0.0), 1.0)
    
    def _find_matches(self, content: str, query: str) -> List[str]:
        """
        Find matching terms between content and query.
        
        Args:
            content: Memory content.
            query: Search query.
            
        Returns:
            List[str]: List of matching terms.
        """
        query_terms = query.lower().split()
        content_terms = content.lower().split()
        
        return [term for term in query_terms if term in content_terms]
    
    def retrieve_by_type(
        self,
        memory_type: MemoryType,
        limit: int = 10
    ) -> List[Memory]:
        """
        Retrieve memories of a specific type.
        
        Args:
            memory_type: Type of memories to retrieve.
            limit: Maximum number of memories to return.
            
        Returns:
            List[Memory]: List of memories of the specified type.
        """
        # Get all memories and filter by type
        all_memories = self.memory_manager.list_all(limit)
        return [m for m in all_memories if m.memory_type == memory_type]
    
    def retrieve_by_importance(
        self,
        importance: MemoryImportance,
        limit: int = 10
    ) -> List[Memory]:
        """
        Retrieve memories of a specific importance level.
        
        Args:
            importance: Importance level of memories to retrieve.
            limit: Maximum number of memories to return.
            
        Returns:
            List[Memory]: List of memories with the specified importance.
        """
        all_memories = self.memory_manager.list_all(limit)
        return [m for m in all_memories if m.importance == importance]
    
    def retrieve_recent(
        self,
        limit: int = 10,
        min_recency: float = 0.5
    ) -> List[Memory]:
        """
        Retrieve recent memories.
        
        Args:
            limit: Maximum number of memories to return.
            min_recency: Minimum recency score.
            
        Returns:
            List[Memory]: List of recent memories.
        """
        all_memories = self.memory_manager.list_all(limit * 2)
        recent_memories = [m for m in all_memories if m.recency >= min_recency]
        
        # Sort by recency (descending)
        recent_memories.sort(key=lambda x: x.recency, reverse=True)
        
        return recent_memories[:limit]
    
    def retrieve_high_relevance(
        self,
        query: str,
        limit: int = 10,
        min_relevance: float = 0.7
    ) -> List[Memory]:
        """
        Retrieve memories with high relevance to a query.
        
        Args:
            query: Query to match against.
            limit: Maximum number of memories to return.
            min_relevance: Minimum relevance score.
            
        Returns:
            List[Memory]: List of high-relevance memories.
        """
        # Search for memories
        memories = self.memory_manager.search(query, limit=limit * 2)
        
        # Filter by relevance
        high_relevance = [m for m in memories if m.relevance >= min_relevance]
        
        # Sort by relevance (descending)
        high_relevance.sort(key=lambda x: x.relevance, reverse=True)
        
        return high_relevance[:limit]
    
    def retrieve_for_context(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve memories for building context.
        
        Args:
            query: Query or input to build context for.
            limit: Maximum number of memories to retrieve.
            
        Returns:
            Dict[str, Any]: Context with retrieved memories.
        """
        # Search for relevant memories
        search_results = self.search(query, limit=limit)
        
        # Extract memories from results
        memories = [result.memory for result in search_results]
        
        # Update recency for accessed memories
        for memory in memories:
            memory.update_recency()
            self.memory_manager.update(memory)
        
        return {
            "query": query,
            "memories": memories,
            "count": len(memories),
            "search_results": search_results,
        }
    
    def get_related_memories(
        self,
        memory_id: int,
        limit: int = 5
    ) -> List[Memory]:
        """
        Get memories related to a specific memory.
        
        Args:
            memory_id: ID of the memory to find related memories for.
            limit: Maximum number of related memories to return.
            
        Returns:
            List[Memory]: List of related memories.
        """
        # Get the source memory
        source_memory = self.memory_manager.get(memory_id)
        
        if not source_memory:
            return []
        
        # Get all memories
        all_memories = self.memory_manager.list_all()
        
        # Calculate similarity with source memory
        similar_memories = []
        for memory in all_memories:
            if memory.id == memory_id:
                continue
            
            similarity = self._calculate_similarity(source_memory, memory)
            
            if similarity > 0.5:  # Threshold for relatedness
                similar_memories.append((memory, similarity))
        
        # Sort by similarity (descending)
        similar_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the memories (without similarity scores)
        return [memory for memory, similarity in similar_memories[:limit]]
    
    def _calculate_similarity(self, memory1: Memory, memory2: Memory) -> float:
        """
        Calculate similarity between two memories.
        
        Args:
            memory1: First memory.
            memory2: Second memory.
            
        Returns:
            float: Similarity score (0.0 to 1.0).
        """
        # Use the same similarity calculation as in the manager
        content1 = memory1.content.lower()
        content2 = memory2.content.lower()
        
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1 & words2
        return len(common_words) / len(words1 | words2)
    
    def get_memory_context(
        self,
        query: str,
        types: Optional[List[MemoryType]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get a comprehensive memory context for a query.
        
        Args:
            query: Query to build context for.
            types: Optional list of memory types to include.
            limit: Maximum number of memories per type.
            
        Returns:
            Dict[str, Any]: Memory context organized by type.
        """
        context = {
            "query": query,
            "by_type": {},
            "all": [],
        }
        
        # If no types specified, use all types
        if types is None:
            types = list(MemoryType)
        
        # Get memories for each type
        for memory_type in types:
            memories = self.search(query, memory_type=memory_type, limit=limit)
            context["by_type"][memory_type.value] = memories
            context["all"].extend(memories)
        
        # Rank all memories together
        context["all"] = self._rank_memories(context["all"], query)
        
        return context
    
    def _rank_memories(self, memories: List[Memory], query: str) -> List[Memory]:
        """
        Rank memories by relevance to the query.
        
        Args:
            memories: List of memories to rank.
            query: Query to rank against.
            
        Returns:
            List[Memory]: Ranked list of memories.
        """
        # Calculate score for each memory
        scored_memories = []
        for memory in memories:
            query_score = self._calculate_query_score(memory, query)
            overall_score = self._calculate_overall_score(memory, query_score)
            scored_memories.append((memory, overall_score))
        
        # Sort by score (descending)
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the memories
        return [memory for memory, score in scored_memories]
