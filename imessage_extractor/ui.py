
"""User interface functions for the iMessage Extractor application."""

import click
from typing import List, Dict, Any, Optional

from .constants import (
    COL_CHAT_IDENTIFIER,
    COL_DISPLAY_NAME,
    COL_PARTICIPANTS,
    ERR_INVALID_CHOICE,
    ERR_NO_CHATS_FOUND,
)
from .validators import validate_user_choice


def display_chat_selection(candidates: List[Dict[str, Any]]) -> None:
    """Display chat options for user selection.

    Args:
        candidates: List of chat dictionaries to display
    """
    click.echo("Multiple chats found. Please select one:")
    for i, chat in enumerate(candidates):
        display_name = chat.get(COL_DISPLAY_NAME) or chat.get(COL_CHAT_IDENTIFIER, "Unknown")
        participants = chat.get(COL_PARTICIPANTS) or "Unknown participants"
        click.echo(f"{i+1}. {display_name} - Participants: {participants}")


def get_user_chat_choice(candidates: List[Dict[str, Any]]) -> Optional[int]:
    """Get user's chat selection choice.

    Args:
        candidates: List of chat candidates

    Returns:
        Selected index (0-based) or None if invalid choice
    """
    try:
        choice = click.prompt("Enter the number of the chat to export", type=int)
        return validate_user_choice(choice, len(candidates))
    except Exception:
        click.echo(ERR_INVALID_CHOICE)
        return None


def select_chat_from_candidates(candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Select a chat from candidates, prompting user if multiple options exist.

    Args:
        candidates: List of chat dictionaries from the database

    Returns:
        Selected chat dictionary or None if selection failed
    """
    if len(candidates) > 1:
        display_chat_selection(candidates)
        choice_index = get_user_chat_choice(candidates)
        if choice_index is None:
            return None
        selected_chat = candidates[choice_index]
    else:
        selected_chat = candidates[0]

    return selected_chat


def display_chat_info(selected_chat: Dict[str, Any]) -> None:
    """Display information about the selected chat.

    Args:
        selected_chat: Selected chat dictionary
    """
    chat_name = selected_chat.get(COL_DISPLAY_NAME) or selected_chat.get(COL_CHAT_IDENTIFIER, "Unknown")
    click.echo(f"Exporting chat: {chat_name}")


def display_export_success(output_path: str, chat_count: Optional[int] = None) -> None:
    """Display successful export message.

    Args:
        output_path: Path to the exported file
        chat_count: Number of chats exported (for JSON export)
    """
    if chat_count is not None:
        click.echo(f"Exported {chat_count} chats to {output_path}")
    else:
        click.echo(f"Chat exported to {output_path}")


def display_chat_list(candidates: List[Dict[str, Any]]) -> None:
    """Display list of all chats with a specific participant.

    Args:
        candidates: List of chat dictionaries
    """
    if not candidates:
        click.echo(ERR_NO_CHATS_FOUND)
        return

    click.echo(f"Found {len(candidates)} chat(s):")
    for i, chat in enumerate(candidates):
        display_name = chat.get(COL_DISPLAY_NAME) or "Unnamed chat"
        participants = chat.get(COL_PARTICIPANTS) or "No participants found"
        click.echo(f"{i+1}. {display_name}")
        click.echo(f"   Identifier: {chat.get(COL_CHAT_IDENTIFIER, 'N/A')}")
        click.echo(f"   Participants: {participants}")
        click.echo()


def display_progress(current: int, total: int, operation: str = "Processing") -> None:
    """Display progress information.

    Args:
        current: Current item being processed
        total: Total number of items
        operation: Description of the operation
    """
    percentage = (current / total) * 100 if total > 0 else 0
    click.echo(f"{operation}: {current}/{total} ({percentage:.1f}%)")


def display_error_message(message: str, details: Optional[str] = None) -> None:
    """Display error message to user.

    Args:
        message: Main error message
        details: Optional additional details
    """
    click.echo(f"Error: {message}", err=True)
    if details:
        click.echo(f"Details: {details}", err=True)


def display_warning_message(message: str) -> None:
    """Display warning message to user.

    Args:
        message: Warning message
    """
    click.echo(f"Warning: {message}", err=True)


def display_info_message(message: str) -> None:
    """Display informational message to user.

    Args:
        message: Information message
    """
    click.echo(message)


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user to confirm an action.

    Args:
        message: Confirmation message
        default: Default value if user just presses Enter

    Returns:
        True if user confirms, False otherwise
    """
    return click.confirm(message, default=default)


def prompt_for_value(message: str, default: Optional[str] = None, hide_input: bool = False) -> str:
    """Prompt user for a value.

    Args:
        message: Prompt message
        default: Default value
        hide_input: Whether to hide input (for passwords)

    Returns:
        User input value
    """
    if hide_input:
        return click.prompt(message, default=default, hide_input=True)
    else:
        return click.prompt(message, default=default)
