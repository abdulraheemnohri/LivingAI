"""
CLI Agent Extension
==================

Extension to the LivingAI CLI that adds agent commands.
This module provides the agent subparser and its handlers.
"""

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import LivingAIApp


def add_agent_parser(subparsers):
    """
    Add the agent command parser to the main CLI.
    
    Args:
        subparsers: The subparsers object from the main parser
    """
    # Agent command
    agent_parser = subparsers.add_parser(
        "agent",
        help="Manage autonomous agents"
    )
    agent_subparsers = agent_parser.add_subparsers(
        dest="agent_command",
        title="Agent Commands",
        description="Use 'livingai agent <command> --help' for more details."
    )
    
    # agent list
    agent_subparsers.add_parser(
        "list",
        help="List all agents"
    )
    
    # agent create
    agent_create_parser = agent_subparsers.add_parser(
        "create",
        help="Create a new agent"
    )
    agent_create_parser.add_argument(
        "goal",
        nargs="+",
        help="The goal/objective for the agent"
    )
    agent_create_parser.add_argument(
        "--name", "-n",
        type=str,
        default=None,
        help="Name for the agent"
    )
    agent_create_parser.add_argument(
        "--description", "-d",
        type=str,
        default=None,
        help="Description of the agent"
    )
    agent_create_parser.add_argument(
        "--mode", "-m",
        type=str,
        default=None,
        choices=["ASK", "ASSIST", "PLAN", "EXECUTE", "AUTONOMOUS", "BACKGROUND"],
        help="Agent operation mode"
    )
    agent_create_parser.add_argument(
        "--priority", "-p",
        type=str,
        default=None,
        choices=["CRITICAL", "HIGH", "NORMAL", "LOW", "BACKGROUND"],
        help="Agent priority"
    )
    agent_create_parser.add_argument(
        "--profile",
        type=str,
        default="SAFE",
        help="Permission profile (READ_ONLY, SAFE, PRODUCTIVITY, FILE_MANAGER, DEVELOPER, AUTONOMOUS)"
    )
    
    # agent start
    agent_start_parser = agent_subparsers.add_parser(
        "start",
        help="Start an agent run"
    )
    agent_start_parser.add_argument(
        "goal",
        nargs="*",
        help="The goal for the agent run (creates new agent if no --id specified)"
    )
    agent_start_parser.add_argument(
        "--id",
        type=str,
        default=None,
        dest="agent_id",
        help="ID of existing agent to start"
    )
    agent_start_parser.add_argument(
        "--mode", "-m",
        type=str,
        default=None,
        choices=["ASK", "ASSIST", "PLAN", "EXECUTE", "AUTONOMOUS", "BACKGROUND"],
        help="Override agent mode"
    )
    
    # agent pause
    agent_pause_parser = agent_subparsers.add_parser(
        "pause",
        help="Pause an agent run"
    )
    agent_pause_parser.add_argument(
        "run_id",
        type=str,
        help="ID of the run to pause"
    )
    
    # agent resume
    agent_resume_parser = agent_subparsers.add_parser(
        "resume",
        help="Resume a paused agent run"
    )
    agent_resume_parser.add_argument(
        "run_id",
        type=str,
        help="ID of the run to resume"
    )
    
    # agent stop
    agent_stop_parser = agent_subparsers.add_parser(
        "stop",
        help="Stop an agent run"
    )
    agent_stop_parser.add_argument(
        "run_id",
        type=str,
        help="ID of the run to stop"
    )
    
    # agent status
    agent_subparsers.add_parser(
        "status",
        help="Show status of active agent runs"
    )
    
    # agent inspect
    agent_inspect_parser = agent_subparsers.add_parser(
        "inspect",
        help="Inspect an agent run in detail"
    )
    agent_inspect_parser.add_argument(
        "run_id",
        type=str,
        help="ID of the run to inspect"
    )
    
    # agent logs
    agent_logs_parser = agent_subparsers.add_parser(
        "logs",
        help="Show logs for an agent run"
    )
    agent_logs_parser.add_argument(
        "run_id",
        type=str,
        help="ID of the run to show logs for"
    )
    
    # agent delete
    agent_delete_parser = agent_subparsers.add_parser(
        "delete",
        help="Delete an agent"
    )
    agent_delete_parser.add_argument(
        "agent_id",
        type=str,
        help="ID of the agent to delete"
    )
    
    # agent schedule
    agent_schedule_parser = agent_subparsers.add_parser(
        "schedule",
        help="Schedule an agent to run at a specific time"
    )
    agent_schedule_parser.add_argument(
        "agent_id",
        type=str,
        help="ID of the agent to schedule"
    )
    agent_schedule_parser.add_argument(
        "--time", "-t",
        type=str,
        default=None,
        help="Time to run (e.g., '09:00', 'every day at 09:00')"
    )
    agent_schedule_parser.add_argument(
        "--recurring", "-r",
        action="store_true",
        help="Make this a recurring schedule"
    )
    
    # agent schedules
    agent_subparsers.add_parser(
        "schedules",
        help="List scheduled agents"
    )
    
    # agent cancel
    agent_cancel_parser = agent_subparsers.add_parser(
        "cancel",
        help="Cancel a scheduled agent"
    )
    agent_cancel_parser.add_argument(
        "schedule_id",
        type=str,
        help="ID of the schedule to cancel"
    )


def handle_agent_command(app: "LivingAIApp", args):
    """
    Handle agent-related commands.
    
    Args:
        app: The LivingAI application instance
        args: Parsed command-line arguments
    """
    from .agents.cli_handlers import handle_agent_command as agent_handle_command
    agent_handle_command(app, args)
