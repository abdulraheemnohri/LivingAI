"""
Agent Planner
=============

Creates execution plans for agent goals.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for plans and tasks."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Task:
    """Represents a single task in a plan."""
    id: str
    title: str
    description: str
    status: str = "PENDING"
    priority: int = 5
    dependencies: List[str] = field(default_factory=list)
    tool: Optional[str] = None
    arguments: Dict[str, Any] = field(default_factory=dict)
    risk: RiskLevel = RiskLevel.LOW
    timeout: int = 300
    retry_limit: int = 3
    verification_required: bool = True
    result: Optional[Dict] = None


class TaskGraph:
    """Manages a graph of tasks with dependencies."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
    
    def add_task(self, task: Task):
        """Add a task to the graph."""
        self.tasks[task.id] = task
        self.dependency_graph[task.id] = task.dependencies
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                self.tasks[dep_id] = Task(
                    id=dep_id,
                    title=f"Dependency: {dep_id}",
                    description="Placeholder"
                )
                self.dependency_graph[dep_id] = []
    
    def topological_sort(self) -> List[str]:
        """Return tasks in topological order."""
        in_degree: Dict[str, int] = {tid: 0 for tid in self.tasks}
        for tid, deps in self.dependency_graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[tid] += 1
        
        queue = [tid for tid, degree in in_degree.items() if degree == 0]
        result: List[str] = []
        
        while queue:
            queue.sort(key=lambda tid: self.tasks[tid].priority, reverse=True)
            task_id = queue.pop(0)
            result.append(task_id)
            
            for dependent in self.get_dependents(task_id):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self.tasks):
            missing = set(self.tasks.keys()) - set(result)
            result.extend(missing)
        
        return result
    
    def get_dependents(self, task_id: str) -> List[str]:
        """Get tasks that depend on this task."""
        dependents = []
        for tid, deps in self.dependency_graph.items():
            if task_id in deps:
                dependents.append(tid)
        return dependents
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks with all dependencies satisfied."""
        ready = []
        for task in self.tasks.values():
            if task.status == "PENDING":
                deps_satisfied = all(
                    self.tasks[dep].status == "COMPLETED"
                    for dep in task.dependencies
                )
                if deps_satisfied or not task.dependencies:
                    ready.append(task)
        return ready


class AgentPlanner:
    """Creates execution plans for agent goals."""
    
    def __init__(self):
        self.task_counter = 0
    
    def create_plan(self, goal: str, config: Optional[Any] = None) -> Dict[str, Any]:
        """Create an execution plan for a goal."""
        self.task_counter = 0
        analysis = self._analyze_goal(goal)
        tasks = self._decompose_goal(goal, analysis)
        
        graph = TaskGraph()
        for task in tasks:
            graph.add_task(task)
        
        execution_order = graph.topological_sort()
        risk = self._calculate_risk(tasks)
        
        return {
            'goal': goal,
            'tasks': [task.__dict__ for task in tasks],
            'dependencies': graph.dependency_graph,
            'execution_order': execution_order,
            'constraints': analysis.get('constraints', []),
            'required_tools': analysis.get('required_tools', []),
            'risk': risk.value,
            'verification_required': True,
            'estimated_complexity': analysis.get('complexity', 'MEDIUM')
        }
    
    def _analyze_goal(self, goal: str) -> Dict[str, Any]:
        """Analyze a goal to extract information."""
        analysis = {
            'constraints': [],
            'required_tools': [],
            'complexity': 'MEDIUM'
        }
        
        goal_lower = goal.lower()
        
        if 'without' in goal_lower or 'except' in goal_lower:
            analysis['constraints'].append('Exclusion constraint')
        if 'only' in goal_lower:
            analysis['constraints'].append('Inclusion constraint')
        
        if 'file' in goal_lower or 'folder' in goal_lower:
            analysis['required_tools'].append('filesystem')
        if 'download' in goal_lower or 'fetch' in goal_lower:
            analysis['required_tools'].append('network')
        if 'calculate' in goal_lower or 'math' in goal_lower:
            analysis['required_tools'].append('calculator')
        if 'database' in goal_lower or 'sqlite' in goal_lower:
            analysis['required_tools'].append('sqlite')
        
        if len(goal.split()) > 20:
            analysis['complexity'] = 'HIGH'
        elif len(goal.split()) < 5:
            analysis['complexity'] = 'LOW'
        
        return analysis
    
    def _decompose_goal(self, goal: str, analysis: Dict[str, Any]) -> List[Task]:
        """Decompose a goal into executable tasks."""
        tasks = []
        goal_lower = goal.lower()
        
        if 'organize' in goal_lower and ('download' in goal_lower or 'folder' in goal_lower):
            tasks = [
                Task(id=self._next_id(), title="Inspect files", description="List files", tool="filesystem.list", arguments={"path": "~/storage/downloads"}, risk=RiskLevel.LOW),
                Task(id=self._next_id(), title="Identify categories", description="Identify file types", risk=RiskLevel.LOW),
                Task(id=self._next_id(), title="Propose organization", description="Create plan", risk=RiskLevel.LOW),
                Task(id=self._next_id(), title="Request confirmation", description="Ask user", risk=RiskLevel.MEDIUM),
                Task(id=self._next_id(), title="Move files", description="Move files", tool="filesystem.move", dependencies=[self._get_id(3)], risk=RiskLevel.MEDIUM),
                Task(id=self._next_id(), title="Verify results", description="Verify", tool="filesystem.list", dependencies=[self._get_id(4)], risk=RiskLevel.LOW),
                Task(id=self._next_id(), title="Report completion", description="Report", dependencies=[self._get_id(5)], risk=RiskLevel.LOW)
            ]
        elif 'backup' in goal_lower:
            tasks = [
                Task(id=self._next_id(), title="Check storage", description="Check space", tool="filesystem.stat", risk=RiskLevel.LOW),
                Task(id=self._next_id(), title="Create backup dir", description="Create directory", tool="filesystem.mkdir", risk=RiskLevel.LOW),
                Task(id=self._next_id(), title="Copy files", description="Copy files", tool="filesystem.copy", risk=RiskLevel.MEDIUM),
                Task(id=self._next_id(), title="Create archive", description="Create archive", tool="archive.create", risk=RiskLevel.MEDIUM),
                Task(id=self._next_id(), title="Verify backup", description="Verify", tool="archive.verify", risk=RiskLevel.LOW),
                Task(id=self._next_id(), title="Report completion", description="Report", risk=RiskLevel.LOW)
            ]
        elif 'analyze' in goal_lower and ('file' in goal_lower or 'report' in goal_lower):
            tasks = [
                Task(id=self._next_id(), title="Read file", description="Read file", tool="filesystem.read", risk=RiskLevel.LOW),
                Task(id=self._next_id(), title="Analyze content", description="Analyze", risk=RiskLevel.LOW),
                Task(id=self._next_id(), title="Generate summary", description="Summarize", risk=RiskLevel.LOW),
                Task(id=self._next_id(), title="Save summary", description="Save", tool="filesystem.write", risk=RiskLevel.LOW)
            ]
        else:
            task_count = max(3, len(goal.split()) // 5)
            for i in range(task_count):
                tasks.append(Task(id=self._next_id(), title=f"Step {i+1}", description=f"Execute step {i+1}", risk=RiskLevel.LOW))
        
        return tasks
    
    def _next_id(self) -> str:
        self.task_counter += 1
        return f"TASK-{self.task_counter:04d}"
    
    def _get_id(self, index: int) -> str:
        return f"TASK-{index:04d}"
    
    def _calculate_risk(self, tasks: List[Task]) -> RiskLevel:
        """Calculate overall risk level."""
        if not tasks:
            return RiskLevel.LOW
        risk_counts = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 0, RiskLevel.HIGH: 0, RiskLevel.CRITICAL: 0}
        for task in tasks:
            risk_counts[task.risk] += 1
        if risk_counts[RiskLevel.CRITICAL] > 0:
            return RiskLevel.CRITICAL
        if risk_counts[RiskLevel.HIGH] > 0:
            return RiskLevel.HIGH
        if risk_counts[RiskLevel.MEDIUM] > len(tasks) / 2 or risk_counts[RiskLevel.MEDIUM] > 2:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
    
    def validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an execution plan."""
        errors = []
        warnings = []
        if not plan.get('tasks'):
            errors.append("Plan has no tasks")
        task_ids = [t.get('id') for t in plan.get('tasks', [])]
        if len(task_ids) != len(set(task_ids)):
            errors.append("Duplicate task IDs")
        for task in plan.get('tasks', []):
            for dep in task.get('dependencies', []):
                if dep not in task_ids:
                    errors.append(f"Task {task.get('id')} depends on non-existent task {dep}")
        graph = TaskGraph()
        for task_data in plan.get('tasks', []):
            task = Task(**task_data)
            graph.add_task(task)
        try:
            sorted_tasks = graph.topological_sort()
            if len(sorted_tasks) != len(plan.get('tasks', [])):
                warnings.append("Circular dependency detected")
        except:
            errors.append("Dependency resolution failed")
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}
