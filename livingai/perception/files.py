# LivingAI File Perception
import os
from typing import Optional


class FilePerception:
    """Handles local file reading, chunking, and content ingestion."""

    @staticmethod
    def read_file(filepath: str, max_bytes: int = 10 * 1024 * 1024) -> str:
        expanded_path = os.path.expanduser(filepath)
        if not os.path.exists(expanded_path):
            raise FileNotFoundError(f"File not found: {filepath}")

        file_size = os.path.getsize(expanded_path)
        if file_size > max_bytes:
            with open(expanded_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read(max_bytes) + "\n\n[Content truncated due to size limit]"

        with open(expanded_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
