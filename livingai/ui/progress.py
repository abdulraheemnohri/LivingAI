# LivingAI UI Progress Utilities
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from typing import Any


class ProgressBar:
    """Rich progress bar wrapper for downloads and benchmarks."""

    @staticmethod
    def create_download_progress() -> Progress:
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn()
        )
