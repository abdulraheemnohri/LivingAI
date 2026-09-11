# LivingAI CLI: Main Command-Line Interface
# ============================================
# This module provides the CLI for LivingAI, built using Python's argparse.

import argparse
import sys
import os
import shutil
from typing import Optional, List

# Local imports
from .app import LivingAIApp
from .ui.terminal import TerminalUI


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="livingai",
        description="LivingAI: One-Model Local AI Operating System for Android Terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--config", "-c", type=str, default=None, help="Path to custom config file")
    
    subparsers = parser.add_subparsers(
        dest="command",
        title="Available Commands",
        description="Use 'livingai <command> --help' for more details on a command."
    )

    subparsers.add_parser("version", help="Show version and exit")

    env_parser = subparsers.add_parser("env", help="Manage Python virtual environment")
    env_subparsers = env_parser.add_subparsers(dest="env_command", title="Env Commands")
    env_subparsers.add_parser("remove", help="Remove virtual environment")

    db_parser = subparsers.add_parser("database", help="Manage database")
    db_subparsers = db_parser.add_subparsers(dest="database_command", title="Database Commands")
    db_subparsers.add_parser("init", help="Initialize database")
    db_subparsers.add_parser("doctor", help="Run database diagnostics")

    server_parser = subparsers.add_parser("server", help="Start local REST API server")
    server_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    server_parser.add_argument("--port", type=int, default=8080, help="Port number")

    subparsers.add_parser("logs", help="View recent application logs")

    chat_parser = subparsers.add_parser("chat", help="Start an interactive chat session")
    chat_parser.add_argument("--no-stream", action="store_true", help="Disable streaming responses")
    chat_parser.add_argument("--context", type=int, default=None, help="Override context window size")

    ask_parser = subparsers.add_parser("ask", help="Ask a direct question")
    ask_parser.add_argument("query", nargs="*", help="The question or prompt to ask")
    ask_parser.add_argument("--stream", action="store_true", help="Stream the response")

    voice_parser = subparsers.add_parser("voice", help="Voice input/output")
    voice_parser.add_argument("voice_cmd", nargs="?", choices=["listen", "speak"], help="Voice command")
    voice_parser.add_argument("--text", "-t", type=str, default=None, help="Text to speak")

    subparsers.add_parser("status", help="Show system status")

    model_parser = subparsers.add_parser("model", help="Manage the AI model")
    model_subparsers = model_parser.add_subparsers(dest="model_command", title="Model Commands")
    model_subparsers.add_parser("status", help="Show model status")
    model_subparsers.add_parser("download", help="Download the model")
    model_subparsers.add_parser("verify", help="Verify model integrity")
    model_subparsers.add_parser("info", help="Show model information")
    model_subparsers.add_parser("benchmark", help="Benchmark model performance")
    model_subparsers.add_parser("unload", help="Unload the model from memory")
    model_subparsers.add_parser("reload", help="Reload the model")

    memory_parser = subparsers.add_parser("memory", help="Manage memories")
    memory_subparsers = memory_parser.add_subparsers(dest="memory_command", title="Memory Commands")
    memory_subparsers.add_parser("list", help="List all memories")
    memory_search = memory_subparsers.add_parser("search", help="Search memories")
    memory_search.add_argument("query", type=str, help="Search query")
    memory_subparsers.add_parser("add", help="Add a new memory")
    memory_show = memory_subparsers.add_parser("show", help="Show a memory by ID")
    memory_show.add_argument("memory_id", type=int, help="Memory ID")
    memory_edit = memory_subparsers.add_parser("edit", help="Edit a memory by ID")
    memory_edit.add_argument("memory_id", type=int, help="Memory ID")
    memory_forget = memory_subparsers.add_parser("forget", help="Forget a memory by ID")
    memory_forget.add_argument("memory_id", type=int, help="Memory ID")
    memory_subparsers.add_parser("export", help="Export memories")
    memory_subparsers.add_parser("import", help="Import memories")
    memory_subparsers.add_parser("consolidate", help="Consolidate memories")
    memory_subparsers.add_parser("stats", help="Show memory statistics")

    skill_parser = subparsers.add_parser("skill", help="Manage skills")
    skill_subparsers = skill_parser.add_subparsers(dest="skill_command", title="Skill Commands")
    skill_subparsers.add_parser("list", help="List all skills")
    skill_create = skill_subparsers.add_parser("create", help="Create a new skill")
    skill_create.add_argument("name", type=str, help="Skill name")
    skill_test = skill_subparsers.add_parser("test", help="Test a skill")
    skill_test.add_argument("skill_name", type=str, help="Skill name")
    skill_run = skill_subparsers.add_parser("run", help="Run a skill")
    skill_run.add_argument("skill_name", type=str, help="Skill name")
    skill_run.add_argument("args", nargs="*", help="Arguments for the skill")
    skill_subparsers.add_parser("disable", help="Disable a skill")
    skill_subparsers.add_parser("delete", help="Delete a skill")
    skill_subparsers.add_parser("export", help="Export a skill")
    skill_subparsers.add_parser("import", help="Import a skill")

    goal_parser = subparsers.add_parser("goal", help="Manage goals")
    goal_subparsers = goal_parser.add_subparsers(dest="goal_command", title="Goal Commands")
    goal_subparsers.add_parser("list", help="List all goals")
    goal_add = goal_subparsers.add_parser("add", help="Add a new goal")
    goal_add.add_argument("title", type=str, help="Goal title")
    goal_add.add_argument("--description", "-d", type=str, default=None, help="Goal description")
    goal_show = goal_subparsers.add_parser("show", help="Show a goal by ID")
    goal_show.add_argument("goal_id", type=int, help="Goal ID")
    goal_start = goal_subparsers.add_parser("start", help="Start a goal")
    goal_start.add_argument("goal_id", type=int, help="Goal ID")
    goal_pause = goal_subparsers.add_parser("pause", help="Pause a goal")
    goal_pause.add_argument("goal_id", type=int, help="Goal ID")
    goal_complete = goal_subparsers.add_parser("complete", help="Complete a goal")
    goal_complete.add_argument("goal_id", type=int, help="Goal ID")
    goal_delete = goal_subparsers.add_parser("delete", help="Delete a goal")
    goal_delete.add_argument("goal_id", type=int, help="Goal ID")

    learn_parser = subparsers.add_parser("learn", help="Review and consolidate learning")
    learn_subparsers = learn_parser.add_subparsers(dest="learn_command", title="Learn Commands")
    learn_subparsers.add_parser("status", help="Show learning status")
    learn_subparsers.add_parser("review", help="Review recent lessons")
    learn_subparsers.add_parser("consolidate", help="Consolidate learned knowledge")
    learn_subparsers.add_parser("lessons", help="List all lessons")

    subparsers.add_parser("activity", help="Show recent activity")

    action_parser = subparsers.add_parser("action", help="Manage actions")
    action_subparsers = action_parser.add_subparsers(dest="action_command", title="Action Commands")
    action_subparsers.add_parser("allowlist", help="Show action allowlist")
    action_subparsers.add_parser("confirmations", help="Manage action confirmations")

    config_parser = subparsers.add_parser("config", help="Configure settings")
    config_subparsers = config_parser.add_subparsers(dest="config_command", title="Config Commands")
    config_subparsers.add_parser("show", help="Show current configuration")
    config_get = config_subparsers.add_parser("get", help="Get a configuration value")
    config_get.add_argument("key", type=str, help="Configuration key")
    config_set = config_subparsers.add_parser("set", help="Set a configuration value")
    config_set.add_argument("key", type=str, help="Configuration key")
    config_set.add_argument("value", type=str, help="Configuration value")
    config_subparsers.add_parser("reset", help="Reset configuration to defaults")
    config_subparsers.add_parser("edit", help="Edit configuration interactively")
    config_subparsers.add_parser("menu", help="Interactive configuration menu")

    subparsers.add_parser("doctor", help="Run system diagnostics")
    subparsers.add_parser("benchmark", help="Benchmark model performance")

    backup_parser = subparsers.add_parser("backup", help="Backup data")
    backup_subparsers = backup_parser.add_subparsers(dest="backup_command", title="Backup Commands")
    backup_subparsers.add_parser("create", help="Create a backup")
    backup_subparsers.add_parser("list", help="List all backups")
    backup_subparsers.add_parser("restore", help="Restore from a backup")

    subparsers.add_parser("restore", help="Restore from backup")

    daemon_parser = subparsers.add_parser("daemon", help="Start background daemon")
    daemon_parser.add_argument("--stop", action="store_true", help="Stop the daemon")
    daemon_parser.add_argument("--restart", action="store_true", help="Restart the daemon")

    subparsers.add_parser("idle", help="Run idle-mode tasks")
    subparsers.add_parser("shell", help="Controlled shell interface")

    return parser


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = create_parser()
    return parser.parse_args(args)


def handle_version() -> None:
    from . import __version__
    print(f"LivingAI v{__version__}")
    sys.exit(0)


def handle_interactive_mode() -> None:
    from .app import LivingAIApp
    from .ui.terminal import TerminalUI
    
    app = LivingAIApp()
    ui = TerminalUI(app)
    ui.run_interactive_mode()


def main() -> None:
    args = parse_args()
    
    if args.version or getattr(args, "command", None) == "version":
        handle_version()
    
    if args.verbose:
        os.environ["LIVINGAI_LOG_LEVEL"] = "DEBUG"
    
    app = LivingAIApp(config_path=args.config)
    
    if not hasattr(args, "command") or args.command is None:
        handle_interactive_mode()
    else:
        handle_command(app, args)


def handle_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    from .ui.terminal import TerminalUI
    ui = TerminalUI(app)

    if args.command == "version":
        handle_version()
    elif args.command == "server":
        from .server.server import APIServer
        server = APIServer(app, host=args.host, port=args.port)
        server.start()
    elif args.command == "env":
        handle_env_command(app, args)
    elif args.command == "database":
        handle_database_command(app, args)
    elif args.command == "logs":
        log_file = os.path.expanduser("~/.livingai/logs/livingai.log")
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                print(f.read()[-2000:])
        else:
            print("No log file found.")
    elif args.command == "chat":
        ui.run_chat(no_stream=args.no_stream, context=args.context)
    elif args.command == "ask":
        from .perception.terminal import TerminalPerception
        piped = TerminalPerception.read_piped_input()
        query = " ".join(args.query) if args.query else ""
        if piped:
            query = f"{query}\n\n[Piped Input]:\n{piped}" if query else piped
        if not query:
            print("Error: No query provided. Use: livingai ask <your question>")
            sys.exit(1)
        ui.run_ask(query, stream=args.stream)
    elif args.command == "voice":
        voice_cmd = getattr(args, "voice_cmd", None)
        if voice_cmd == "listen":
            ui.run_voice_listen()
        elif voice_cmd == "speak":
            ui.run_voice_speak(args.text)
        else:
            ui.run_voice()
    elif args.command == "status":
        ui.show_status()
    elif args.command == "model":
        handle_model_command(app, args)
    elif args.command == "memory":
        handle_memory_command(app, args)
    elif args.command == "skill":
        handle_skill_command(app, args)
    elif args.command == "goal":
        handle_goal_command(app, args)
    elif args.command == "learn":
        handle_learn_command(app, args)
    elif args.command == "activity":
        ui.show_activity()
    elif args.command == "action":
        handle_action_command(app, args)
    elif args.command == "config":
        handle_config_command(app, args)
    elif args.command == "doctor":
        ui.run_doctor()
    elif args.command == "benchmark":
        ui.run_benchmark()
    elif args.command == "backup":
        handle_backup_command(app, args)
    elif args.command == "restore":
        app.backup_manager.restore()
    elif args.command == "daemon":
        if args.stop:
            app.daemon.stop()
        elif args.restart:
            app.daemon.restart()
        else:
            app.daemon.start()
    elif args.command == "idle":
        app.idle.run()
    elif args.command == "shell":
        ui.run_shell()
    else:
        print(f"Error: Unknown command '{args.command}'")
        sys.exit(1)


def handle_env_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    venv_dir = os.path.expanduser("~/.livingai/runtime/venv")
    if getattr(args, "env_command", None) == "remove":
        confirm = input("Are you sure you want to remove the virtual environment? (y/N): ")
        if confirm.lower() == "y":
            if os.path.exists(venv_dir):
                shutil.rmtree(venv_dir)
                print("✅ Virtual environment removed.")
            else:
                print("Virtual environment directory does not exist.")
    else:
        print(f"Python Version: {sys.version}")
        print(f"Environment Location: {venv_dir}")
        print(f"Venv Exists: {'Yes' if os.path.exists(venv_dir) else 'No'}")


def handle_database_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    if getattr(args, "database_command", None) == "init":
        app.memory_manager.db.initialize()
        print("✅ Database initialized successfully.")
    elif getattr(args, "database_command", None) == "doctor":
        diags = app.memory_manager.db.doctor()
        print(f"Database Diagnostics: {diags}")
    else:
        print("Use 'livingai database init' or 'livingai database doctor'.")


def handle_model_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    cmd = getattr(args, "model_command", None)
    if cmd == "status":
        app.model_manager.status()
    elif cmd == "download":
        app.model_manager.download()
    elif cmd == "verify":
        app.model_manager.verify()
    elif cmd == "info":
        print(app.model_manager.info())
    elif cmd == "benchmark":
        print(app.model_manager.benchmark())
    elif cmd == "unload":
        app.model_manager.unload()
    elif cmd == "reload":
        app.model_manager.reload()
    else:
        app.model_manager.status()


def handle_memory_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    cmd = getattr(args, "memory_command", None)
    if cmd == "list":
        memories = app.memory_manager.list_all()
        for m in memories:
            print(f"[{m.id}] ({m.memory_type.value}) {m.content}")
    elif cmd == "search":
        results = app.memory_manager.search(args.query)
        for m in results:
            print(f"[{m.id}] {m.content}")
    elif cmd == "add":
        content = input("Enter memory content: ")
        if content:
            app.memory_manager.add({"content": content})
            print("✅ Memory saved.")
    elif cmd == "show":
        m = app.memory_manager.get(args.memory_id)
        print(m if m else "Memory not found.")
    elif cmd == "forget":
        app.memory_manager.forget(args.memory_id)
        print("✅ Memory forgotten.")
    elif cmd == "stats":
        print(app.memory_manager.get_stats())
    elif cmd == "consolidate":
        app.memory_manager.consolidate()
        print("✅ Memory consolidated.")
    else:
        memories = app.memory_manager.list_all()
        print(f"Total memories: {len(memories)}")


def handle_skill_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    cmd = getattr(args, "skill_command", None)
    if cmd == "list":
        skills = app.skill_manager.list_skills()
        print(f"Skills: {skills}")
    elif cmd == "create":
        app.skill_manager.create_skill(args.name)
        print(f"✅ Skill {args.name} created.")
    else:
        print(f"Skill count: {app.skill_manager.get_skill_count()}")


def handle_goal_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    cmd = getattr(args, "goal_command", None)
    if cmd == "list":
        goals = app.goal_manager.get_active_goals()
        for g in goals:
            print(f"[{g.get('id')}] {g.get('title')} ({g.get('status')})")
    elif cmd == "add":
        app.goal_manager.add_goal(args.title, args.description)
        print(f"✅ Goal '{args.title}' added.")
    else:
        goals = app.goal_manager.get_active_goals()
        print(f"Active goals: {len(goals)}")


def handle_learn_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    cmd = getattr(args, "learn_command", None)
    if cmd == "status":
        print(app.learning_engine.get_status())
    elif cmd == "lessons":
        print(app.learning_engine.get_lessons())
    elif cmd == "consolidate":
        app.learning_engine.consolidate()
        print("✅ Learning consolidated.")
    else:
        print(app.learning_engine.get_status())


def handle_action_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    cmd = getattr(args, "action_command", None)
    if cmd == "allowlist":
        print("Allowed safe commands: ls, pwd, cat, grep, find, head, tail, date, df, du")
    elif cmd == "confirmations":
        print(app.action_engine.get_confirmations_status())
    else:
        print("Action Policy: Active")


def handle_config_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    cmd = getattr(args, "config_command", None)
    if cmd == "show":
        print(app.config.show())
    elif cmd == "get":
        print(app.config.get(args.key))
    elif cmd == "set":
        app.config.set(args.key, args.value)
        print(f"✅ Config updated: {args.key} = {args.value}")
    elif cmd == "reset":
        app.config.reset()
        print("✅ Config reset to defaults.")
    elif cmd == "menu":
        from .ui.menus import ConfigMenu
        menu = ConfigMenu(app.config)
        menu.show_menu()
    else:
        print(app.config.show())


def handle_backup_command(app: LivingAIApp, args: argparse.Namespace) -> None:
    cmd = getattr(args, "backup_command", None)
    if cmd == "create":
        app.backup_manager.create()
    elif cmd == "list":
        print(app.backup_manager.list())
    elif cmd == "restore":
        app.backup_manager.restore()
    else:
        print(app.backup_manager.list())


if __name__ == "__main__":
    main()
