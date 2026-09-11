# LivingAI CLI: Main Command-Line Interface
# ============================================
# This module provides the CLI for LivingAI, built using Python's argparse.

import argparse
import sys
import os
from typing import Optional, List

# Local imports
from .app import LivingAIApp
from .ui.terminal import TerminalUI


def create_parser() -> argparse.ArgumentParser:
    """
    Create the main argument parser for LivingAI CLI.
    
    Returns:
        argparse.ArgumentParser: Configured parser with all subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="livingai",
        description="LivingAI: One-Model Local AI Operating System for Android Terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  livingai chat                 Start an interactive chat session
  livingai ask "question"       Ask a direct question
  livingai model download       Download the AI model
  livingai status              Show system status
  livingai doctor              Run system diagnostics
        """
    )
    
    # Global arguments
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help="Path to custom config file"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        title="Available Commands",
        description="Use 'livingai <command> --help' for more details on a command."
    )
    
    # --- Chat Command ---
    chat_parser = subparsers.add_parser(
        "chat",
        help="Start an interactive chat session",
        description="Start an interactive chat session with LivingAI."
    )
    chat_parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming responses"
    )
    chat_parser.add_argument(
        "--context",
        type=int,
        default=None,
        help="Override context window size"
    )
    
    # --- Ask Command ---
    ask_parser = subparsers.add_parser(
        "ask",
        help="Ask a direct question",
        description="Ask a direct question and get an answer (output only)."
    )
    ask_parser.add_argument(
        "query",
        nargs="*",
        help="The question or prompt to ask"
    )
    ask_parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream the response"
    )
    
    # --- Voice Command ---
    voice_parser = subparsers.add_parser(
        "voice",
        help="Voice input/output",
        description="Use voice input and/or text-to-speech output."
    )
    voice_parser.add_argument(
        "command",
        nargs="?",
        choices=["listen", "speak"],
        help="Voice command: 'listen' or 'speak'"
    )
    voice_parser.add_argument(
        "--text",
        "-t",
        type=str,
        default=None,
        help="Text to speak (for 'speak' command)"
    )
    
    # --- Status Command ---
    subparsers.add_parser(
        "status",
        help="Show system status",
        description="Display the current status of LivingAI (model, memory, goals, etc.)."
    )
    
    # --- Model Command ---
    model_parser = subparsers.add_parser(
        "model",
        help="Manage the AI model",
        description="Download, verify, and manage the AI model."
    )
    model_subparsers = model_parser.add_subparsers(
        dest="model_command",
        title="Model Commands"
    )
    
    model_subparsers.add_parser(
        "status",
        help="Show model status"
    )
    model_subparsers.add_parser(
        "download",
        help="Download the model"
    )
    model_subparsers.add_parser(
        "verify",
        help="Verify model integrity"
    )
    model_subparsers.add_parser(
        "info",
        help="Show model information"
    )
    model_subparsers.add_parser(
        "benchmark",
        help="Benchmark model performance"
    )
    model_subparsers.add_parser(
        "unload",
        help="Unload the model from memory"
    )
    model_subparsers.add_parser(
        "reload",
        help="Reload the model"
    )
    
    # --- Memory Command ---
    memory_parser = subparsers.add_parser(
        "memory",
        help="Manage memories",
        description="List, search, add, edit, or forget memories."
    )
    memory_subparsers = memory_parser.add_subparsers(
        dest="memory_command",
        title="Memory Commands"
    )
    
    memory_subparsers.add_parser(
        "list",
        help="List all memories"
    )
    memory_search_parser = memory_subparsers.add_parser(
        "search",
        help="Search memories"
    )
    memory_search_parser.add_argument(
        "query",
        type=str,
        help="Search query"
    )
    memory_subparsers.add_parser(
        "add",
        help="Add a new memory"
    )
    memory_show_parser = memory_subparsers.add_parser(
        "show",
        help="Show a memory by ID"
    )
    memory_show_parser.add_argument(
        "memory_id",
        type=int,
        help="Memory ID"
    )
    memory_edit_parser = memory_subparsers.add_parser(
        "edit",
        help="Edit a memory by ID"
    )
    memory_edit_parser.add_argument(
        "memory_id",
        type=int,
        help="Memory ID"
    )
    memory_forget_parser = memory_subparsers.add_parser(
        "forget",
        help="Forget a memory by ID"
    )
    memory_forget_parser.add_argument(
        "memory_id",
        type=int,
        help="Memory ID"
    )
    memory_subparsers.add_parser(
        "export",
        help="Export memories"
    )
    memory_subparsers.add_parser(
        "import",
        help="Import memories"
    )
    memory_subparsers.add_parser(
        "consolidate",
        help="Consolidate memories"
    )
    memory_subparsers.add_parser(
        "stats",
        help="Show memory statistics"
    )
    
    # --- Skill Command ---
    skill_parser = subparsers.add_parser(
        "skill",
        help="Manage skills",
        description="List, create, test, run, or delete skills."
    )
    skill_subparsers = skill_parser.add_subparsers(
        dest="skill_command",
        title="Skill Commands"
    )
    
    skill_subparsers.add_parser(
        "list",
        help="List all skills"
    )
    skill_create_parser = skill_subparsers.add_parser(
        "create",
        help="Create a new skill"
    )
    skill_create_parser.add_argument(
        "name",
        type=str,
        help="Skill name"
    )
    skill_test_parser = skill_subparsers.add_parser(
        "test",
        help="Test a skill"
    )
    skill_test_parser.add_argument(
        "skill_name",
        type=str,
        help="Skill name"
    )
    skill_run_parser = skill_subparsers.add_parser(
        "run",
        help="Run a skill"
    )
    skill_run_parser.add_argument(
        "skill_name",
        type=str,
        help="Skill name"
    )
    skill_run_parser.add_argument(
        "args",
        nargs="*",
        help="Arguments for the skill"
    )
    skill_subparsers.add_parser(
        "disable",
        help="Disable a skill"
    )
    skill_subparsers.add_parser(
        "delete",
        help="Delete a skill"
    )
    skill_subparsers.add_parser(
        "export",
        help="Export a skill"
    )
    skill_subparsers.add_parser(
        "import",
        help="Import a skill"
    )
    
    # --- Goal Command ---
    goal_parser = subparsers.add_parser(
        "goal",
        help="Manage goals",
        description="List, add, show, start, pause, complete, or delete goals."
    )
    goal_subparsers = goal_parser.add_subparsers(
        dest="goal_command",
        title="Goal Commands"
    )
    
    goal_subparsers.add_parser(
        "list",
        help="List all goals"
    )
    goal_add_parser = goal_subparsers.add_parser(
        "add",
        help="Add a new goal"
    )
    goal_add_parser.add_argument(
        "title",
        type=str,
        help="Goal title"
    )
    goal_add_parser.add_argument(
        "--description",
        "-d",
        type=str,
        default=None,
        help="Goal description"
    )
    goal_show_parser = goal_subparsers.add_parser(
        "show",
        help="Show a goal by ID"
    )
    goal_show_parser.add_argument(
        "goal_id",
        type=int,
        help="Goal ID"
    )
    goal_start_parser = goal_subparsers.add_parser(
        "start",
        help="Start a goal"
    )
    goal_start_parser.add_argument(
        "goal_id",
        type=int,
        help="Goal ID"
    )
    goal_pause_parser = goal_subparsers.add_parser(
        "pause",
        help="Pause a goal"
    )
    goal_pause_parser.add_argument(
        "goal_id",
        type=int,
        help="Goal ID"
    )
    goal_complete_parser = goal_subparsers.add_parser(
        "complete",
        help="Complete a goal"
    )
    goal_complete_parser.add_argument(
        "goal_id",
        type=int,
        help="Goal ID"
    )
    goal_delete_parser = goal_subparsers.add_parser(
        "delete",
        help="Delete a goal"
    )
    goal_delete_parser.add_argument(
        "goal_id",
        type=int,
        help="Goal ID"
    )
    
    # --- Learn Command ---
    learn_parser = subparsers.add_parser(
        "learn",
        help="Review and consolidate learning",
        description="Review, consolidate, and manage learned lessons."
    )
    learn_subparsers = learn_parser.add_subparsers(
        dest="learn_command",
        title="Learn Commands"
    )
    
    learn_subparsers.add_parser(
        "status",
        help="Show learning status"
    )
    learn_subparsers.add_parser(
        "review",
        help="Review recent lessons"
    )
    learn_subparsers.add_parser(
        "consolidate",
        help="Consolidate learned knowledge"
    )
    learn_subparsers.add_parser(
        "lessons",
        help="List all lessons"
    )
    
    # --- Activity Command ---
    subparsers.add_parser(
        "activity",
        help="Show recent activity",
        description="Display recent system activity and events."
    )
    
    # --- Action Command ---
    action_parser = subparsers.add_parser(
        "action",
        help="Manage actions",
        description="Manage action allowlists, confirmations, and policies."
    )
    action_subparsers = action_parser.add_subparsers(
        dest="action_command",
        title="Action Commands"
    )
    
    action_subparsers.add_parser(
        "allowlist",
        help="Show action allowlist"
    )
    action_subparsers.add_parser(
        "confirmations",
        help="Manage action confirmations"
    )
    
    # --- Config Command ---
    config_parser = subparsers.add_parser(
        "config",
        help="Configure settings",
        description="View or modify LivingAI configuration."
    )
    config_subparsers = config_parser.add_subparsers(
        dest="config_command",
        title="Config Commands"
    )
    
    config_subparsers.add_parser(
        "show",
        help="Show current configuration"
    )
    config_get_parser = config_subparsers.add_parser(
        "get",
        help="Get a configuration value"
    )
    config_get_parser.add_argument(
        "key",
        type=str,
        help="Configuration key (e.g., model.temperature)"
    )
    config_set_parser = config_subparsers.add_parser(
        "set",
        help="Set a configuration value"
    )
    config_set_parser.add_argument(
        "key",
        type=str,
        help="Configuration key"
    )
    config_set_parser.add_argument(
        "value",
        type=str,
        help="Configuration value"
    )
    config_subparsers.add_parser(
        "reset",
        help="Reset configuration to defaults"
    )
    config_subparsers.add_parser(
        "edit",
        help="Edit configuration interactively"
    )
    config_subparsers.add_parser(
        "menu",
        help="Interactive configuration menu"
    )
    
    # --- Doctor Command ---
    subparsers.add_parser(
        "doctor",
        help="Run system diagnostics",
        description="Check system health, dependencies, and model status."
    )
    
    # --- Benchmark Command ---
    subparsers.add_parser(
        "benchmark",
        help="Benchmark model performance",
        description="Measure model load time, token generation speed, and memory usage."
    )
    
    # --- Backup Command ---
    backup_parser = subparsers.add_parser(
        "backup",
        help="Backup data",
        description="Create, list, or restore backups of memories, skills, and goals."
    )
    backup_subparsers = backup_parser.add_subparsers(
        dest="backup_command",
        title="Backup Commands"
    )
    
    backup_subparsers.add_parser(
        "create",
        help="Create a backup"
    )
    backup_subparsers.add_parser(
        "list",
        help="List all backups"
    )
    backup_subparsers.add_parser(
        "restore",
        help="Restore from a backup"
    )
    
    # --- Restore Command (Alias for backup restore) ---
    subparsers.add_parser(
        "restore",
        help="Restore from backup",
        description="Alias for 'livingai backup restore'."
    )
    
    # --- Daemon Command ---
    daemon_parser = subparsers.add_parser(
        "daemon",
        help="Start background daemon",
        description="Start the LivingAI background daemon for idle tasks."
    )
    daemon_parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop the daemon"
    )
    daemon_parser.add_argument(
        "--restart",
        action="store_true",
        help="Restart the daemon"
    )
    
    # --- Idle Command ---
    subparsers.add_parser(
        "idle",
        help="Run idle-mode tasks",
        description="Run memory consolidation, goal review, and other idle tasks."
    )
    
    # --- Shell Command ---
    subparsers.add_parser(
        "shell",
        help="Controlled shell interface",
        description="Start a controlled shell interface with AI assistance."
    )
    
    return parser


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: List of arguments (defaults to sys.argv[1:])
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = create_parser()
    return parser.parse_args(args)


def handle_version() -> None:
    """Print version information and exit."""
    from . import __version__
    print(f"LivingAI v{__version__}")
    sys.exit(0)


def handle_interactive_mode() -> None:
    """Start the interactive LivingAI shell."""
    from .app import LivingAIApp
    from .ui.terminal import TerminalUI
    
    app = LivingAIApp()
    ui = TerminalUI(app)
    ui.run_interactive_mode()


def main() -> None:
    """
    Main entry point for the LivingAI CLI.
    """
    args = parse_args()
    
    # Handle version
    if args.version:
        handle_version()
    
    # Set up logging
    if args.verbose:
        os.environ["LIVINGAI_LOG_LEVEL"] = "DEBUG"
    
    # Initialize app
    app = LivingAIApp(config_path=args.config)
    
    # Handle commands
    if not hasattr(args, "command") or args.command is None:
        handle_interactive_mode()
    else:
        handle_command(app, args)


def handle_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    """
    Route the parsed command to the appropriate handler.
    
    Args:
        app: LivingAIApp instance
        args: Parsed command-line arguments
    """
    from .ui.terminal import TerminalUI
    ui = TerminalUI(app)
    
    # Chat
    if args.command == "chat":
        ui.run_chat(no_stream=args.no_stream, context=args.context)
    
    # Ask
    elif args.command == "ask":
        query = " ".join(args.query) if args.query else None
        if not query:
            print("Error: No query provided. Use: livingai ask <your question>")
            sys.exit(1)
        ui.run_ask(query, stream=args.stream)
    
    # Voice
    elif args.command == "voice":
        if args.command == "listen":
            ui.run_voice_listen()
        elif args.command == "speak":
            ui.run_voice_speak(args.text)
        else:
            ui.run_voice()
    
    # Status
    elif args.command == "status":
        ui.show_status()
    
    # Model
    elif args.command == "model":
        handle_model_command(app, args)
    
    # Memory
    elif args.command == "memory":
        handle_memory_command(app, args)
    
    # Skill
    elif args.command == "skill":
        handle_skill_command(app, args)
    
    # Goal
    elif args.command == "goal":
        handle_goal_command(app, args)
    
    # Learn
    elif args.command == "learn":
        handle_learn_command(app, args)
    
    # Activity
    elif args.command == "activity":
        ui.show_activity()
    
    # Action
    elif args.command == "action":
        handle_action_command(app, args)
    
    # Config
    elif args.command == "config":
        handle_config_command(app, args)
    
    # Doctor
    elif args.command == "doctor":
        ui.run_doctor()
    
    # Benchmark
    elif args.command == "benchmark":
        ui.run_benchmark()
    
    # Backup
    elif args.command == "backup":
        handle_backup_command(app, args)
    
    # Restore (alias)
    elif args.command == "restore":
        app.backup_manager.restore()
    
    # Daemon
    elif args.command == "daemon":
        if args.stop:
            app.daemon.stop()
        elif args.restart:
            app.daemon.restart()
        else:
            app.daemon.start()
    
    # Idle
    elif args.command == "idle":
        app.idle.run()
    
    # Shell
    elif args.command == "shell":
        ui.run_shell()
    
    else:
        print(f"Error: Unknown command '{args.command}'")
        sys.exit(1)


def handle_model_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    """Handle model subcommands."""
    if args.model_command == "status":
        app.model_manager.status()
    elif args.model_command == "download":
        app.model_manager.download()
    elif args.model_command == "verify":
        app.model_manager.verify()
    elif args.model_command == "info":
        app.model_manager.info()
    elif args.model_command == "benchmark":
        app.model_manager.benchmark()
    elif args.model_command == "unload":
        app.model_manager.unload()
    elif args.model_command == "reload":
        app.model_manager.reload()
    else:
        print(f"Error: Unknown model command '{args.model_command}'")
        sys.exit(1)


def handle_memory_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    """Handle memory subcommands."""
    if args.memory_command == "list":
        app.memory_manager.list()
    elif args.memory_command == "search":
        app.memory_manager.search(args.query)
    elif args.memory_command == "add":
        app.memory_manager.add()
    elif args.memory_command == "show":
        app.memory_manager.show(args.memory_id)
    elif args.memory_command == "edit":
        app.memory_manager.edit(args.memory_id)
    elif args.memory_command == "forget":
        app.memory_manager.forget(args.memory_id)
    elif args.memory_command == "export":
        app.memory_manager.export()
    elif args.memory_command == "import":
        app.memory_manager.import_()
    elif args.memory_command == "consolidate":
        app.memory_manager.consolidate()
    elif args.memory_command == "stats":
        app.memory_manager.stats()
    else:
        print(f"Error: Unknown memory command '{args.memory_command}'")
        sys.exit(1)


def handle_skill_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    """Handle skill subcommands."""
    if args.skill_command == "list":
        app.skill_manager.list()
    elif args.skill_command == "create":
        app.skill_manager.create(args.name)
    elif args.skill_command == "test":
        app.skill_manager.test(args.skill_name)
    elif args.skill_command == "run":
        app.skill_manager.run(args.skill_name, args.args)
    elif args.skill_command == "disable":
        app.skill_manager.disable()
    elif args.skill_command == "delete":
        app.skill_manager.delete()
    elif args.skill_command == "export":
        app.skill_manager.export()
    elif args.skill_command == "import":
        app.skill_manager.import_()
    else:
        print(f"Error: Unknown skill command '{args.skill_command}'")
        sys.exit(1)


def handle_goal_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    """Handle goal subcommands."""
    if args.goal_command == "list":
        app.goal_manager.list()
    elif args.goal_command == "add":
        app.goal_manager.add(args.title, args.description)
    elif args.goal_command == "show":
        app.goal_manager.show(args.goal_id)
    elif args.goal_command == "start":
        app.goal_manager.start(args.goal_id)
    elif args.goal_command == "pause":
        app.goal_manager.pause(args.goal_id)
    elif args.goal_command == "complete":
        app.goal_manager.complete(args.goal_id)
    elif args.goal_command == "delete":
        app.goal_manager.delete(args.goal_id)
    else:
        print(f"Error: Unknown goal command '{args.goal_command}'")
        sys.exit(1)


def handle_learn_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    """Handle learn subcommands."""
    if args.learn_command == "status":
        app.learning_engine.status()
    elif args.learn_command == "review":
        app.learning_engine.review()
    elif args.learn_command == "consolidate":
        app.learning_engine.consolidate()
    elif args.learn_command == "lessons":
        app.learning_engine.list_lessons()
    else:
        print(f"Error: Unknown learn command '{args.learn_command}'")
        sys.exit(1)


def handle_action_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    """Handle action subcommands."""
    if args.action_command == "allowlist":
        app.action_engine.show_allowlist()
    elif args.action_command == "confirmations":
        app.action_engine.manage_confirmations()
    else:
        print(f"Error: Unknown action command '{args.action_command}'")
        sys.exit(1)


def handle_config_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    """Handle config subcommands."""
    if args.config_command == "show":
        app.config.show()
    elif args.config_command == "get":
        app.config.get(args.key)
    elif args.config_command == "set":
        app.config.set(args.key, args.value)
    elif args.config_command == "reset":
        app.config.reset()
    elif args.config_command == "edit":
        app.config.edit()
    elif args.config_command == "menu":
        app.config.menu()
    else:
        print(f"Error: Unknown config command '{args.config_command}'")
        sys.exit(1)


def handle_backup_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    """Handle backup subcommands."""
    if args.backup_command == "create":
        app.backup_manager.create()
    elif args.backup_command == "list":
        app.backup_manager.list()
    elif args.backup_command == "restore":
        app.backup_manager.restore()
    else:
        print(f"Error: Unknown backup command '{args.backup_command}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
