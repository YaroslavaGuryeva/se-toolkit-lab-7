#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode: print response to stdout
"""
import argparse
import sys
from pathlib import Path

# Add bot directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.intent_router import route as route_intent


def parse_command(text: str) -> tuple[str, str]:
    """Parse a command string like '/start' or '/scores lab-04'.
    
    Returns:
        Tuple of (command_name, arguments)
    """
    text = text.strip()
    if not text.startswith('/'):
        # Plain text - will be handled by LLM in Task 3
        return ('', text)
    
    parts = text[1:].split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ''
    return (command, args)


def run_command(command: str, args: str) -> str:
    """Run a command handler and return the response.

    Args:
        command: Command name without '/' (e.g., 'start', 'help')
        args: Command arguments (if any)

    Returns:
        Response text from the handler
    """
    # If no command but has text, route through LLM
    if not command and args:
        return route_intent(args)
    
    handlers = {
        'start': lambda: handle_start(),
        'help': lambda: handle_help(),
        'health': lambda: handle_health(),
        'labs': lambda: handle_labs(),
        'scores': lambda: handle_scores(args),
    }

    handler = handlers.get(command)
    if handler is None:
        return f"Unknown command: /{command}. Use /help to see available commands."

    return handler()


def test_mode(command_text: str) -> None:
    """Run in test mode: execute command and print response to stdout.
    
    Args:
        command_text: Full command string like '/start' or '/scores lab-04'
    """
    command, args = parse_command(command_text)
    response = run_command(command, args)
    print(response)
    sys.exit(0)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LMS Telegram Bot')
    parser.add_argument(
        '--test',
        metavar='COMMAND',
        help='Test mode: run a command and print response (no Telegram connection)'
    )
    
    args = parser.parse_args()
    
    if args.test:
        test_mode(args.test)
        return
    
    # TODO: Task 2+ — Start Telegram bot
    print("Telegram bot startup not yet implemented.")
    print("Run with --test to test handlers offline.")
    sys.exit(1)


if __name__ == '__main__':
    main()
