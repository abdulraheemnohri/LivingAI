"""
Agent CLI Handlers
==================

Command handlers for agent-related CLI commands.
"""

import sys
from typing import Optional


def handle_agent_command(app, args):
    """Handle agent-related commands."""
    agent_manager = app.agent_manager
    
    if not hasattr(args, 'agent_command') or args.agent_command is None:
        # Default: list agents
        handle_agent_list(agent_manager)
        return
    
    command = args.agent_command
    
    if command == 'list':
        handle_agent_list(agent_manager)
    elif command == 'create':
        handle_agent_create(agent_manager, args)
    elif command == 'start':
        handle_agent_start(agent_manager, args)
    elif command == 'pause':
        handle_agent_pause(agent_manager, args)
    elif command == 'resume':
        handle_agent_resume(agent_manager, args)
    elif command == 'stop':
        handle_agent_stop(agent_manager, args)
    elif command == 'status':
        handle_agent_status(agent_manager, args)
    elif command == 'inspect':
        handle_agent_inspect(agent_manager, args)
    elif command == 'logs':
        handle_agent_logs(agent_manager, args)
    elif command == 'delete':
        handle_agent_delete(agent_manager, args)
    elif command == 'schedule':
        handle_agent_schedule(agent_manager, args)
    elif command == 'schedules':
        handle_agent_schedules(agent_manager, args)
    elif command == 'cancel':
        handle_agent_cancel(agent_manager, args)
    else:
        print(f"Error: Unknown agent command '{command}'")
        print("Use 'livingai agent --help' for available commands.")
        sys.exit(1)


def handle_agent_list(agent_manager):
    """List all agents."""
    agents = agent_manager.list_agents()
    
    if not agents:
        print("No agents found.")
        print("Create an agent with: livingai agent create <goal>")
        return
    
    print("\nAGENTS")
    print("=" * 60)
    for agent in agents:
        print(f"ID: {agent.id}")
        print(f"  Name: {agent.name}")
        print(f"  Goal: {agent.goal}")
        print(f"  Mode: {agent.mode.value}")
        print(f"  Priority: {agent.priority.value}")
        print(f"  Profile: {agent.permission_profile}")
        print(f"  Created: {__import__('datetime').datetime.fromtimestamp(agent.created_at).isoformat()}")
        print()
    
    print(f"Total: {len(agents)} agents")


def handle_agent_create(agent_manager, args):
    """Create a new agent."""
    from .manager import AgentMode, AgentPriority
    
    # Get goal from arguments
    if args.goal:
        goal = ' '.join(args.goal)
    else:
        print("Error: No goal provided.")
        print("Usage: livingai agent create <goal>")
        sys.exit(1)
    
    # Parse options
    name = getattr(args, 'name', None)
    description = getattr(args, 'description', None)
    mode_str = getattr(args, 'mode', None)
    priority_str = getattr(args, 'priority', None)
    profile = getattr(args, 'profile', 'SAFE')
    
    # Convert mode string to enum
    mode = AgentMode.ASSIST
    if mode_str:
        try:
            mode = AgentMode[mode_str.upper()]
        except KeyError:
            print(f"Error: Invalid mode '{mode_str}'. Valid modes: ASK, ASSIST, PLAN, EXECUTE, AUTONOMOUS, BACKGROUND")
            sys.exit(1)
    
    # Convert priority string to enum
    priority = AgentPriority.NORMAL
    if priority_str:
        try:
            priority = AgentPriority[priority_str.upper()]
        except KeyError:
            print(f"Error: Invalid priority '{priority_str}'. Valid priorities: CRITICAL, HIGH, NORMAL, LOW, BACKGROUND")
            sys.exit(1)
    
    # Create agent
    config = agent_manager.create_agent(
        goal=goal,
        name=name,
        description=description,
        mode=mode,
        priority=priority,
        permission_profile=profile
    )
    
    print(f"✅ Agent created: {config.id}")
    print(f"   Name: {config.name}")
    print(f"   Goal: {config.goal}")
    print(f"   Mode: {config.mode.value}")
    print(f"   Priority: {config.priority.value}")


def handle_agent_start(agent_manager, args):
    """Start an agent."""
    from .manager import AgentMode
    
    # Get goal or agent_id
    if args.goal:
        goal = ' '.join(args.goal)
        agent_id = None
    elif args.agent_id:
        agent_id = args.agent_id
        goal = None
    else:
        print("Error: No goal or agent ID provided.")
        print("Usage: livingai agent start <goal>")
        print("       livingai agent start --id <agent_id> [--goal <goal>]")
        sys.exit(1)
    
    # Parse mode
    mode_str = getattr(args, 'mode', None)
    mode = None
    if mode_str:
        try:
            mode = AgentMode[mode_str.upper()]
        except KeyError:
            print(f"Error: Invalid mode '{mode_str}'")
            sys.exit(1)
    
    # Start agent
    run = agent_manager.start_agent(agent_id or '', goal=goal, mode=mode)
    
    print(f"✅ Agent started: {run.run_id}")
    print(f"   Agent ID: {run.agent_id}")
    print(f"   Goal: {run.goal}")
    print(f"   State: {run.state.value}")
    print(f"   Tasks: {run.total_tasks}")
    print(f"   Run ID: {run.run_id}")


def handle_agent_pause(agent_manager, args):
    """Pause an agent run."""
    if not args.run_id:
        print("Error: No run ID provided.")
        print("Usage: livingai agent pause <run_id>")
        sys.exit(1)
    
    agent_manager.pause_agent(args.run_id)
    print(f"✅ Agent run {args.run_id} paused")


def handle_agent_resume(agent_manager, args):
    """Resume a paused agent run."""
    if not args.run_id:
        print("Error: No run ID provided.")
        print("Usage: livingai agent resume <run_id>")
        sys.exit(1)
    
    success = agent_manager.resume_agent(args.run_id)
    if success:
        print(f"✅ Agent run {args.run_id} resumed")
    else:
        print(f"❌ Failed to resume agent run {args.run_id}")
        sys.exit(1)


def handle_agent_stop(agent_manager, args):
    """Stop an agent run."""
    if not args.run_id:
        print("Error: No run ID provided.")
        print("Usage: livingai agent stop <run_id>")
        sys.exit(1)
    
    agent_manager.stop_agent(args.run_id)
    print(f"✅ Agent run {args.run_id} stopped")


def handle_agent_status(agent_manager, args):
    """Show agent status."""
    runs = agent_manager.list_runs()
    
    if not runs:
        print("No active agent runs.")
        return
    
    print("\nACTIVE AGENT RUNS")
    print("=" * 60)
    
    for run in runs:
        status = agent_manager.get_status(run.run_id)
        if status:
            print(f"Run ID: {status['run_id']}")
            print(f"  Agent: {status['agent_id']}")
            print(f"  Goal: {status['goal']}")
            print(f"  State: {status['state']}")
            print(f"  Progress: {status['progress']}")
            print(f"  Steps: {status['steps']}")
            print(f"  Tools: {status['tools']}")
            print(f"  Retries: {status['retries']}")
            print(f"  Runtime: {status['runtime']}")
            print(f"  Risk: {status['risk']}")
            print()


def handle_agent_inspect(agent_manager, args):
    """Inspect an agent run."""
    if not args.run_id:
        print("Error: No run ID provided.")
        print("Usage: livingai agent inspect <run_id>")
        sys.exit(1)
    
    run = agent_manager.inspect_agent(args.run_id)
    
    if not run:
        print(f"❌ Agent run {args.run_id} not found")
        sys.exit(1)
    
    print(f"\nAGENT RUN: {run.run_id}")
    print("=" * 60)
    print(f"Agent ID: {run.agent_id}")
    print(f"Goal: {run.goal}")
    print(f"State: {run.state.value}")
    print(f"Progress: {run.completed_tasks}/{run.total_tasks} tasks")
    print(f"Steps: {run.steps_taken}/{run.budget.max_steps}")
    print(f"Tools: {run.tool_calls}/{run.budget.max_tool_calls}")
    print(f"Retries: {run.retries_used}/{run.budget.max_retries}")
    
    if run.plan:
        print(f"\nPLAN")
        print("-" * 60)
        for task in run.plan.get('tasks', []):
            status_symbol = "✓" if task.get('status') == 'COMPLETED' else "→" if task.get('status') == 'RUNNING' else "○"
            print(f"{status_symbol} {task.get('title', task.get('id', 'Unknown'))}")
    
    if run.result:
        print(f"\nRESULT")
        print("-" * 60)
        print(f"Verification: {run.result.get('verification', {}).get('overall_status', 'N/A')}")
        print(f"Completed: {run.result.get('completed_tasks', 0)}/{run.result.get('total_tasks', 0)}")
    
    if run.error:
        print(f"\nERROR")
        print("-" * 60)
        print(run.error)


def handle_agent_logs(agent_manager, args):
    """Show agent logs."""
    if not args.run_id:
        print("Error: No run ID provided.")
        print("Usage: livingai agent logs <run_id>")
        sys.exit(1)
    
    logs = agent_manager.get_logs(args.run_id)
    
    if not logs:
        print(f"No logs found for run {args.run_id}")
        return
    
    print(f"\nLOGS FOR RUN: {args.run_id}")
    print("=" * 60)
    
    for log in logs:
        timestamp = __import__('datetime').datetime.fromtimestamp(log['timestamp']).isoformat()
        print(f"[{timestamp}] [{log['level']}] {log['message']}")
        if log.get('data'):
            print(f"  Data: {log['data']}")


def handle_agent_delete(agent_manager, args):
    """Delete an agent."""
    if not args.agent_id:
        print("Error: No agent ID provided.")
        print("Usage: livingai agent delete <agent_id>")
        sys.exit(1)
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete agent {args.agent_id}? (y/N): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return
    
    agent_manager.delete_agent(args.agent_id)
    print(f"✅ Agent {args.agent_id} deleted")


def handle_agent_schedule(agent_manager, args):
    """Schedule an agent."""
    print("Agent scheduling is not yet implemented.")
    print("This feature will be available in a future update.")


def handle_agent_schedules(agent_manager, args):
    """List scheduled agents."""
    print("Agent scheduling is not yet implemented.")


def handle_agent_cancel(agent_manager, args):
    """Cancel a scheduled agent."""
    print("Agent scheduling is not yet implemented.")
