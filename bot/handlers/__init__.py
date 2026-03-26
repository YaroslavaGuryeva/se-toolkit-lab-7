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
from .intent_router import route as route_intent

__all__ = [
    'handle_start',
    'handle_help',
    'handle_health',
    'handle_labs',
    'handle_scores',
    'route_intent',
]
