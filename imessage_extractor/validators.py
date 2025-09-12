
"""Input validation functions for the iMessage Extractor application."""

import os
from typing import Dict, List, Any, Optional

from .constants import REQUIRED_CHAT_KEYS
from .exceptions import (
    MissingRequiredFieldError,
    InvalidChoiceError,
    InvalidDataFormatError,
)


def validate_chat_candidates(candidates: List[Dict[str, Any]]) -> bool:
    """Validate that chat candidates have all required keys.

    Args:
        candidates: List of chat dictionaries from the database

    Returns:
        True if all candidates are valid, False otherwise

    Raises:
        MissingRequiredFieldError: If any candidate is missing required keys
    """
    for i, chat in enumerate(candidates):
        missing_keys = [key for key in REQUIRED_CHAT_KEYS if key not in chat]
        if missing_keys:
            raise MissingRequiredFieldError(missing_keys, f"Chat candidate {i}")
    return True


def validate_user_choice(choice: int, max_valid_choice: int) -> int:
    """Validate user's chat selection choice.

    Args:
        choice: The user's choice (1-based)
        max_valid_choice: Maximum valid choice number

    Returns:
        Validated choice (0-based)

    Raises:
        InvalidChoiceError: If choice is invalid
    """
    if choice < 1 or choice > max_valid_choice:
        raise InvalidChoiceError(choice, (1, max_valid_choice))

    return choice - 1  # Convert to 0-based indexing


def validate_file_path(file_path: str, must_exist: bool = False) -> str:
    """Validate and expand file path.

    Args:
        file_path: File path to validate
        must_exist: Whether the file must exist

    Returns:
        Expanded absolute file path

    Raises:
        FileNotFoundError: If must_exist is True and file doesn't exist
        InvalidDataFormatError: If file_path is empty or invalid
    """
    if not file_path or not isinstance(file_path, str):
        raise InvalidDataFormatError("file path", "non-empty string", str(file_path))

    expanded_path = os.path.expanduser(file_path)

    if must_exist and not os.path.exists(expanded_path):
        raise FileNotFoundError(f"File not found: {expanded_path}")

    return expanded_path


def validate_participant_identifier(participant: str) -> str:
    """Validate participant identifier.

    Args:
        participant: Participant identifier to validate

    Returns:
        Validated participant identifier

    Raises:
        InvalidDataFormatError: If participant identifier is invalid
    """
    if not participant or not isinstance(participant, str):
        raise InvalidDataFormatError("participant identifier", "non-empty string", str(participant))

    # Basic validation - should contain at least some alphanumeric characters
    if not any(c.isalnum() for c in participant):
        raise InvalidDataFormatError("participant identifier", "containing alphanumeric characters", participant)

    return participant.strip()


def validate_database_row(row: Dict[str, Any], required_keys: List[str]) -> Dict[str, Any]:
    """Validate that a database row contains all required keys.

    Args:
        row: Database row as dictionary
        required_keys: List of required keys

    Returns:
        Validated row dictionary

    Raises:
        MissingRequiredFieldError: If required keys are missing
    """
    missing_keys = [key for key in required_keys if key not in row]
    if missing_keys:
        raise MissingRequiredFieldError(missing_keys, "database row")

    return row


def validate_output_format(output_path: str, allowed_extensions: Optional[List[str]] = None) -> str:
    """Validate output file format.

    Args:
        output_path: Output file path
        allowed_extensions: List of allowed file extensions (without dots)

    Returns:
        Validated output path

    Raises:
        InvalidDataFormatError: If format is not supported
    """
    if allowed_extensions:
        _, ext = os.path.splitext(output_path)
        ext = ext.lower().lstrip('.')
        if ext not in allowed_extensions:
            raise InvalidDataFormatError(
                "output file format",
                f"one of: {', '.join(allowed_extensions)}",
                ext
            )

    return validate_file_path(output_path)


def validate_positive_integer(value: Any, field_name: str) -> int:
    """Validate that a value is a positive integer.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        Validated positive integer

    Raises:
        InvalidDataFormatError: If value is not a positive integer
    """
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValueError()
        return int_value
    except (ValueError, TypeError):
        raise InvalidDataFormatError(field_name, "positive integer", str(value))
