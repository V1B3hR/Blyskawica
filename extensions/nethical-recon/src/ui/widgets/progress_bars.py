"""
Custom progress bars for the Command Center
"""

from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn


def create_progress_bar(filled: int, total: int, char: str = "█", empty_char: str = "░") -> str:
    """
    Create a simple text-based progress bar

    Args:
        filled: Number of filled segments
        total: Total segments
        char: Character for filled segments
        empty_char: Character for empty segments

    Returns:
        Progress bar string
    """
    if total <= 0:
        return ""

    filled = max(0, min(filled, total))
    return char * filled + empty_char * (total - filled)


def create_stealth_bar(percentage: int, width: int = 10) -> str:
    """
    Create a stealth indicator progress bar

    Args:
        percentage: Stealth percentage (0-100)
        width: Width of the bar in characters

    Returns:
        Stealth bar with emoji indicators
    """
    percentage = max(0, min(100, percentage))
    filled = int((percentage / 100) * width)

    # Use shush emoji for stealth
    stealth_char = "🤫"
    empty_char = "░"

    return stealth_char * filled + empty_char * (width - filled)


def create_confidence_bar(confidence: float, width: int = 10) -> str:
    """
    Create a confidence indicator bar

    Args:
        confidence: Confidence value (0.0-1.0)
        width: Width of the bar in characters

    Returns:
        Confidence bar string
    """
    confidence = max(0.0, min(1.0, confidence))
    filled = int(confidence * width)

    return "█" * filled + "░" * (width - filled)


def percentage_to_bar(percentage: int, width: int = 10, char: str = "█") -> str:
    """
    Convert percentage to a visual bar

    Args:
        percentage: Percentage (0-100)
        width: Width of the bar
        char: Character to use for filled portion

    Returns:
        Visual bar string
    """
    percentage = max(0, min(100, percentage))
    filled = int((percentage / 100) * width)

    return char * filled + "░" * (width - filled)


class RichProgressBar:
    """Rich-based progress bar for long-running operations"""

    def __init__(self, description: str = "Processing..."):
        self.description = description
        self.progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )

    def __enter__(self):
        self.progress.__enter__()
        return self.progress

    def __exit__(self, *args):
        self.progress.__exit__(*args)
