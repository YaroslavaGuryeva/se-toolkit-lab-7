"""Command handlers for the LMS bot.

Handlers are plain functions that take command input and return text.
They have no dependency on Telegram — same function works from --test,
unit tests, or the Telegram bot.
"""
from services.lms_api import get_lms_client


def handle_start() -> str:
    """Handle /start command — returns a welcome message."""
    return """Welcome to the LMS Bot! 

I can help you check system health, browse labs, and view scores. You can:
• Use slash commands like /help, /health, /labs, /scores
• Or just ask me questions like "which lab has the lowest pass rate?"

Use /help to see all available commands."""


def handle_help() -> str:
    """Handle /help command — lists available commands."""
    return """Available commands:
/start — Welcome message
/help — Show this help message
/health — Check backend status
/labs — List available labs
/scores <lab> — View scores for a specific lab

You can also ask questions in plain English:
• "what labs are available?"
• "show me scores for lab 4"
• "which lab has the lowest pass rate?"
• "who are the top 5 students?"
• "how many students are enrolled?"
"""


def handle_health() -> str:
    """Handle /health command — checks backend status."""
    client = get_lms_client()
    result = client.get_items()
    
    if isinstance(result, tuple):
        # Error occurred
        _, error_msg = result
        return f"Backend error: {error_msg}"
    
    # Success - result is a list of items
    item_count = len(result)
    return f"Backend is healthy. {item_count} items available."


def handle_labs() -> str:
    """Handle /labs command — lists available labs."""
    client = get_lms_client()
    result = client.get_items()
    
    if isinstance(result, tuple):
        # Error occurred
        _, error_msg = result
        return f"Backend error: {error_msg}"
    
    # Filter for labs only (not tasks)
    labs = [item for item in result if item.get('type') == 'lab']
    
    if not labs:
        return "No labs available."
    
    lines = ["Available labs:"]
    for lab in labs:
        title = lab.get('title', 'Unknown')
        lines.append(f"- {title}")
    
    return "\n".join(lines)


def handle_scores(lab_id: str = "") -> str:
    """Handle /scores command — shows scores for a lab.

    Args:
        lab_id: The lab identifier (e.g., 'lab-04')
    """
    if not lab_id:
        return "Please specify a lab, e.g., /scores lab-04"
    
    client = get_lms_client()
    result = client.get_pass_rates(lab_id)
    
    if isinstance(result, tuple):
        # Error occurred
        _, error_msg = result
        return f"Backend error: {error_msg}"
    
    # result is a list of dicts with task, avg_score, attempts
    if not result:
        return f"No pass rate data available for {lab_id}."
    
    # Format lab ID for display (lab-04 -> Lab 04)
    lab_display = lab_id.replace('lab-', 'Lab ').title()
    
    lines = [f"Pass rates for {lab_display}:"]
    
    for item in result:
        task_name = item.get('task', 'Unknown task')
        avg_score = item.get('avg_score', 0)
        attempts = item.get('attempts', 0)
        lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")
    
    return "\n".join(lines)
