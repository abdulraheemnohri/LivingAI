# LivingAI: One-Model Local AI Operating System for Android Terminal
# ================================================================
# This package provides a terminal-first AI assistant for Termux on Android.

__version__ = "1.0.0"
__author__ = "Abdulraheem Nohari"
__license__ = "MIT"

# Import core modules
from .cli import main
from .app import LivingAIApp

# Expose the main CLI entry point
__all__ = ["main", "LivingAIApp", "__version__"]
