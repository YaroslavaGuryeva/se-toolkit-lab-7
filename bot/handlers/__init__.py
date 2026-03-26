"""Command handlers for the LMS bot.

Handlers are plain functions that take command input and return text.
They have no dependency on Telegram — same function works from --test,
unit tests, or the Telegram bot.
"""

from .commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)

__all__ = [
    'handle_start',
    'handle_help',
    'handle_health',
    'handle_labs',
    'handle_scores',
]
