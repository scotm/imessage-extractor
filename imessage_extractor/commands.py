"""Command implementations for the iMessage Extractor application."""

import logging
from typing import Optional

from .constants import DEFAULT_CSV_FILENAME, DEFAULT_JSON_FILENAME
from .database import IMessageDatabase
from .error_handlers import handle_error_with_fallback
from .exceptions import NoChatsFoundError
from .ui import (
    select_chat_from_candidates,
    display_chat_info,
    display_export_success,
    display_chat_list,
)
from .validators import (
    validate_chat_candidates,
    validate_file_path,
    validate_participant_identifier,
)


def setup_logging(verbose: bool) -> logging.Logger:
    """Set up logging based on verbose flag.

    Args:
        verbose: If True, set logging level to DEBUG, otherwise to WARNING

    Returns:
        Logger instance
    """
    from .constants import LOG_FORMAT

    if verbose:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.WARNING)
    return logging.getLogger(__name__)


def export_chat_command(
    participant: str,
    output: Optional[str] = None,
    db_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """Export a chat conversation with a specific participant to CSV.

    Args:
        participant: A substring of the phone number or email of the participant
        output: Path to the output CSV file. Defaults to DEFAULT_CSV_FILENAME
        db_path: Optional path to chat.db file if not using the default location
        verbose: Enable verbose logging for debugging

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger = setup_logging(verbose)

    try:
        if verbose:
            logger.debug(f"Starting export-chat command with participant: {participant}, output: {output}, db_path: {db_path}")

        # Validate inputs
        validated_participant = validate_participant_identifier(participant)
        validated_output = validate_file_path(output or DEFAULT_CSV_FILENAME)

        # Connect to database
        db = IMessageDatabase(db_path)
        if verbose:
            logger.debug(f"Connected to database: {db.db_path}")

        # Find chats matching the participant
        candidates = db.find_chat_by_participant(validated_participant)
        if verbose:
            logger.debug(f"Found {len(candidates)} chat candidates")

        if not candidates:
            raise NoChatsFoundError(validated_participant)

        # Validate candidates structure
        validate_chat_candidates(candidates)

        # Select chat to export
        selected_chat = select_chat_from_candidates(candidates)
        if selected_chat is None:
            return 1

        display_chat_info(selected_chat)

        # Export the chat
        db.export_chat_to_csv(selected_chat["rowid"], validated_output)
        display_export_success(validated_output)

        if verbose:
            logger.debug("Export completed successfully")

        return 0

    except Exception as e:
        return handle_error_with_fallback(e, logger)


def export_all_command(
    output: Optional[str] = None,
    db_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """Export all chat conversations to JSON.

    Args:
        output: Path to the output JSON file. Defaults to DEFAULT_JSON_FILENAME
        db_path: Optional path to chat.db file if not using the default location
        verbose: Enable verbose logging for debugging

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger = setup_logging(verbose)

    try:
        if verbose:
            logger.debug(f"Starting export-all command with output: {output}, db_path: {db_path}")

        # Validate inputs
        validated_output = validate_file_path(output or DEFAULT_JSON_FILENAME)

        # Connect to database
        db = IMessageDatabase(db_path)
        if verbose:
            logger.debug(f"Connected to database: {db.db_path}")

        # Export all chats
        db.export_all_chats_to_json(validated_output)
        display_export_success(validated_output)

        if verbose:
            logger.debug("Export completed successfully")

        return 0

    except Exception as e:
        return handle_error_with_fallback(e, logger)


def list_chats_command(
    participant: str,
    db_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """List all chats with a specific participant.

    Args:
        participant: A substring of the phone number or email of the participant
        db_path: Optional path to chat.db file if not using the default location
        verbose: Enable verbose logging for debugging

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger = setup_logging(verbose)

    try:
        if verbose:
            logger.debug(f"Starting list-chats command with participant: {participant}, db_path: {db_path}")

        # Validate inputs
        validated_participant = validate_participant_identifier(participant)

        # Connect to database
        db = IMessageDatabase(db_path)
        if verbose:
            logger.debug(f"Connected to database: {db.db_path}")

        # Find chats matching the participant
        candidates = db.find_chat_by_participant(validated_participant)
        if verbose:
            logger.debug(f"Found {len(candidates)} chat candidates")

        if not candidates:
            raise NoChatsFoundError(validated_participant)

        # Validate candidates structure
        validate_chat_candidates(candidates)

        # Display chat list
        display_chat_list(candidates)

        if verbose:
            logger.debug("List chats completed successfully")

        return 0

    except Exception as e:
        return handle_error_with_fallback(e, logger)
