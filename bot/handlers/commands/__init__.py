"""Command handlers for the LMS bot.

Handlers are plain functions that take command input and return text.
They have no dependency on Telegram — same function works from --test,
unit tests, or the Telegram bot.
"""


def handle_start() -> str:
    """Handle /start command — returns a welcome message."""
    return "Welcome to the LMS Bot! I can help you check system health, browse labs, and view scores. Use /help to see all available commands."


def handle_help() -> str:
    """Handle /help command — lists available commands."""
    return """Available commands:
/start — Welcome message
/help — Show this help message
/health — Check backend status
/labs — List available labs
/scores <lab> — View scores for a specific lab"""


def handle_health() -> str:
    """Handle /health command — checks backend status."""
    # TODO: Task 2 — actually call the backend
    return "Backend status: OK (placeholder)"


def handle_labs() -> str:
    """Handle /labs command — lists available labs."""
    # TODO: Task 2 — fetch from backend
    return "Available labs: (placeholder)"


def handle_scores(lab_id: str = "") -> str:
    """Handle /scores command — shows scores for a lab.

    Args:
        lab_id: The lab identifier (e.g., 'lab-04')
    """
    # TODO: Task 2 — fetch from backend
    if not lab_id:
        return "Please specify a lab, e.g., /scores lab-04"
    return f"Scores for {lab_id}: (placeholder)"
