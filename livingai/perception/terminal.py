# LivingAI Terminal Perception
import sys
from typing import Dict, Any


class TerminalPerception:
    """Handles terminal input perception, stdin piping, and formatting."""

    @staticmethod
    def read_piped_input() -> str:
        if not sys.stdin.isatty():
            return sys.stdin.read().strip()
        return ""

    @staticmethod
    def parse_input(raw_input: str) -> Dict[str, Any]:
        return {
            "text": raw_input.strip(),
            "has_piped_input": bool(TerminalPerception.read_piped_input()),
        }
