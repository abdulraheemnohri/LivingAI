# LivingAI Platform Package
from .termux import TermuxPlatform
from .android import AndroidPlatform
from .system import SystemInfo

__all__ = ["TermuxPlatform", "AndroidPlatform", "SystemInfo"]
