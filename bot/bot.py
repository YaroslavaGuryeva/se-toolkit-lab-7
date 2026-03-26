#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode: print response to stdout
"""
import argparse
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

# Add bot directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.intent_router import route as route_intent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    # Start Telegram bot
    logger.info("Starting Telegram bot...")
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Register command handlers
    @dp.message(CommandStart())
    async def on_start(message: types.Message) -> None:
        response = handle_start()
        await message.answer(response)

    @dp.message(Command("help"))
    async def on_help(message: types.Message) -> None:
        response = handle_help()
        await message.answer(response)

    @dp.message(Command("health"))
    async def on_health(message: types.Message) -> None:
        response = handle_health()
        await message.answer(response)

    @dp.message(Command("labs"))
    async def on_labs(message: types.Message) -> None:
        response = handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def on_scores(message: types.Message) -> None:
        # Extract lab argument if provided
        args = message.text.split()[1:] if len(message.text.split()) > 1 else ""
        response = handle_scores(" ".join(args))
        await message.answer(response)

    @dp.message()
    async def on_plain_text(message: types.Message) -> None:
        """Handle plain text messages using LLM intent routing."""
        if message.text:
            response = route_intent(message.text)
            await message.answer(response)

    # Start polling
    logger.info("Bot is running. Press Ctrl+C to stop.")
    dp.run_polling(bot)


if __name__ == '__main__':
    main()
