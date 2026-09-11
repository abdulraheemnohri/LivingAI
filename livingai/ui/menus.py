# LivingAI Config Menus
from rich.console import Console
from rich.prompt import Prompt
from typing import Any


class ConfigMenu:
    """Interactive configuration menu."""

    def __init__(self, config_manager: Any, console: Console = None):
        self.config_manager = config_manager
        self.console = console or Console()

    def show_menu(self) -> None:
        categories = [
            "Model", "Generation", "Memory", "Learning", "Skills", "Goals",
            "Autonomy", "Actions", "Voice", "Download", "Privacy", "Security",
            "Battery", "Performance", "Logging", "Backup", "Terminal"
        ]
        self.console.print("[bold cyan]LIVINGAI CONFIGURATION MENU[/bold cyan]\n")
        for idx, cat in enumerate(categories, 1):
            self.console.print(f"[{idx:2d}] {cat}")
        self.console.print("[ 0] Exit")

        choice = Prompt.ask("Select category", default="0")
        if choice != "0":
            self.console.print(f"[green]Selected category {choice}. (Use 'livingai config set <key> <value>' to modify settings directly)[/green]")
