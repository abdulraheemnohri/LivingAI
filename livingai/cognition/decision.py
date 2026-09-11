# LivingAI Decision Engine
# ========================
# This module handles decision-making for the cognitive engine.

import logging
import time
from typing import Dict, Any, Optional, List
from enum import Enum

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class DecisionType(Enum):
    """Types of decisions the engine can make."""
    ACTION = "action"
    RESPONSE = "response"
    PLAN = "plan"
    MEMORY = "memory"
    GOAL = "goal"


class DecisionEngine:
    """
    Handles decision-making for the cognitive engine.
    
    Responsibilities:
    - Make decisions based on context and thoughts
    - Evaluate options
    - Apply decision policies
    - Track decision history
    """
    
    def __init__(
        self,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the DecisionEngine.
        
        Args:
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.config = config
        self.audit_logger = audit_logger
        
        # Decision state
        self._decision_history: List[Dict[str, Any]] = []
        self._current_decision: Optional[Dict[str, Any]] = None
        
        # Decision policies
        self._policies = {
            "action": self._get_action_policy(),
            "response": self._get_response_policy(),
            "plan": self._get_plan_policy(),
            "memory": self._get_memory_policy(),
            "goal": self._get_goal_policy(),
        }
        
        logging.info("DecisionEngine initialized")
    
    def decide(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any],
        plan: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Make decisions based on context, thoughts, and plan.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            plan: Optional plan to consider.
            
        Returns:
            Dict[str, Any]: Decisions to be acted upon.
        """
        self.audit_logger.log("DECISION_START", "Starting decision process")
        
        try:
            decisions = {
                "timestamp": time.time(),
                "context": context,
                "thoughts": thoughts,
                "decisions": [],
                "actions": [],
                "responses": [],
            }
            
            # Determine what type of decision we need to make
            decision_type = self._determine_decision_type(context, thoughts, plan)
            
            # Apply the appropriate decision policy
            if decision_type == DecisionType.ACTION:
                action_decisions = self._make_action_decisions(context, thoughts, plan)
                decisions["decisions"].extend(action_decisions.get("decisions", []))
                decisions["actions"].extend(action_decisions.get("actions", []))
            
            if decision_type == DecisionType.RESPONSE or decision_type == DecisionType.ACTION:
                response_decisions = self._make_response_decisions(context, thoughts)
                decisions["decisions"].extend(response_decisions.get("decisions", []))
                decisions["responses"].extend(response_decisions.get("responses", []))
            
            if decision_type == DecisionType.PLAN and plan:
                plan_decisions = self._make_plan_decisions(context, thoughts, plan)
                decisions["decisions"].extend(plan_decisions.get("decisions", []))
            
            if decision_type == DecisionType.MEMORY:
                memory_decisions = self._make_memory_decisions(context, thoughts)
                decisions["decisions"].extend(memory_decisions.get("decisions", []))
            
            if decision_type == DecisionType.GOAL:
                goal_decisions = self._make_goal_decisions(context, thoughts)
                decisions["decisions"].extend(goal_decisions.get("decisions", []))
            
            # Add to decision history
            self._decision_history.append(decisions)
            self._current_decision = decisions
            
            self.audit_logger.log(
                "DECISION_SUCCESS",
                f"Made {len(decisions['decisions'])} decisions"
            )
            
            return decisions
            
        except Exception as e:
            self.audit_logger.log("DECISION_FAIL", str(e))
            logging.error(f"Decision making failed: {e}")
            return {
                "error": str(e),
                "decisions": [],
                "actions": [],
                "responses": [],
            }
    
    def _determine_decision_type(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any],
        plan: Optional[List[Dict[str, Any]]]
    ) -> DecisionType:
        """
        Determine what type of decision needs to be made.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            plan: Optional plan.
            
        Returns:
            DecisionType: The type of decision to make.
        """
        # Check if there's a plan to execute
        if plan:
            return DecisionType.PLAN
        
        # Check input type
        input_type = context.get("perception", {}).get("type", "statement")
        
        if input_type == "command":
            return DecisionType.ACTION
        
        # Check if this is a question
        if input_type == "question":
            return DecisionType.RESPONSE
        
        # Check the thoughts for action indicators
        response = thoughts.get("response", "").lower()
        
        action_indicators = [
            "i should",
            "let's",
            "we need to",
            "i will",
            "execute",
            "run",
            "do",
        ]
        
        for indicator in action_indicators:
            if indicator in response:
                return DecisionType.ACTION
        
        # Default to response
        return DecisionType.RESPONSE
    
    def _make_action_decisions(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any],
        plan: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Make decisions about actions to take.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            plan: Optional plan.
            
        Returns:
            Dict[str, Any]: Action decisions.
        """
        decisions = {
            "type": "action",
            "decisions": [],
            "actions": [],
        }
        
        # If there's a plan, use its next step
        if plan:
            next_step = self._get_next_plan_step(plan)
            if next_step:
                action = next_step.get("action", "")
                if action:
                    decisions["actions"].append({
                        "type": "plan_step",
                        "action": action,
                        "description": next_step.get("description", ""),
                        "step_id": next_step.get("id"),
                    })
        
        # Check the thoughts for action suggestions
        response = thoughts.get("response", "")
        actions = self._extract_actions_from_text(response)
        
        for action in actions:
            decisions["actions"].append({
                "type": "suggested",
                "action": action,
                "source": "model_response",
            })
        
        # Apply action policy
        decisions["actions"] = self._apply_action_policy(decisions["actions"])
        
        return decisions
    
    def _make_response_decisions(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make decisions about responses to give.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            
        Returns:
            Dict[str, Any]: Response decisions.
        """
        decisions = {
            "type": "response",
            "decisions": [],
            "responses": [],
        }
        
        # Primary response is from the model
        response = thoughts.get("response", "")
        if response:
            decisions["responses"].append({
                "type": "primary",
                "response": response,
                "source": "model",
            })
        
        # Check if we need to add any additional responses
        # (e.g., clarifications, follow-up questions)
        additional_responses = self._get_additional_responses(context, thoughts)
        decisions["responses"].extend(additional_responses)
        
        return decisions
    
    def _make_plan_decisions(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any],
        plan: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Make decisions about plan execution.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            plan: The plan to execute.
            
        Returns:
            Dict[str, Any]: Plan decisions.
        """
        decisions = {
            "type": "plan",
            "decisions": [],
        }
        
        # Check if we should start executing the plan
        should_execute = self._should_execute_plan(context, thoughts, plan)
        
        if should_execute:
            decisions["decisions"].append({
                "type": "execute_plan",
                "plan": plan,
                "status": "approved",
            })
        else:
            decisions["decisions"].append({
                "type": "execute_plan",
                "plan": plan,
                "status": "pending_confirmation",
            })
        
        return decisions
    
    def _make_memory_decisions(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make decisions about memory operations.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            
        Returns:
            Dict[str, Any]: Memory decisions.
        """
        decisions = {
            "type": "memory",
            "decisions": [],
        }
        
        # Check if we should remember something
        input_text = context.get("perception", {}).get("raw_input", "")
        response = thoughts.get("response", "")
        
        # Simple heuristic: if the user says "remember this", we should remember
        if "remember" in input_text.lower():
            decisions["decisions"].append({
                "type": "remember",
                "content": response,
                "priority": 0.9,
            })
        
        return decisions
    
    def _make_goal_decisions(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make decisions about goal operations.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            
        Returns:
            Dict[str, Any]: Goal decisions.
        """
        decisions = {
            "type": "goal",
            "decisions": [],
        }
        
        # Check if we should create a new goal
        input_text = context.get("perception", {}).get("raw_input", "")
        
        goal_indicators = [
            "i want to",
            "my goal is",
            "i need to",
            "let's",
        ]
        
        for indicator in goal_indicators:
            if indicator in input_text.lower():
                decisions["decisions"].append({
                    "type": "create_goal",
                    "description": input_text,
                    "priority": 0.8,
                })
                break
        
        return decisions
    
    def _get_next_plan_step(self, plan: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Get the next step to execute from a plan.
        
        Args:
            plan: The plan.
            
        Returns:
            Optional[Dict[str, Any]]: Next step to execute, or None.
        """
        for step in plan:
            if step.get("status") == "PENDING":
                return step
        return None
    
    def _extract_actions_from_text(self, text: str) -> List[str]:
        """
        Extract potential actions from text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            List[str]: List of extracted actions.
        """
        # Simple extraction - in a real implementation, this would be more sophisticated
        actions = []
        
        # Look for imperative statements
        lines = text.split(".")
        for line in lines:
            line = line.strip()
            if line and line[0].isupper():
                # Might be a command or action
                actions.append(line)
        
        return actions
    
    def _apply_action_policy(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply the action policy to filter or modify actions.
        
        Args:
            actions: List of proposed actions.
            
        Returns:
            List[Dict[str, Any]]: Filtered list of actions.
        """
        policy = self._policies.get("action", {})
        
        # Get allowed actions
        allowed_actions = policy.get("allowed", [])
        blocked_actions = policy.get("blocked", [])
        
        filtered_actions = []
        for action in actions:
            action_name = action.get("action", "").lower()
            
            # Check if blocked
            if any(blocked in action_name for blocked in blocked_actions):
                logging.warning(f"Action blocked by policy: {action_name}")
                continue
            
            # Check if allowed or if we need confirmation
            if any(allowed in action_name for allowed in allowed_actions):
                action["confirmation_required"] = False
            else:
                action["confirmation_required"] = True
            
            filtered_actions.append(action)
        
        return filtered_actions
    
    def _get_additional_responses(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get any additional responses that should be given.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            
        Returns:
            List[Dict[str, Any]]: Additional responses.
        """
        # In a real implementation, this would analyze the context
        # and determine if additional responses are needed
        return []
    
    def _should_execute_plan(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any],
        plan: List[Dict[str, Any]]
    ) -> bool:
        """
        Determine if we should start executing a plan.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            plan: The plan to potentially execute.
            
        Returns:
            bool: True if we should execute the plan, False otherwise.
        """
        # Check if auto-execution is enabled
        auto_execute = self.config.get("autonomy.auto_execute_plans", False)
        
        if auto_execute:
            return True
        
        # Check if the user explicitly requested execution
        input_text = context.get("perception", {}).get("raw_input", "").lower()
        
        execution_indicators = [
            "start",
            "begin",
            "execute",
            "do it",
            "go ahead",
        ]
        
        return any(indicator in input_text for indicator in execution_indicators)
    
    def _get_action_policy(self) -> Dict[str, Any]:
        """
        Get the action policy from configuration.
        
        Returns:
            Dict[str, Any]: Action policy.
        """
        return {
            "allowed": self.config.get("actions.allowed", []),
            "blocked": self.config.get("actions.blocked", ["rm -rf", "dd", "format"]),
            "confirmation_required": self.config.get("actions.confirmation_required", True),
        }
    
    def _get_response_policy(self) -> Dict[str, Any]:
        """
        Get the response policy from configuration.
        
        Returns:
            Dict[str, Any]: Response policy.
        """
        return {
            "max_length": self.config.get("generation.max_tokens", 512),
            "require_clarification": self.config.get("response.require_clarification", False),
        }
    
    def _get_plan_policy(self) -> Dict[str, Any]:
        """
        Get the plan policy from configuration.
        
        Returns:
            Dict[str, Any]: Plan policy.
        """
        return {
            "auto_execute": self.config.get("autonomy.auto_execute_plans", False),
            "max_steps": self.config.get("planning.max_steps", 10),
        }
    
    def _get_memory_policy(self) -> Dict[str, Any]:
        """
        Get the memory policy from configuration.
        
        Returns:
            Dict[str, Any]: Memory policy.
        """
        return {
            "auto_remember": self.config.get("memory.auto_remember", True),
            "min_importance": self.config.get("memory.min_importance", 0.5),
        }
    
    def _get_goal_policy(self) -> Dict[str, Any]:
        """
        Get the goal policy from configuration.
        
        Returns:
            Dict[str, Any]: Goal policy.
        """
        return {
            "auto_create": self.config.get("goals.auto_create", True),
            "max_active": self.config.get("goals.max_active", 5),
        }
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of decisions.
        
        Returns:
            List[Dict[str, Any]]: Decision history.
        """
        return self._decision_history.copy()
    
    def get_current_decision(self) -> Optional[Dict[str, Any]]:
        """
        Get the current decision.
        
        Returns:
            Optional[Dict[str, Any]]: Current decision, or None.
        """
        return self._current_decision
    
    def clear_decision_history(self) -> None:
        """Clear the decision history."""
        self._decision_history = []
        self._current_decision = None
