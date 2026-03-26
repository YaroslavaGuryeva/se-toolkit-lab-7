"""Inline keyboard definitions for the Telegram bot."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Get the keyboard shown after /start command.
    
    Provides quick access to common queries.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Available Labs", callback_data="labs"),
                InlineKeyboardButton(text="💚 Health Check", callback_data="health"),
            ],
            [
                InlineKeyboardButton(text="📊 Lab Scores", callback_data="scores_prompt"),
                InlineKeyboardButton(text="👥 Top Learners", callback_data="top_learners"),
            ],
            [
                InlineKeyboardButton(text="📅 Timeline", callback_data="timeline_prompt"),
                InlineKeyboardButton(text="🔄 Sync Data", callback_data="sync"),
            ],
        ]
    )


def get_lab_selection_keyboard(lab_ids: list[str]) -> InlineKeyboardMarkup:
    """Get keyboard for selecting a lab.
    
    Args:
        lab_ids: List of lab identifiers (e.g., ['lab-01', 'lab-02', ...])
    """
    buttons = []
    row = []
    for lab_id in lab_ids[:10]:  # Limit to first 10 labs
        row.append(InlineKeyboardButton(text=lab_id.replace('lab-', 'Lab ').title(), callback_data=f"select_{lab_id}"))
        if len(row) >= 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_scores_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for score-related queries."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Pass Rates", callback_data="scores_pass_rates"),
                InlineKeyboardButton(text="Score Distribution", callback_data="scores_distribution"),
            ],
            [
                InlineKeyboardButton(text="Completion Rate", callback_data="scores_completion"),
                InlineKeyboardButton(text="Group Performance", callback_data="scores_groups"),
            ],
        ]
    )
