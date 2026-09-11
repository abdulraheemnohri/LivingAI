# LivingAI Cognitive Engine
# ========================
# This module implements the core cognitive loop for LivingAI.

import logging
import time
from typing import Dict, Any, Optional, List, Union

# Local imports
from .context import ContextBuilder
from .reasoning import ReasoningEngine
from .planner import Planner
from .decision import DecisionEngine
from .reflection import ReflectionEngine
from ..config import ConfigManager
from ..memory.manager import MemoryManager
from ..ai.model_manager import ModelManager
from ..security.audit import AuditLogger


class CognitiveEngine:
    """
    Implements the core cognitive loop for LivingAI.
    
    The cognitive loop follows this pattern:
    PERCEIVE -> REMEMBER -> UNDERSTAND -> THINK -> PLAN -> DECIDE -> ACT -> OBSERVE -> REFLECT -> LEARN -> CONSOLIDATE
    
    This class orchestrates all these steps and maintains the system's cognitive state.
    """
    
    # Cognitive state
    COGNITIVE_STATES = [
        "IDLE",
        "PERCEIVING",
        "REMEMBERING",
        "UNDERSTANDING",
        "THINKING",
        "PLANNING",
        "DECIDING",
        "ACTING",
        "OBSERVING",
        "REFLECTING",
        "LEARNING",
        "CONSOLIDATING",
    ]
    
    def __init__(
        self,
        model_manager: ModelManager,
        config: ConfigManager,
        audit_logger: AuditLogger,
        memory_manager: Optional[MemoryManager] = None
    ):
        """
        Initialize the CognitiveEngine.
        
        Args:
            model_manager: Model manager for AI inference.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
            memory_manager: Optional memory manager (can be set later).
        """
        self.model_manager = model_manager
        self.config = config
        self.audit_logger = audit_logger
        self.memory_manager = memory_manager
        
        # Initialize components
        self.context_builder = ContextBuilder(
            memory_manager=self.memory_manager,
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        self.reasoning_engine = ReasoningEngine(
            model_manager=self.model_manager,
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        self.planner = Planner(
            memory_manager=self.memory_manager,
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        self.decision_engine = DecisionEngine(
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        self.reflection_engine = ReflectionEngine(
            memory_manager=self.memory_manager,
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Cognitive state
        self._current_state = "IDLE"
        self._last_activity_time = time.time()
        self._conversation_context: Dict[str, Any] = {}
        self._current_goal: Optional[Dict[str, Any]] = None
        self._current_plan: Optional[List[Dict[str, Any]]] = None
        
        logging.info("CognitiveEngine initialized")
        self.audit_logger.log("COGNITIVE_ENGINE_INIT", "Cognitive engine initialized")
    
    def set_memory_manager(self, memory_manager: MemoryManager) -> None:
        """
        Set the memory manager (for lazy initialization).
        
        Args:
            memory_manager: Memory manager instance.
        """
        self.memory_manager = memory_manager
        self.context_builder.set_memory_manager(memory_manager)
        self.planner.set_memory_manager(memory_manager)
        self.reflection_engine.set_memory_manager(memory_manager)
    
    def get_state(self) -> str:
        """Get the current cognitive state."""
        return self._current_state
    
    def set_state(self, state: str) -> None:
        """
        Set the current cognitive state.
        
        Args:
            state: New cognitive state.
        """
        if state not in self.COGNITIVE_STATES:
            logging.warning(f"Unknown cognitive state: {state}")
            return
        
        self._current_state = state
        self._last_activity_time = time.time()
        logging.debug(f"Cognitive state changed to: {state}")
        self.audit_logger.log("COGNITIVE_STATE_CHANGE", f"State: {state}")
    
    def process(
        self,
        input_text: str,
        **kwargs
    ) -> str:
        """
        Process an input through the full cognitive loop.
        
        This is the main entry point for the cognitive engine.
        
        Args:
            input_text: The user's input text.
            **kwargs: Additional processing parameters.
            
        Returns:
            str: The AI's response.
        """
        self.set_state("PERCEIVING")
        self.audit_logger.log("COGNITIVE_PROCESS_START", f"Input: {input_text[:50]}...")
        
        try:
            # Step 1: PERCEIVE - Receive and parse the input
            self.set_state("PERCEIVING")
            perception_result = self._perceive(input_text)
            
            # Step 2: REMEMBER - Retrieve relevant memories
            self.set_state("REMEMBERING")
            memory_context = self._remember(perception_result)
            
            # Step 3: UNDERSTAND - Build context
            self.set_state("UNDERSTANDING")
            context = self._understand(perception_result, memory_context)
            
            # Step 4: THINK - Process with the model
            self.set_state("THINKING")
            thoughts = self._think(context)
            
            # Step 5: PLAN - Create a plan if needed
            self.set_state("PLANNING")
            plan = self._plan(context, thoughts)
            
            # Step 6: DECIDE - Make decisions
            self.set_state("DECIDING")
            decisions = self._decide(context, thoughts, plan)
            
            # Step 7: ACT - Execute actions (if any)
            self.set_state("ACTING")
            actions = self._act(decisions)
            
            # Step 8: OBSERVE - Observe the results
            self.set_state("OBSERVING")
            observations = self._observe(actions)
            
            # Step 9: REFLECT - Reflect on the interaction
            self.set_state("REFLECTING")
            reflections = self._reflect(context, actions, observations)
            
            # Step 10: LEARN - Learn from the interaction
            self.set_state("LEARNING")
            self._learn(reflections)
            
            # Step 11: CONSOLIDATE - Consolidate memories
            self.set_state("CONSOLIDATING")
            self._consolidate()
            
            # Return the final response
            self.set_state("IDLE")
            response = self._format_response(thoughts, plan, decisions, actions, reflections)
            
            self.audit_logger.log("COGNITIVE_PROCESS_SUCCESS", "Processing completed")
            return response
            
        except Exception as e:
            self.set_state("IDLE")
            self.audit_logger.log("COGNITIVE_PROCESS_FAIL", str(e))
            logging.error(f"Cognitive processing failed: {e}")
            return f"I encountered an error processing your request: {str(e)}"
    
    def process_streaming(
        self,
        input_text: str,
        **kwargs
    ) -> Any:
        """
        Process an input with streaming output.
        
        Args:
            input_text: The user's input text.
            **kwargs: Additional processing parameters.
            
        Yields:
            str: Chunks of the AI's response.
        """
        # For streaming, we'll process in chunks
        # This is a simplified version - in practice, we'd stream tokens from the model
        
        self.set_state("PERCEIVING")
        self.audit_logger.log("COGNITIVE_STREAM_START", f"Input: {input_text[:50]}...")
        
        try:
            # Build context
            self.set_state("UNDERSTANDING")
            context = self._build_full_context(input_text)
            
            # Stream the response from the model
            self.set_state("THINKING")
            
            # Use the model's streaming capability
            stream = self.model_manager.generate_streaming(
                self._format_prompt(context),
                **kwargs
            )
            
            for chunk in stream:
                self.set_state("ACTING")  # Streaming is part of the action
                yield chunk
            
            # After streaming, do reflection and learning
            self.set_state("REFLECTING")
            self._reflect_on_streaming(input_text)
            
            self.set_state("IDLE")
            self.audit_logger.log("COGNITIVE_STREAM_SUCCESS", "Streaming completed")
            
        except Exception as e:
            self.set_state("IDLE")
            self.audit_logger.log("COGNITIVE_STREAM_FAIL", str(e))
            logging.error(f"Streaming processing failed: {e}")
            yield f"I encountered an error: {str(e)}"
    
    def _perceive(self, input_text: str) -> Dict[str, Any]:
        """
        PERCEIVE: Parse and analyze the input.
        
        Args:
            input_text: The user's input.
            
        Returns:
            Dict[str, Any]: Perception result with parsed input.
        """
        # Basic perception: just pass through for now
        # In a real implementation, this would include:
        # - Intent detection
        # - Entity extraction
        # - Sentiment analysis
        # - Command parsing
        
        return {
            "raw_input": input_text,
            "timestamp": time.time(),
            "type": self._detect_input_type(input_text),
        }
    
    def _detect_input_type(self, input_text: str) -> str:
        """
        Detect the type of input (question, command, statement, etc.).
        
        Args:
            input_text: The input text.
            
        Returns:
            str: Input type.
        """
        input_text = input_text.strip().lower()
        
        if input_text.endswith("?"):
            return "question"
        elif input_text.startswith(("remember", "create", "add", "delete", "show", "list")):
            return "command"
        elif any(word in input_text for word in ["how", "what", "why", "when", "where"]):
            return "question"
        else:
            return "statement"
    
    def _remember(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        REMEMBER: Retrieve relevant memories.
        
        Args:
            perception: The perception result.
            
        Returns:
            Dict[str, Any]: Memory context.
        """
        if not self.memory_manager:
            return {"memories": []}
        
        # Search for relevant memories
        query = perception.get("raw_input", "")
        memories = self.memory_manager.search(query, limit=5)
        
        return {
            "memories": memories,
            "query": query,
        }
    
    def _understand(
        self,
        perception: Dict[str, Any],
        memory_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        UNDERSTAND: Build context from perception and memories.
        
        Args:
            perception: The perception result.
            memory_context: The memory context.
            
        Returns:
            Dict[str, Any]: Full context for processing.
        """
        return self.context_builder.build(
            perception=perception,
            memory_context=memory_context
        )
    
    def _build_full_context(self, input_text: str) -> Dict[str, Any]:
        """
        Build a full context for processing.
        
        Args:
            input_text: The user's input.
            
        Returns:
            Dict[str, Any]: Full context.
        """
        perception = self._perceive(input_text)
        memory_context = self._remember(perception)
        return self._understand(perception, memory_context)
    
    def _think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        THINK: Process the context with the AI model.
        
        Args:
            context: The full context.
            
        Returns:
            Dict[str, Any]: Thoughts and reasoning from the model.
        """
        # Format the context as a prompt for the model
        prompt = self._format_prompt(context)
        
        # Get generation parameters
        generation_config = self.config.get("generation", {})
        
        # Generate a response
        response = self.model_manager.generate(
            prompt,
            temperature=generation_config.get("temperature", 0.7),
            max_tokens=generation_config.get("max_tokens", 512)
        )
        
        return {
            "prompt": prompt,
            "response": response,
            "context": context,
        }
    
    def _format_prompt(self, context: Dict[str, Any]) -> str:
        """
        Format the context as a prompt for the model.
        
        Args:
            context: The full context.
            
        Returns:
            str: Formatted prompt.
        """
        # Basic prompt formatting
        # In a real implementation, this would include:
        # - System prompt
        # - Memory context
        # - Current conversation
        # - User input
        
        user_input = context.get("perception", {}).get("raw_input", "")
        memories = context.get("memory_context", {}).get("memories", [])
        
        # Build memory context string
        memory_str = ""
        if memories:
            memory_str = "\n\nRelevant memories:\n"
            for i, memory in enumerate(memories, 1):
                memory_str += f"{i}. {memory.get('content', '')}\n"
        
        # Build the full prompt
        prompt = f"""You are LivingAI, a helpful AI assistant running in Termux on Android.

Current context:{memory_str}

User: {user_input}

Assistant:"""
        
        return prompt
    
    def _plan(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        PLAN: Create a plan based on context and thoughts.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            
        Returns:
            Optional[List[Dict[str, Any]]]: A plan with steps, or None if no plan needed.
        """
        # Check if planning is needed
        input_type = context.get("perception", {}).get("type", "statement")
        
        if input_type == "command":
            # For commands, we might not need a plan
            return None
        
        # Use the planner to create a plan
        return self.planner.create_plan(context, thoughts)
    
    def _decide(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any],
        plan: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        DECIDE: Make decisions based on context, thoughts, and plan.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            plan: The plan (if any).
            
        Returns:
            Dict[str, Any]: Decisions to be acted upon.
        """
        return self.decision_engine.decide(
            context=context,
            thoughts=thoughts,
            plan=plan
        )
    
    def _act(self, decisions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        ACT: Execute actions based on decisions.
        
        Args:
            decisions: The decisions to act upon.
            
        Returns:
            List[Dict[str, Any]]: Results of the actions.
        """
        # In a real implementation, this would:
        # 1. Check action permissions
        # 2. Execute safe actions
        # 3. Request confirmation for risky actions
        # 4. Return action results
        
        actions = decisions.get("actions", [])
        results = []
        
        for action in actions:
            # Simulate action execution
            result = {
                "action": action,
                "status": "simulated",
                "result": f"Action '{action}' would be executed here.",
            }
            results.append(result)
        
        return results
    
    def _observe(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        OBSERVE: Observe the results of actions.
        
        Args:
            actions: The actions that were executed.
            
        Returns:
            Dict[str, Any]: Observations from the actions.
        """
        observations = {
            "actions": actions,
            "timestamp": time.time(),
        }
        
        # In a real implementation, this would:
        # - Capture action outputs
        # - Check for errors
        # - Monitor system state changes
        
        return observations
    
    def _reflect(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        REFLECT: Reflect on the interaction.
        
        Args:
            context: The full context.
            actions: The actions that were executed.
            observations: The observations from the actions.
            
        Returns:
            Dict[str, Any]: Reflections and insights.
        """
        return self.reflection_engine.reflect(
            context=context,
            actions=actions,
            observations=observations
        )
    
    def _learn(self, reflections: Dict[str, Any]) -> None:
        """
        LEARN: Learn from the reflections.
        
        Args:
            reflections: The reflections to learn from.
        """
        # In a real implementation, this would:
        # - Extract lessons
        # - Update memories
        # - Improve skills
        
        if self.memory_manager:
            # Store the interaction in memory
            user_input = reflections.get("context", {}).get("perception", {}).get("raw_input", "")
            response = reflections.get("thoughts", {}).get("response", "")
            
            self.memory_manager.add({
                "content": f"User: {user_input}\nAI: {response}",
                "type": "conversation",
                "importance": 0.8,
                "relevance": 0.9,
                "recency": 1.0,
            })
    
    def _consolidate(self) -> None:
        """
        CONSOLIDATE: Consolidate memories and knowledge.
        """
        if self.memory_manager:
            self.memory_manager.consolidate()
    
    def _format_response(
        self,
        thoughts: Dict[str, Any],
        plan: Optional[List[Dict[str, Any]]],
        decisions: Dict[str, Any],
        actions: List[Dict[str, Any]],
        reflections: Dict[str, Any]
    ) -> str:
        """
        Format the final response to the user.
        
        Args:
            thoughts: The thoughts from the model.
            plan: The plan (if any).
            decisions: The decisions made.
            actions: The actions executed.
            reflections: The reflections.
            
        Returns:
            str: Formatted response.
        """
        # Start with the model's response
        response = thoughts.get("response", "")
        
        # Add plan information if there's a plan
        if plan:
            response += "\n\nPlan:"
            for i, step in enumerate(plan, 1):
                response += f"\n{i}. {step.get('description', step.get('action', 'Unknown'))}"
        
        # Add action results if there are actions
        if actions:
            response += "\n\nActions taken:"
            for action in actions:
                response += f"\n- {action.get('result', 'No result')}"
        
        return response
    
    def _reflect_on_streaming(self, input_text: str) -> None:
        """
        Reflect on a streaming interaction.
        
        Args:
            input_text: The user's input.
        """
        # In a real implementation, this would:
        # - Store the interaction in memory
        # - Update conversation context
        
        if self.memory_manager:
            self.memory_manager.add({
                "content": f"Streaming interaction: {input_text[:50]}...",
                "type": "conversation",
                "importance": 0.7,
                "relevance": 0.8,
                "recency": 1.0,
            })
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """
        Get the current conversation context.
        
        Returns:
            Dict[str, Any]: Current conversation context.
        """
        return self._conversation_context
    
    def set_conversation_context(self, context: Dict[str, Any]) -> None:
        """
        Set the current conversation context.
        
        Args:
            context: New conversation context.
        """
        self._conversation_context = context
    
    def get_current_goal(self) -> Optional[Dict[str, Any]]:
        """
        Get the current active goal.
        
        Returns:
            Optional[Dict[str, Any]]: Current goal, or None if none.
        """
        return self._current_goal
    
    def set_current_goal(self, goal: Optional[Dict[str, Any]]) -> None:
        """
        Set the current active goal.
        
        Args:
            goal: Goal to set as current, or None to clear.
        """
        self._current_goal = goal
    
    def get_current_plan(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get the current plan.
        
        Returns:
            Optional[List[Dict[str, Any]]]: Current plan, or None if none.
        """
        return self._current_plan
    
    def set_current_plan(self, plan: Optional[List[Dict[str, Any]]]) -> None:
        """
        Set the current plan.
        
        Args:
            plan: Plan to set as current, or None to clear.
        """
        self._current_plan = plan
