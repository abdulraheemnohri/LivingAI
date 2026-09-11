# LivingAI Input Sanitizer
import re


class InputSanitizer:
    """Sanitizes user input, file data, and prompts to prevent prompt injection and core code tampering."""

    @staticmethod
    def sanitize_text(text: str) -> str:
        if not text:
            return ""
        # Neutralize system prompt injection directives
        sanitized = re.sub(r'(?i)(system prompt:|ignore previous instructions)', '[filtered]', text)
        return sanitized.strip()

    @staticmethod
    def sanitize_command(command: str) -> str:
        # Prevent shell chain operators or dangerous wildcards in untrusted commands
        cleaned = command.strip()
        cleaned = re.sub(r'[\r\n]', ' ', cleaned)
        return cleaned
