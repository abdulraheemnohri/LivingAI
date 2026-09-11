# LivingAI Generation Wrapper
import logging
from typing import Dict, Any, Generator, Optional


class TextGenerator:
    """Provides high-level text generation facilities and streaming wrappers around SmolLM3-3B model runtime."""

    def __init__(self, model_manager: Any):
        self.model_manager = model_manager

    def generate(self, prompt: str, **kwargs) -> str:
        return self.model_manager.generate(prompt, **kwargs)

    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        return self.model_manager.generate_streaming(prompt, **kwargs)
