# LivingAI Outcome Evaluator
# ============================
# This module evaluates the outcomes of actions and interactions.

import logging
import time
from typing import Dict, Any, Optional, List
from enum import Enum

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class OutcomeType(Enum):
    """Types of outcomes."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class OutcomeEvaluator:
    """
    Evaluates the outcomes of actions and interactions.
    
    Responsibilities:
    - Evaluate action outcomes
    - Assess effectiveness
    - Calculate impact
    - Determine confidence
    - Track evaluation history
    """
    
    def __init__(
        self,
        config: Optional[ConfigManager] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize the OutcomeEvaluator.
        
        Args:
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.config = config
        self.audit_logger = audit_logger
        
        # Evaluation state
        self._evaluation_history: List[Dict[str, Any]] = []
        self._current_evaluation: Optional[Dict[str, Any]] = None
        
        logging.info("OutcomeEvaluator initialized")
    
    def evaluate(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate the outcome of an interaction.
        
        Args:
            context: The context of the interaction.
            actions: Actions that were taken.
            observations: Observations from the actions.
            
        Returns:
            Dict[str, Any]: Evaluation results.
        """
        self.audit_logger.log("EVALUATION_START", "Starting outcome evaluation")
        start_time = time.time()
        
        try:
            evaluation = {
                "timestamp": time.time(),
                "context": context,
                "actions": actions,
                "observations": observations,
            }
            
            # Step 1: Determine outcome type
            outcome_type = self._determine_outcome_type(context, actions, observations)
            evaluation["outcome"] = outcome_type.value
            
            # Step 2: Calculate effectiveness
            effectiveness = self._calculate_effectiveness(context, actions, observations)
            evaluation["effectiveness"] = effectiveness
            
            # Step 3: Calculate impact
            impact = self._calculate_impact(context, actions, observations)
            evaluation["impact"] = impact
            
            # Step 4: Determine confidence
            confidence = self._calculate_confidence(context, actions, observations)
            evaluation["confidence"] = confidence
            
            # Step 5: Extract insights
            insights = self._extract_insights(context, actions, observations, evaluation)
            evaluation["insights"] = insights
            
            # Step 6: Generate recommendations
            recommendations = self._generate_recommendations(context, actions, observations, evaluation)
            evaluation["recommendations"] = recommendations
            
            evaluation["duration"] = time.time() - start_time
            
            # Store in history
            self._evaluation_history.append(evaluation)
            self._current_evaluation = evaluation
            
            self.audit_logger.log(
                "EVALUATION_SUCCESS",
                f"Evaluated in {evaluation['duration']:.2f}s: {outcome_type.value}"
            )
            
            return evaluation
        
        except Exception as e:
            self.audit_logger.log("EVALUATION_FAIL", str(e))
            logging.error(f"Evaluation failed: {e}")
            return {
                "error": str(e),
                "outcome": OutcomeType.UNKNOWN.value,
                "effectiveness": 0.0,
                "impact": 0.0,
                "confidence": 0.0,
            }
    
    def _determine_outcome_type(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any]
    ) -> OutcomeType:
        """
        Determine the type of outcome.
        
        Args:
            context: The context of the interaction.
            actions: Actions that were taken.
            observations: Observations from the actions.
            
        Returns:
            OutcomeType: The outcome type.
        """
        # Check if all actions were successful
        if actions:
            successful = sum(1 for a in actions if a.get("status") == "success")
            failed = sum(1 for a in actions if a.get("status") == "failed")
            
            if failed > 0 and successful == 0:
                return OutcomeType.FAILURE
            elif failed > 0:
                return OutcomeType.PARTIAL
            elif successful > 0:
                return OutcomeType.SUCCESS
        
        # Check observations for clues
        if observations.get("error"):
            return OutcomeType.FAILURE
        
        # Default to neutral
        return OutcomeType.NEUTRAL
    
    def _calculate_effectiveness(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any]
    ) -> float:
        """
        Calculate the effectiveness of the interaction.
        
        Args:
            context: The context of the interaction.
            actions: Actions that were taken.
            observations: Observations from the actions.
            
        Returns:
            float: Effectiveness score (0.0 to 1.0).
        """
        if not actions:
            return 0.5
        
        # Calculate success rate
        successful = sum(1 for a in actions if a.get("status") == "success")
        total = len(actions)
        success_rate = successful / total
        
        # Calculate based on success rate
        if success_rate == 1.0:
            return 1.0
        elif success_rate >= 0.7:
            return 0.8
        elif success_rate >= 0.4:
            return 0.5
        else:
            return 0.2
    
    def _calculate_impact(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any]
    ) -> float:
        """
        Calculate the impact of the interaction.
        
        Args:
            context: The context of the interaction.
            actions: Actions that were taken.
            observations: Observations from the actions.
            
        Returns:
            float: Impact score (0.0 to 1.0).
        """
        # Simple heuristic based on action count and success
        if not actions:
            return 0.1
        
        # Count important actions
        important_actions = sum(
            1 for a in actions
            if a.get("importance", "medium") in ["high", "critical"]
        )
        
        # Calculate impact based on important actions
        if important_actions >= 3:
            return 1.0
        elif important_actions >= 1:
            return 0.7
        else:
            return 0.3
    
    def _calculate_confidence(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any]
    ) -> float:
        """
        Calculate the confidence in the evaluation.
        
        Args:
            context: The context of the interaction.
            actions: Actions that were taken.
            observations: Observations from the actions.
            
        Returns:
            float: Confidence score (0.0 to 1.0).
        """
        # Simple heuristic
        if actions:
            # More actions = more confidence in evaluation
            num_actions = len(actions)
            if num_actions >= 5:
                return 0.9
            elif num_actions >= 3:
                return 0.7
            elif num_actions >= 1:
                return 0.5
        
        return 0.3
    
    def _extract_insights(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract insights from the evaluation.
        
        Args:
            context: The context of the interaction.
            actions: Actions that were taken.
            observations: Observations from the actions.
            evaluation: The evaluation results.
            
        Returns:
            List[Dict[str, Any]]: List of insights.
        """
        insights = []
        
        # Insight: Action success rate
        if actions:
            successful = sum(1 for a in actions if a.get("status") == "success")
            total = len(actions)
            success_rate = successful / total
            
            insights.append({
                "type": "action_success",
                "description": f"Action success rate: {success_rate:.1%}",
                "value": success_rate,
                "confidence": 0.9,
            })
        
        # Insight: Outcome type
        outcome = evaluation.get("outcome", "unknown")
        insights.append({
            "type": "outcome",
            "description": f"Outcome: {outcome}",
            "value": outcome,
            "confidence": 0.8,
        })
        
        # Insight: Effectiveness
        effectiveness = evaluation.get("effectiveness", 0)
        insights.append({
            "type": "effectiveness",
            "description": f"Effectiveness: {effectiveness:.1%}",
            "value": effectiveness,
            "confidence": 0.7,
        })
        
        return insights
    
    def _generate_recommendations(
        self,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        observations: Dict[str, Any],
        evaluation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on the evaluation.
        
        Args:
            context: The context of the interaction.
            actions: Actions that were taken.
            observations: Observations from the actions.
            evaluation: The evaluation results.
            
        Returns:
            List[Dict[str, Any]]: List of recommendations.
        """
        recommendations = []
        
        outcome = evaluation.get("outcome")
        effectiveness = evaluation.get("effectiveness", 0)
        
        # Recommendation: Repeat successful actions
        if outcome == OutcomeType.SUCCESS.value and effectiveness > 0.8:
            recommendations.append({
                "type": "repeat_success",
                "description": "Repeat successful actions in similar situations",
                "priority": "high",
                "confidence": 0.9,
            })
        
        # Recommendation: Avoid failed actions
        if outcome == OutcomeType.FAILURE.value:
            recommendations.append({
                "type": "avoid_failure",
                "description": "Avoid repeating failed actions",
                "priority": "critical",
                "confidence": 0.9,
            })
        
        # Recommendation: Improve partial successes
        if outcome == OutcomeType.PARTIAL.value:
            recommendations.append({
                "type": "improve_partial",
                "description": "Analyze and improve partially successful actions",
                "priority": "medium",
                "confidence": 0.7,
            })
        
        return recommendations
    
    def get_evaluation_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of evaluations.
        
        Returns:
            List[Dict[str, Any]]: Evaluation history.
        """
        return self._evaluation_history.copy()
    
    def get_current_evaluation(self) -> Optional[Dict[str, Any]]:
        """
        Get the current evaluation.
        
        Returns:
            Optional[Dict[str, Any]]: Current evaluation, or None.
        """
        return self._current_evaluation
    
    def clear_history(self) -> None:
        """Clear the evaluation history."""
        self._evaluation_history = []
        self._current_evaluation = None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about evaluations.
        
        Returns:
            Dict[str, Any]: Evaluation statistics.
        """
        if not self._evaluation_history:
            return {
                "total_evaluations": 0,
                "by_outcome": {},
                "avg_effectiveness": 0.0,
                "avg_impact": 0.0,
                "avg_confidence": 0.0,
            }
        
        by_outcome = {}
        total_effectiveness = 0.0
        total_impact = 0.0
        total_confidence = 0.0
        
        for eval in self._evaluation_history:
            # By outcome
            outcome = eval.get("outcome", "unknown")
            by_outcome[outcome] = by_outcome.get(outcome, 0) + 1
            
            # Totals
            total_effectiveness += eval.get("effectiveness", 0)
            total_impact += eval.get("impact", 0)
            total_confidence += eval.get("confidence", 0)
        
        count = len(self._evaluation_history)
        
        return {
            "total_evaluations": count,
            "by_outcome": by_outcome,
            "avg_effectiveness": total_effectiveness / count,
            "avg_impact": total_impact / count,
            "avg_confidence": total_confidence / count,
        }
    
    def get_outcome_types(self) -> List[str]:
        """
        Get all outcome types.
        
        Returns:
            List[str]: List of outcome type values.
        """
        return [ot.value for ot in OutcomeType]
