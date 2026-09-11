# LivingAI Terminal Dashboard
from rich.console import Console
from rich.panel import Panel
from typing import Dict, Any


class TerminalDashboard:
    """Renders ANSI / Unicode terminal dashboard status cards."""

    def __init__(self, console: Console = None):
        self.console = console or Console()

    def render_status_card(self, status: Dict[str, Any]) -> None:
        model_info = status.get("model", {})
        if isinstance(model_info, dict):
            runtime = model_info.get("runtime", "LOCAL")
        else:
            runtime = "LOCAL"

        memory_info = status.get("memory", {})
        if hasattr(memory_info, "total_memories"):
            total_memories = memory_info.total_memories
        elif isinstance(memory_info, dict):
            total_memories = memory_info.get("total_memories", 0)
        else:
            total_memories = 0

        goals_info = status.get("goals", [])
        active_goals = len(goals_info) if isinstance(goals_info, list) else 0

        skills_count = status.get("skills", 0)

        state_info = status.get("state", {})
        if hasattr(state_info, "get_summary"):
            summary = state_info.get_summary()
            activity = summary.get("activity", "IDLE").upper()
            vars_dict = summary.get("variables", {})
            energy = vars_dict.get("energy", {}).get("percent", 100)
            focus = vars_dict.get("focus", {}).get("percent", 100)
        elif isinstance(state_info, dict):
            activity = state_info.get("activity", "IDLE").upper()
            energy = state_info.get("energy", 100)
            focus = state_info.get("focus", 100)
        else:
            activity = "IDLE"
            energy = 100
            focus = 100

        content = f"""
 STATUS       ● ONLINE
 BRAIN        SmolLM3-3B
 RUNTIME      {runtime}
 MEMORY       {total_memories}
 SKILLS       {skills_count}
 GOALS        {active_goals} active
 STATE        {activity}
 ENERGY       {energy}%
 FOCUS        {focus}%
 NETWORK      OFFLINE
"""
        panel = Panel(
            content.strip(),
            title="[bold cyan]✦ LIVINGAI ✦[/bold cyan]",
            subtitle="[dim]Local Cognitive Assistant[/dim]",
            border_style="cyan"
        )
        self.console.print(panel)
