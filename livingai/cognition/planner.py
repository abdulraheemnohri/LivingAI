# LivingAI Planner
# ================
# This module handles planning and task breakdown for the cognitive engine.

import logging
import time
from typing import Dict, Any, Optional, List

# Local imports
from ..config import ConfigManager
from ..memory.manager import MemoryManager
from ..security.audit import AuditLogger


class Planner:
    """
    Handles planning and task breakdown for the cognitive engine.
    
    Responsibilities:
    - Create plans from goals and tasks
    - Break down complex tasks
    - Manage plan execution
    - Track plan progress
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        config: Optional[ConfigManager] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize the Planner.
        
        Args:
            memory_manager: Memory manager for storing plans.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.memory_manager = memory_manager
        self.config = config
        self.audit_logger = audit_logger
        
        # Planning state
        self._current_plan: Optional[List[Dict[str, Any]]] = None
        self._current_goal: Optional[Dict[str, Any]] = None
        self._plan_history: List[Dict[str, Any]] = []
        
        logging.info("Planner initialized")
    
    def set_memory_manager(self, memory_manager: MemoryManager) -> None:
        """
        Set the memory manager (for lazy initialization).
        
        Args:
            memory_manager: Memory manager instance.
        """
        self.memory_manager = memory_manager
    
    def create_plan(
        self,
        context: Dict[str, Any],
        thoughts: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Create a plan based on context and thoughts.
        
        Args:
            context: The full context.
            thoughts: The thoughts from the model.
            
        Returns:
            Optional[List[Dict[str, Any]]]: A plan with steps, or None if no plan needed.
        """
        self.audit_logger.log("PLANNER_CREATE_START", "Creating plan")
        
        try:
            # Extract goal or task from context
            goal = self._extract_goal(context)
            
            if not goal:
                # No specific goal, check if we should create one
                if self._should_create_goal(context):
                    goal = self._create_goal_from_context(context)
                else:
                    # No goal needed
                    self.audit_logger.log("PLANNER_SKIP", "No goal or plan needed")
                    return None
            
            # Set current goal
            self._current_goal = goal
            
            # Break down the goal into steps
            plan = self._break_down_goal(goal)
            
            if plan:
                self._current_plan = plan
                self._plan_history.append({
                    "goal": goal,
                    "plan": plan,
                    "timestamp": time.time(),
                })
                
                self.audit_logger.log(
                    "PLANNER_CREATE_SUCCESS",
                    f"Created plan with {len(plan)} steps"
                )
                return plan
            else:
                self.audit_logger.log("PLANNER_SKIP", "No plan created")
                return None
                
        except Exception as e:
            self.audit_logger.log("PLANNER_CREATE_FAIL", str(e))
            logging.error(f"Failed to create plan: {e}")
            return None
    
    def _extract_goal(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract a goal from the context.
        
        Args:
            context: The full context.
            
        Returns:
            Optional[Dict[str, Any]]: Extracted goal, or None if none found.
        """
        # Check if there's an explicit goal in the context
        if "goal" in context:
            return context["goal"]
        
        # Check if there's a goal in the active goals
        goals_context = context.get("goals", {})
        active_goals = goals_context.get("active_goals", [])
        
        if active_goals:
            # For now, just return the first active goal
            return active_goals[0]
        
        # Check if the input contains goal-like language
        input_text = context.get("perception", {}).get("raw_input", "").lower()
        
        goal_keywords = [
            "i want to",
            "i need to",
            "my goal is",
            "i'd like to",
            "can you help me",
            "how can i",
        ]
        
        for keyword in goal_keywords:
            if keyword in input_text:
                # Extract the goal from the input
                start_idx = input_text.find(keyword) + len(keyword)
                goal_text = input_text[start_idx:].strip()
                
                # Clean up the goal text
                if goal_text.endswith("?"):
                    goal_text = goal_text[:-1]
                
                return {
                    "title": goal_text,
                    "description": f"Goal extracted from input: {goal_text}",
                    "source": "input",
                }
        
        return None
    
    def _should_create_goal(self, context: Dict[str, Any]) -> bool:
        """
        Determine if we should create a goal from the context.
        
        Args:
            context: The full context.
            
        Returns:
            bool: True if we should create a goal, False otherwise.
        """
        # Check input type
        input_type = context.get("perception", {}).get("type", "statement")
        
        if input_type == "command":
            # Commands might not need goals
            return False
        
        # Check for goal-like language
        input_text = context.get("perception", {}).get("raw_input", "").lower()
        
        goal_keywords = [
            "i want",
            "i need",
            "my goal",
            "i'd like",
            "help me",
            "how can",
        ]
        
        return any(keyword in input_text for keyword in goal_keywords)
    
    def _create_goal_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a goal from the context.
        
        Args:
            context: The full context.
            
        Returns:
            Dict[str, Any]: Created goal.
        """
        input_text = context.get("perception", {}).get("raw_input", "")
        
        # Simple goal creation - in a real implementation, this would be more sophisticated
        return {
            "title": input_text[:50],  # Truncate to reasonable length
            "description": f"Goal created from input: {input_text}",
            "source": "context",
            "status": "PLANNED",
            "priority": 1,
        }
    
    def _break_down_goal(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Break down a goal into actionable steps.
        
        Args:
            goal: The goal to break down.
            
        Returns:
            List[Dict[str, Any]]: List of steps to achieve the goal.
        """
        title = goal.get("title", "").lower()
        description = goal.get("description", "")
        
        # Try to understand the goal and create appropriate steps
        if "report" in title or "report" in description:
            return self._create_report_plan(goal)
        elif "learn" in title or "learn" in description:
            return self._create_learning_plan(goal)
        elif "organize" in title or "organize" in description:
            return self._create_organization_plan(goal)
        elif "write" in title or "write" in description:
            return self._create_writing_plan(goal)
        else:
            # Default plan for unknown goals
            return self._create_default_plan(goal)
    
    def _create_report_plan(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a plan for generating a report.
        
        Args:
            goal: The report goal.
            
        Returns:
            List[Dict[str, Any]]: Plan steps for report generation.
        """
        return [
            {
                "id": 1,
                "description": "Gather information and data",
                "action": "gather_data",
                "status": "PENDING",
                "dependencies": [],
            },
            {
                "id": 2,
                "description": "Analyze gathered data",
                "action": "analyze_data",
                "status": "PENDING",
                "dependencies": [1],
            },
            {
                "id": 3,
                "description": "Identify key findings",
                "action": "identify_findings",
                "status": "PENDING",
                "dependencies": [2],
            },
            {
                "id": 4,
                "description": "Create report outline",
                "action": "create_outline",
                "status": "PENDING",
                "dependencies": [3],
            },
            {
                "id": 5,
                "description": "Write report content",
                "action": "write_content",
                "status": "PENDING",
                "dependencies": [4],
            },
            {
                "id": 6,
                "description": "Review and finalize report",
                "action": "review_report",
                "status": "PENDING",
                "dependencies": [5],
            },
        ]
    
    def _create_learning_plan(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a plan for learning something new.
        
        Args:
            goal: The learning goal.
            
        Returns:
            List[Dict[str, Any]]: Plan steps for learning.
        """
        return [
            {
                "id": 1,
                "description": "Identify learning resources",
                "action": "find_resources",
                "status": "PENDING",
                "dependencies": [],
            },
            {
                "id": 2,
                "description": "Study the material",
                "action": "study_material",
                "status": "PENDING",
                "dependencies": [1],
            },
            {
                "id": 3,
                "description": "Take notes on key concepts",
                "action": "take_notes",
                "status": "PENDING",
                "dependencies": [2],
            },
            {
                "id": 4,
                "description": "Practice with exercises",
                "action": "practice_exercises",
                "status": "PENDING",
                "dependencies": [3],
            },
            {
                "id": 5,
                "description": "Review and test understanding",
                "action": "review_understanding",
                "status": "PENDING",
                "dependencies": [4],
            },
        ]
    
    def _create_organization_plan(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a plan for organizing something.
        
        Args:
            goal: The organization goal.
            
        Returns:
            List[Dict[str, Any]]: Plan steps for organization.
        """
        return [
            {
                "id": 1,
                "description": "Assess current organization",
                "action": "assess_organization",
                "status": "PENDING",
                "dependencies": [],
            },
            {
                "id": 2,
                "description": "Identify items to organize",
                "action": "identify_items",
                "status": "PENDING",
                "dependencies": [1],
            },
            {
                "id": 3,
                "description": "Categorize items",
                "action": "categorize_items",
                "status": "PENDING",
                "dependencies": [2],
            },
            {
                "id": 4,
                "description": "Create organization system",
                "action": "create_system",
                "status": "PENDING",
                "dependencies": [3],
            },
            {
                "id": 5,
                "description": "Implement organization",
                "action": "implement_organization",
                "status": "PENDING",
                "dependencies": [4],
            },
        ]
    
    def _create_writing_plan(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a plan for writing something.
        
        Args:
            goal: The writing goal.
            
        Returns:
            List[Dict[str, Any]]: Plan steps for writing.
        """
        return [
            {
                "id": 1,
                "description": "Define purpose and audience",
                "action": "define_purpose",
                "status": "PENDING",
                "dependencies": [],
            },
            {
                "id": 2,
                "description": "Create outline",
                "action": "create_outline",
                "status": "PENDING",
                "dependencies": [1],
            },
            {
                "id": 3,
                "description": "Write first draft",
                "action": "write_draft",
                "status": "PENDING",
                "dependencies": [2],
            },
            {
                "id": 4,
                "description": "Review and revise",
                "action": "review_revise",
                "status": "PENDING",
                "dependencies": [3],
            },
            {
                "id": 5,
                "description": "Finalize and format",
                "action": "finalize_format",
                "status": "PENDING",
                "dependencies": [4],
            },
        ]
    
    def _create_default_plan(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a default plan for unknown goal types.
        
        Args:
            goal: The goal.
            
        Returns:
            List[Dict[str, Any]]: Default plan steps.
        """
        return [
            {
                "id": 1,
                "description": "Understand the goal",
                "action": "understand_goal",
                "status": "PENDING",
                "dependencies": [],
            },
            {
                "id": 2,
                "description": "Identify required actions",
                "action": "identify_actions",
                "status": "PENDING",
                "dependencies": [1],
            },
            {
                "id": 3,
                "description": "Execute actions",
                "action": "execute_actions",
                "status": "PENDING",
                "dependencies": [2],
            },
            {
                "id": 4,
                "description": "Verify completion",
                "action": "verify_completion",
                "status": "PENDING",
                "dependencies": [3],
            },
        ]
    
    def get_current_plan(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get the current plan.
        
        Returns:
            Optional[List[Dict[str, Any]]]: Current plan, or None if none.
        """
        return self._current_plan
    
    def get_current_goal(self) -> Optional[Dict[str, Any]]:
        """
        Get the current goal.
        
        Returns:
            Optional[Dict[str, Any]]: Current goal, or None if none.
        """
        return self._current_goal
    
    def get_plan_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of plans.
        
        Returns:
            List[Dict[str, Any]]: Plan history.
        """
        return self._plan_history.copy()
    
    def clear_current_plan(self) -> None:
        """Clear the current plan."""
        self._current_plan = None
        self._current_goal = None
    
    def update_plan_status(
        self,
        step_id: int,
        status: str
    ) -> bool:
        """
        Update the status of a plan step.
        
        Args:
            step_id: ID of the step to update.
            status: New status (e.g., "COMPLETED", "FAILED").
            
        Returns:
            bool: True if update succeeded, False otherwise.
        """
        if not self._current_plan:
            return False
        
        for step in self._current_plan:
            if step.get("id") == step_id:
                step["status"] = status
                return True
        
        return False
    
    def get_next_step(self) -> Optional[Dict[str, Any]]:
        """
        Get the next pending step in the current plan.
        
        Returns:
            Optional[Dict[str, Any]]: Next pending step, or None if all steps are completed.
        """
        if not self._current_plan:
            return None
        
        for step in self._current_plan:
            if step.get("status") == "PENDING":
                # Check if dependencies are completed
                dependencies = step.get("dependencies", [])
                if self._are_dependencies_completed(dependencies):
                    return step
        
        return None
    
    def _are_dependencies_completed(self, dependencies: List[int]) -> bool:
        """
        Check if all dependencies for a step are completed.
        
        Args:
            dependencies: List of step IDs that must be completed.
            
        Returns:
            bool: True if all dependencies are completed, False otherwise.
        """
        if not dependencies:
            return True
        
        if not self._current_plan:
            return False
        
        for dep_id in dependencies:
            found = False
            for step in self._current_plan:
                if step.get("id") == dep_id:
                    found = True
                    if step.get("status") != "COMPLETED":
                        return False
                    break
            
            if not found:
                return False
        
        return True
    
    def is_plan_complete(self) -> bool:
        """
        Check if the current plan is complete.
        
        Returns:
            bool: True if all steps are completed, False otherwise.
        """
        if not self._current_plan:
            return False
        
        for step in self._current_plan:
            if step.get("status") != "COMPLETED":
                return False
        
        return True
    
    def get_plan_progress(self) -> Dict[str, Any]:
        """
        Get the progress of the current plan.
        
        Returns:
            Dict[str, Any]: Progress information.
        """
        if not self._current_plan:
            return {"progress": 0, "total": 0, "completed": 0, "pending": 0}
        
        total = len(self._current_plan)
        completed = sum(1 for step in self._current_plan if step.get("status") == "COMPLETED")
        pending = total - completed
        
        return {
            "progress": (completed / total) * 100 if total > 0 else 0,
            "total": total,
            "completed": completed,
            "pending": pending,
        }
