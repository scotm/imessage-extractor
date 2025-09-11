import click
import sqlite3
import logging
from typing import List, Dict, Any, Optional
from .database import IMessageDatabase


def setup_logging(verbose: bool):
    """Set up logging based on verbose flag.

    Args:
        verbose: If True, set logging level to DEBUG, otherwise to WARNING
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING)
    return logging.getLogger(__name__)


def validate_chat_candidates(candidates: List[Dict[str, Any]], logger) -> bool:
    """Validate that chat candidates have all required keys.

    Args:
        candidates: List of chat dictionaries from the database
        logger: Logger instance for verbose output

    Returns:
        True if all candidates are valid, False otherwise
    """
    required_keys = ["rowid", "display_name", "chat_identifier", "participants"]
    for i, chat in enumerate(candidates):
        missing_keys = [key for key in required_keys if key not in chat]
        if missing_keys:
            logger.error(f"Candidate {i} missing keys: {missing_keys}")
            click.echo(f"Error: Chat data structure is incomplete. Missing keys: {missing_keys}", err=True)
            return False
    return True


def display_chat_selection(candidates: List[Dict[str, Any]]) -> None:
    """Display chat options for user selection.

    Args:
        candidates: List of chat dictionaries to display
    """
    click.echo("Multiple chats found. Please select one:")
    for i, chat in enumerate(candidates):
        display_name = chat['display_name'] or chat['chat_identifier']
        participants = chat['participants'] or "Unknown participants"
        click.echo(f"{i+1}. {display_name} - Participants: {participants}")


def get_user_chat_choice(candidates: List[Dict[str, Any]]) -> Optional[int]:
    """Get user's chat selection choice.

    Args:
        candidates: List of chat candidates

    Returns:
        Selected index (0-based) or None if invalid choice
    """
    choice = click.prompt("Enter the number of the chat to export", type=int)
    if choice < 1 or choice > len(candidates):
        click.echo("Invalid choice.")
        return None
    return choice - 1


def select_chat_from_candidates(candidates: List[Dict[str, Any]], logger) -> Optional[Dict[str, Any]]:
    """Select a chat from candidates, prompting user if multiple options exist.

    Args:
        candidates: List of chat dictionaries from the database
        logger: Logger instance for verbose output

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

    chat_name = selected_chat["display_name"] or selected_chat["chat_identifier"]
    logger.debug(f"Selected chat: {chat_name} with rowid: {selected_chat['rowid']}")
    click.echo(f"Exporting chat: {chat_name}")

    return selected_chat


def handle_permission_error(e: Exception, logger) -> int:
    """Handle permission errors with helpful guidance.

    Args:
        e: The permission error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    click.echo(f"Error: {e}", err=True)
    logger.error(f"Permission error: {e}")
    click.echo("\nTo resolve this issue:", err=True)
    click.echo("1. Open System Settings > Privacy & Security > Full Disk Access", err=True)
    click.echo("2. Add your terminal application (Terminal, iTerm, etc.) to the list", err=True)
    click.echo("3. Restart your terminal application", err=True)
    click.echo("4. Quit the Messages app completely", err=True)
    click.echo("5. Try running the command again", err=True)
    return 1


def handle_database_error(e: sqlite3.Error, logger) -> int:
    """Handle database errors.

    Args:
        e: The database error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    click.echo(f"Database error: {e}", err=True)
    logger.error(f"Database error: {e}")
    return 1


def handle_key_error(e: KeyError, logger) -> int:
    """Handle key errors in data structures.

    Args:
        e: The key error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    click.echo(f"Data structure error: Missing key {e}", err=True)
    logger.error(f"KeyError in data structure: {e}", exc_info=True)
    return 1


def handle_unexpected_error(e: Exception, logger) -> int:
    """Handle unexpected errors.

    Args:
        e: The unexpected error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    click.echo(f"Unexpected error: {e}", err=True)
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return 1


@click.group()
@click.version_option()
def cli():
    """Parse and Extract iMessage Conversations.

    A command-line tool to extract iMessage conversations from the macOS Messages database.
    Provides functionality to export individual chats to CSV or all chats to JSON format.
    """


@cli.command(name="export-chat")
@click.argument("participant")
@click.option("-o", "--output", type=click.Path(), help="Output CSV file path", default="imessage_chat.csv")
@click.option("-d", "--db-path", type=click.Path(exists=True), help="Path to chat.db file")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def export_chat_command(participant, output, db_path, verbose):
    """Export a chat conversation with a specific participant to CSV.

    Extracts messages from a chat thread containing the specified participant
    and saves them to a CSV file with detailed metadata.

    If multiple chats match the participant identifier, you will be prompted to
    select which chat to export.

    Args:
        participant: A substring of the phone number or email of the participant
                    (e.g. "+44" or "john@example.com")
        output: Path to the output CSV file. Defaults to "imessage_chat.csv"
        db_path: Optional path to chat.db file if not using the default location
        verbose: Enable verbose logging for debugging

    Example:
        imessage-extractor export-chat "+1234567890" -o my_conversation.csv
    """
    logger = setup_logging(verbose)

    if verbose:
        logger.debug(f"Starting export-chat command with participant: {participant}, output: {output}, db_path: {db_path}")

    try:
        db = IMessageDatabase(db_path)
        if verbose:
            logger.debug(f"Connected to database: {db.db_path}")

        # Find chats matching the participant
        candidates = db.find_chat_by_participant(participant)
        if verbose:
            logger.debug(f"Found {len(candidates)} chat candidates")

        if not candidates:
            click.echo("No chats found with the specified participant.")
            return

        # Validate candidates structure
        if not validate_chat_candidates(candidates, logger):
            return 1

        # Select chat to export
        selected_chat = select_chat_from_candidates(candidates, logger)
        if selected_chat is None:
            return 1

        # Export the chat
        db.export_chat_to_csv(selected_chat["rowid"], output)
        click.echo(f"Chat exported to {output}")

        if verbose:
            logger.debug("Export completed successfully")

    except PermissionError as e:
        return handle_permission_error(e, logger)
    except sqlite3.OperationalError as e:
        return handle_database_error(e, logger)
    except sqlite3.Error as e:
        return handle_database_error(e, logger)
    except KeyError as e:
        return handle_key_error(e, logger)
    except Exception as e:
        return handle_unexpected_error(e, logger)


@cli.command(name="export-all")
@click.option("-o", "--output", type=click.Path(), help="Output JSON file path", default="imessage_all.json")
@click.option("-d", "--db-path", type=click.Path(exists=True), help="Path to chat.db file")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def export_all_command(output, db_path, verbose):
    """Export all chat conversations to JSON.

    Extracts all messages from all chat threads and saves them to a JSON file.
    Messages are grouped by conversation thread with complete metadata.

    Chats are sorted by most recent activity, with the most recently active
    threads appearing first in the output.

    Args:
        output: Path to the output JSON file. Defaults to "imessage_all.json"
        db_path: Optional path to chat.db file if not using the default location
        verbose: Enable verbose logging for debugging

    Example:
        imessage-extractor export-all -o all_conversations.json
    """
    logger = setup_logging(verbose)

    if verbose:
        logger.debug(f"Starting export-all command with output: {output}, db_path: {db_path}")

    try:
        db = IMessageDatabase(db_path)
        if verbose:
            logger.debug(f"Connected to database: {db.db_path}")

        # Export all chats
        db.export_all_chats_to_json(output)
        click.echo(f"All chats exported to {output}")

        if verbose:
            logger.debug("Export completed successfully")

    except PermissionError as e:
        return handle_permission_error(e, logger)
    except sqlite3.OperationalError as e:
        return handle_database_error(e, logger)
    except sqlite3.Error as e:
        return handle_database_error(e, logger)
    except Exception as e:
        return handle_unexpected_error(e, logger)


@cli.command(name="list-chats")
@click.argument("participant")
@click.option("-d", "--db-path", type=click.Path(exists=True), help="Path to chat.db file")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def list_chats_command(participant, db_path, verbose):
    """List all chats with a specific participant.

    Displays information about all chat threads that include a participant
    whose identifier (phone number or email) contains the provided substring.

    Args:
        participant: A substring of the phone number or email of the participant
                    (e.g. "+44" or "john@example.com")
        db_path: Optional path to chat.db file if not using the default location
        verbose: Enable verbose logging for debugging

    Example:
        imessage-extractor list-chats "+1234567890"
    """
    logger = setup_logging(verbose)

    if verbose:
        logger.debug(f"Starting list-chats command with participant: {participant}, db_path: {db_path}")

    try:
        db = IMessageDatabase(db_path)
        if verbose:
            logger.debug(f"Connected to database: {db.db_path}")

        # Find chats matching the participant
        candidates = db.find_chat_by_participant(participant)
        if verbose:
            logger.debug(f"Found {len(candidates)} chat candidates")

        if not candidates:
            click.echo("No chats found with the specified participant.")
            return

        # Validate candidates structure
        if not validate_chat_candidates(candidates, logger):
            return 1

        click.echo(f"Found {len(candidates)} chat(s):")
        for i, chat in enumerate(candidates):
            display_name = chat["display_name"] or "Unnamed chat"
            participants = chat["participants"] or "No participants found"
            click.echo(f"{i+1}. {display_name}")
            click.echo(f"   Identifier: {chat['chat_identifier']}")
            click.echo(f"   Participants: {participants}")
            click.echo()

        if verbose:
            logger.debug("List chats completed successfully")

    except PermissionError as e:
        return handle_permission_error(e, logger)
    except sqlite3.OperationalError as e:
        return handle_database_error(e, logger)
    except sqlite3.Error as e:
        return handle_database_error(e, logger)
    except KeyError as e:
        return handle_key_error(e, logger)
    except Exception as e:
        return handle_unexpected_error(e, logger)
