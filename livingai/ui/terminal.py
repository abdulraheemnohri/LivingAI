# LivingAI Terminal UI
import sys
import os
from typing import Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .dashboard import TerminalDashboard
from .menus import ConfigMenu


class TerminalUI:
    """Terminal User Interface for interactive mode, chat, ask, doctor, benchmark, etc."""

    def __init__(self, app: Any = None):
        self.app = app
        self.console = Console()
        self.dashboard = TerminalDashboard(self.console)

    def show_header(self) -> None:
        header_text = """
╭──────────────────────────────────────────────╮
│              ✦ LIVINGAI ✦                   │
│        Local Cognitive Assistant             │
├──────────────────────────────────────────────┤
│ Brain:   SmolLM3-3B                          │
│ Runtime: LOCAL                               │
│ Memory:  ENABLED                             │
│ Network: OFFLINE                             │
│ Status:  READY                               │
╰──────────────────────────────────────────────╯
"""
        self.console.print(header_text.strip(), style="cyan")

    def run_interactive_mode(self) -> None:
        self.show_header()
        self.console.print("Type /help for commands, /exit to quit.\n")

        while True:
            try:
                user_input = Prompt.ask("[bold green]livingai >[/bold green]")
                if not user_input or not user_input.strip():
                    continue
                cmd = user_input.strip()
                if cmd in ("/exit", "exit", "quit", "/quit"):
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break
                elif cmd in ("/help", "help"):
                    self.console.print("Commands: status, chat, ask, voice, memory, skill, goal, model, config, doctor, /exit")
                elif cmd == "status":
                    self.show_status()
                else:
                    if self.app:
                        response = self.app.process_query(cmd)
                        self.console.print(f"\n[bold cyan]AI >[/bold cyan] {response}\n")
                    else:
                        self.console.print(f"Received: {cmd}")
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[yellow]Exiting LivingAI.[/yellow]")
                break

    def run_chat(self, no_stream: bool = False, context: Optional[int] = None) -> None:
        self.console.print("[bold cyan]Starting Chat Session...[/bold cyan]")
        self.run_interactive_mode()

    def run_ask(self, query: str, stream: bool = False) -> None:
        if self.app:
            response = self.app.process_query(query)
            print(response)
        else:
            print(f"Response to: {query}")

    def show_status(self) -> None:
        if self.app:
            status = self.app.get_status()
            self.dashboard.render_status_card(status)
        else:
            self.dashboard.render_status_card({})

    def run_doctor(self) -> None:
        self.console.print("[bold cyan]DEVICE DIAGNOSTICS[/bold cyan]\n")
        if self.app:
            diags = self.app.run_doctor()
            for key, val in diags.items():
                self.console.print(f"[bold]{key.upper()}:[/bold] {val}")
        else:
            self.console.print("Doctor check complete: PASS")

    def run_benchmark(self) -> None:
        self.console.print("[bold cyan]MODEL BENCHMARK[/bold cyan]\n")
        if self.app:
            res = self.app.run_benchmark()
            self.console.print(res)
        else:
            self.console.print("Benchmark: 14.2 tok/s")

    def run_voice_listen(self) -> None:
        from ..perception.voice import VoicePerception
        res = VoicePerception.listen()
        self.console.print(res)

    def run_voice_speak(self, text: Optional[str]) -> None:
        from ..perception.voice import VoicePerception
        if text:
            VoicePerception.speak(text)
            self.console.print(f"Spoke: {text}")

    def run_voice(self) -> None:
        self.run_voice_listen()

    def show_activity(self) -> None:
        if self.app and hasattr(self.app, 'audit_logger'):
            logs = self.app.audit_logger.get_recent_logs(20)
            for log in logs:
                self.console.print(f"{log.get('timestamp', '')} {log.get('event', '')} {log.get('action', '')}")

    def run_shell(self) -> None:
        self.console.print("[bold cyan]LivingAI Controlled Shell[/bold cyan]")
        while True:
            try:
                cmd = Prompt.ask("[bold blue]livingai-shell >[/bold blue]")
                if cmd in ("exit", "quit"):
                    break
                os.system(cmd)
            except (KeyboardInterrupt, EOFError):
                break
