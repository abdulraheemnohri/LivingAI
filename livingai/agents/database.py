"""
Agent Database
=============

SQLite database for storing agent data.
"""

import sqlite3
import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import asdict


class AgentDatabase:
    """
    SQLite database for agent-related data.
    
    Tables:
    - agents: Agent configurations
    - agent_runs: Agent execution runs
    - agent_tasks: Tasks within runs
    - agent_plans: Execution plans
    - agent_tool_calls: Tool execution history
    - agent_observations: Agent observations
    - agent_results: Agent results
    - agent_failures: Agent failures
    - agent_permissions: Agent permissions
    - agent_events: Agent events
    - agent_checkpoints: Agent checkpoints
    - agent_metrics: Agent metrics
    - agent_lessons: Lessons learned from runs
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the agent database."""
        self.db_path = db_path or os.path.expanduser('~/.livingai/data/agents.db')
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    goal TEXT,
                    mode TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    budget_json TEXT,
                    require_confirmation INTEGER DEFAULT 1,
                    verify_actions INTEGER DEFAULT 1,
                    learn_from_runs INTEGER DEFAULT 1,
                    permission_profile TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_runs (
                    run_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    state TEXT NOT NULL,
                    plan_json TEXT,
                    completed_tasks INTEGER DEFAULT 0,
                    total_tasks INTEGER DEFAULT 0,
                    steps_taken INTEGER DEFAULT 0,
                    retries_used INTEGER DEFAULT 0,
                    tool_calls INTEGER DEFAULT 0,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    result_json TEXT,
                    error TEXT,
                    checkpoint_json TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_tasks (
                    task_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    dependencies_json TEXT,
                    tool TEXT,
                    arguments_json TEXT,
                    risk TEXT DEFAULT 'LOW',
                    timeout INTEGER DEFAULT 300,
                    retry_limit INTEGER DEFAULT 3,
                    verification_required INTEGER DEFAULT 1,
                    result_json TEXT,
                    start_time REAL,
                    end_time REAL,
                    FOREIGN KEY (run_id) REFERENCES agent_runs(run_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_plans (
                    plan_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES agent_runs(run_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_tool_calls (
                    call_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    task_id TEXT,
                    tool TEXT NOT NULL,
                    arguments_json TEXT,
                    result_json TEXT,
                    success INTEGER,
                    error TEXT,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES agent_runs(run_id),
                    FOREIGN KEY (task_id) REFERENCES agent_tasks(task_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_observations (
                    observation_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    task_id TEXT,
                    source TEXT NOT NULL,
                    data_json TEXT,
                    confidence REAL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES agent_runs(run_id),
                    FOREIGN KEY (task_id) REFERENCES agent_tasks(task_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_results (
                    result_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    task_id TEXT,
                    result_type TEXT NOT NULL,
                    data_json TEXT,
                    verified INTEGER DEFAULT 0,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES agent_runs(run_id),
                    FOREIGN KEY (task_id) REFERENCES agent_tasks(task_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_failures (
                    failure_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    task_id TEXT,
                    failure_type TEXT NOT NULL,
                    error TEXT,
                    stack_trace TEXT,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES agent_runs(run_id),
                    FOREIGN KEY (task_id) REFERENCES agent_tasks(task_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    agent_id TEXT,
                    state TEXT NOT NULL,
                    plan_json TEXT,
                    completed_tasks INTEGER,
                    total_tasks INTEGER,
                    context_json TEXT,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES agent_runs(run_id),
                    FOREIGN KEY (agent_id) REFERENCES agents(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_lessons (
                    lesson_id TEXT PRIMARY KEY,
                    run_id TEXT,
                    lesson_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    recommendation TEXT,
                    validated INTEGER DEFAULT 0,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES agent_runs(run_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    metric_id TEXT PRIMARY KEY,
                    run_id TEXT,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES agent_runs(run_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_logs (
                    log_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data_json TEXT,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES agent_runs(run_id)
                )
            ''')
            
            conn.commit()
    
    def create_agent(self, config: Any) -> str:
        """Create a new agent configuration."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agents (id, name, description, goal, mode, priority, 
                                   budget_json, require_confirmation, verify_actions, 
                                   learn_from_runs, permission_profile, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                config.id,
                config.name,
                config.description,
                config.goal,
                config.mode.value,
                config.priority.value,
                json.dumps(asdict(config.budget)),
                int(config.require_confirmation),
                int(config.verify_actions),
                int(config.learn_from_runs),
                config.permission_profile,
                config.created_at,
                config.updated_at
            ))
            conn.commit()
        return config.id
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get an agent configuration."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agents WHERE id = ?', (agent_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_agent_dict(row)
        return None
    
    def get_all_agents(self) -> List[Dict]:
        """Get all agent configurations."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agents')
            return [self._row_to_agent_dict(row) for row in cursor.fetchall()]
    
    def _row_to_agent_dict(self, row: sqlite3.Row) -> Dict:
        """Convert database row to agent dict."""
        return {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'goal': row[3],
            'mode': row[4],
            'priority': row[5],
            'budget': json.loads(row[6]) if row[6] else {},
            'require_confirmation': bool(row[7]),
            'verify_actions': bool(row[8]),
            'learn_from_runs': bool(row[9]),
            'permission_profile': row[10],
            'created_at': row[11],
            'updated_at': row[12]
        }
    
    def update_agent(self, config: Any):
        """Update an agent configuration."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE agents SET name = ?, description = ?, goal = ?, mode = ?, 
                                   priority = ?, budget_json = ?, require_confirmation = ?, 
                                   verify_actions = ?, learn_from_runs = ?, permission_profile = ?, 
                                   updated_at = ?
                WHERE id = ?
            ''', (
                config.name,
                config.description,
                config.goal,
                config.mode.value,
                config.priority.value,
                json.dumps(asdict(config.budget)),
                int(config.require_confirmation),
                int(config.verify_actions),
                int(config.learn_from_runs),
                config.permission_profile,
                __import__('time').time(),
                config.id
            ))
            conn.commit()
    
    def delete_agent(self, agent_id: str):
        """Delete an agent configuration."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM agents WHERE id = ?', (agent_id,))
            conn.commit()
    
    def create_agent_run(self, run: Any) -> str:
        """Create a new agent run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_runs (run_id, agent_id, goal, state, plan_json, 
                                       completed_tasks, total_tasks, steps_taken, retries_used, 
                                       tool_calls, start_time, end_time, result_json, error, checkpoint_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                run.run_id,
                run.agent_id,
                run.goal,
                run.state.value,
                json.dumps(run.plan) if run.plan else None,
                run.completed_tasks,
                run.total_tasks,
                run.steps_taken,
                run.retries_used,
                run.tool_calls,
                run.start_time,
                run.end_time,
                json.dumps(run.result) if run.result else None,
                run.error,
                json.dumps(run.checkpoint) if run.checkpoint else None
            ))
            conn.commit()
        return run.run_id
    
    def get_agent_run(self, run_id: str) -> Optional[Dict]:
        """Get an agent run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agent_runs WHERE run_id = ?', (run_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_run_dict(row)
        return None
    
    def _row_to_run_dict(self, row: sqlite3.Row) -> Dict:
        """Convert database row to run dict."""
        return {
            'run_id': row[0],
            'agent_id': row[1],
            'goal': row[2],
            'state': row[3],
            'plan': json.loads(row[4]) if row[4] else None,
            'completed_tasks': row[5],
            'total_tasks': row[6],
            'steps_taken': row[7],
            'retries_used': row[8],
            'tool_calls': row[9],
            'start_time': row[10],
            'end_time': row[11],
            'result': json.loads(row[12]) if row[12] else None,
            'error': row[13],
            'checkpoint': json.loads(row[14]) if row[14] else None
        }
    
    def update_agent_run(self, run: Any):
        """Update an agent run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE agent_runs SET state = ?, plan_json = ?, completed_tasks = ?,
                                   total_tasks = ?, steps_taken = ?, retries_used = ?,
                                   tool_calls = ?, end_time = ?, result_json = ?, error = ?, 
                                   checkpoint_json = ?
                WHERE run_id = ?
            ''', (
                run.state.value,
                json.dumps(run.plan) if run.plan else None,
                run.completed_tasks,
                run.total_tasks,
                run.steps_taken,
                run.retries_used,
                run.tool_calls,
                run.end_time,
                json.dumps(run.result) if run.result else None,
                run.error,
                json.dumps(run.checkpoint) if run.checkpoint else None,
                run.run_id
            ))
            conn.commit()
    
    def get_all_agent_runs(self, agent_id: Optional[str] = None) -> List[Dict]:
        """Get all agent runs, optionally filtered by agent ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if agent_id:
                cursor.execute('SELECT * FROM agent_runs WHERE agent_id = ?', (agent_id,))
            else:
                cursor.execute('SELECT * FROM agent_runs')
            return [self._row_to_run_dict(row) for row in cursor.fetchall()]
    
    def save_checkpoint(self, checkpoint: Dict):
        """Save an agent checkpoint."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_checkpoints (checkpoint_id, run_id, agent_id, state, 
                                              plan_json, completed_tasks, total_tasks, 
                                              context_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                checkpoint.get('checkpoint_id', f"CP-{__import__('uuid').uuid4().hex[:8].upper()}"),
                checkpoint.get('run_id'),
                checkpoint.get('agent_id'),
                checkpoint.get('state'),
                json.dumps(checkpoint.get('plan')),
                checkpoint.get('completed_tasks'),
                checkpoint.get('total_tasks'),
                json.dumps(checkpoint.get('context')),
                __import__('time').time()
            ))
            conn.commit()
    
    def get_checkpoint(self, run_id: str) -> Optional[Dict]:
        """Get the latest checkpoint for a run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM agent_checkpoints WHERE run_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            ''', (run_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'checkpoint_id': row[0],
                    'run_id': row[1],
                    'agent_id': row[2],
                    'state': row[3],
                    'plan': json.loads(row[4]) if row[4] else None,
                    'completed_tasks': row[5],
                    'total_tasks': row[6],
                    'context': json.loads(row[7]) if row[7] else None,
                    'timestamp': row[8]
                }
        return None
    
    def save_lesson(self, lesson: Dict):
        """Save a lesson learned from an agent run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_lessons (lesson_id, run_id, lesson_type, description, 
                                         recommendation, validated, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                lesson.get('lesson_id', f"LESSON-{__import__('uuid').uuid4().hex[:8].upper()}"),
                lesson.get('run_id'),
                lesson.get('type', 'unknown'),
                lesson.get('description', ''),
                lesson.get('recommendation', ''),
                int(lesson.get('validated', False)),
                __import__('time').time()
            ))
            conn.commit()
    
    def get_lessons(self, run_id: Optional[str] = None) -> List[Dict]:
        """Get lessons, optionally filtered by run ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if run_id:
                cursor.execute('SELECT * FROM agent_lessons WHERE run_id = ?', (run_id,))
            else:
                cursor.execute('SELECT * FROM agent_lessons')
            return [
                {
                    'lesson_id': row[0],
                    'run_id': row[1],
                    'lesson_type': row[2],
                    'description': row[3],
                    'recommendation': row[4],
                    'validated': bool(row[5]),
                    'timestamp': row[6]
                }
                for row in cursor.fetchall()
            ]
    
    def save_log(self, run_id: str, level: str, message: str, data: Optional[Dict] = None):
        """Save a log entry for an agent run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_logs (log_id, run_id, level, message, data_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                f"LOG-{__import__('uuid').uuid4().hex[:8].upper()}",
                run_id,
                level,
                message,
                json.dumps(data) if data else None,
                __import__('time').time()
            ))
            conn.commit()
    
    def get_agent_logs(self, run_id: str) -> List[Dict]:
        """Get logs for an agent run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agent_logs WHERE run_id = ? ORDER BY timestamp', (run_id,))
            return [
                {
                    'log_id': row[0],
                    'run_id': row[1],
                    'level': row[2],
                    'message': row[3],
                    'data': json.loads(row[4]) if row[4] else None,
                    'timestamp': row[5]
                }
                for row in cursor.fetchall()
            ]
    
    def save_tool_call(self, run_id: str, task_id: Optional[str], tool: str, 
                      arguments: Dict, result: Dict) -> str:
        """Save a tool call record."""
        call_id = f"TC-{__import__('uuid').uuid4().hex[:8].upper()}"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_tool_calls (call_id, run_id, task_id, tool, 
                                              arguments_json, result_json, success, error, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                call_id,
                run_id,
                task_id,
                tool,
                json.dumps(arguments),
                json.dumps(result),
                int(result.get('success', False)),
                result.get('error'),
                __import__('time').time()
            ))
            conn.commit()
        return call_id
    
    def get_tool_calls(self, run_id: Optional[str] = None) -> List[Dict]:
        """Get tool calls, optionally filtered by run ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if run_id:
                cursor.execute('SELECT * FROM agent_tool_calls WHERE run_id = ?', (run_id,))
            else:
                cursor.execute('SELECT * FROM agent_tool_calls')
            return [
                {
                    'call_id': row[0],
                    'run_id': row[1],
                    'task_id': row[2],
                    'tool': row[3],
                    'arguments': json.loads(row[4]) if row[4] else {},
                    'result': json.loads(row[5]) if row[5] else {},
                    'success': bool(row[6]),
                    'error': row[7],
                    'timestamp': row[8]
                }
                for row in cursor.fetchall()
            ]
    
    def save_metric(self, run_id: Optional[str], metric_name: str, value: float):
        """Save a metric."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_metrics (metric_id, run_id, metric_name, value, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                f"METRIC-{__import__('uuid').uuid4().hex[:8].upper()}",
                run_id,
                metric_name,
                value,
                __import__('time').time()
            ))
            conn.commit()
    
    def get_metrics(self, run_id: Optional[str] = None) -> List[Dict]:
        """Get metrics, optionally filtered by run ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if run_id:
                cursor.execute('SELECT * FROM agent_metrics WHERE run_id = ?', (run_id,))
            else:
                cursor.execute('SELECT * FROM agent_metrics')
            return [
                {
                    'metric_id': row[0],
                    'run_id': row[1],
                    'metric_name': row[2],
                    'value': row[3],
                    'timestamp': row[4]
                }
                for row in cursor.fetchall()
            ]
    
    def cleanup_old_data(self, max_age_days: int = 30):
        """Clean up old data."""
        import time
        cutoff = time.time() - (max_age_days * 24 * 60 * 60)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete old runs
            cursor.execute('DELETE FROM agent_runs WHERE start_time < ?', (cutoff,))
            
            # Delete old logs, tool calls, etc.
            cursor.execute('DELETE FROM agent_logs WHERE timestamp < ?', (cutoff,))
            cursor.execute('DELETE FROM agent_tool_calls WHERE timestamp < ?', (cutoff,))
            cursor.execute('DELETE FROM agent_checkpoints WHERE timestamp < ?', (cutoff,))
            cursor.execute('DELETE FROM agent_metrics WHERE timestamp < ?', (cutoff,))
            
            conn.commit()
