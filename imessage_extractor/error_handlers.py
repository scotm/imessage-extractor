
"""Error handling functions for the iMessage Extractor application."""

import logging
import sys
from typing import Optional

from .constants import GUIDANCE_PERMISSION_ERROR
from .exceptions import (
    DatabaseError,
    DatabasePermissionError,
    DatabaseLockedError,
    DatabaseNotFoundError,
    FileOperationError,
    FileWriteError,
    FileReadError,
    IMessageExtractorError,
    ValidationError,
    MissingRequiredFieldError,
    InvalidChoiceError,
    NoChatsFoundError,
    TextExtractionError,
)


def handle_permission_error(e: Exception, logger: logging.Logger) -> int:
    """Handle permission errors with helpful guidance.

    Args:
        e: The permission error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    logger.error(f"Permission error: {e}")
    print(f"Error: {e}", file=sys.stderr)
    print(GUIDANCE_PERMISSION_ERROR, file=sys.stderr)
    return 1


def handle_database_error(e: DatabaseError, logger: logging.Logger) -> int:
    """Handle database errors.

    Args:
        e: The database error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    logger.error(f"Database error: {e}")
    print(f"Database error: {e}", file=sys.stderr)
    return 1


def handle_file_operation_error(e: FileOperationError, logger: logging.Logger) -> int:
    """Handle file operation errors.

    Args:
        e: The file operation error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    logger.error(f"File operation error: {e}")
    print(f"Error: {e}", file=sys.stderr)
    return 1


def handle_validation_error(e: ValidationError, logger: logging.Logger) -> int:
    """Handle validation errors.

    Args:
        e: The validation error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    logger.error(f"Validation error: {e}")
    print(f"Error: {e}", file=sys.stderr)
    return 1


def handle_parsing_error(e: TextExtractionError, logger: logging.Logger) -> int:
    """Handle parsing errors.

    Args:
        e: The parsing error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    logger.error(f"Parsing error: {e}")
    print(f"Error: {e}", file=sys.stderr)
    return 1


def handle_user_input_error(e: NoChatsFoundError, logger: logging.Logger) -> int:
    """Handle user input errors.

    Args:
        e: The user input error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    logger.error(f"User input error: {e}")
    print(f"Error: {e}", file=sys.stderr)
    return 1


def handle_unexpected_error(e: Exception, logger: logging.Logger) -> int:
    """Handle unexpected errors.

    Args:
        e: The unexpected error exception
        logger: Logger instance for verbose output

    Returns:
        Exit code 1
    """
    logger.error(f"Unexpected error: {e}", exc_info=True)
    print(f"Unexpected error: {e}", file=sys.stderr)
    return 1


def handle_error_with_fallback(e: Exception, logger: logging.Logger, fallback_message: Optional[str] = None) -> int:
    """Handle errors with appropriate fallback based on exception type.

    Args:
        e: The exception to handle
        logger: Logger instance for verbose output
        fallback_message: Optional fallback message if exception type is not recognized

    Returns:
        Exit code 1
    """
    # Map exception types to their handlers
    error_handlers = {
        DatabasePermissionError: handle_permission_error,
        DatabaseLockedError: handle_database_error,
        DatabaseNotFoundError: handle_database_error,
        DatabaseError: handle_database_error,
        FileWriteError: handle_file_operation_error,
        FileReadError: handle_file_operation_error,
        FileOperationError: handle_file_operation_error,
        MissingRequiredFieldError: handle_validation_error,
        InvalidChoiceError: handle_validation_error,
        ValidationError: handle_validation_error,
        TextExtractionError: handle_parsing_error,
        NoChatsFoundError: handle_user_input_error,
        IMessageExtractorError: lambda ex, log: handle_unexpected_error(ex, log),
    }

    # Find the most specific handler for this exception type
    for exception_type, handler in error_handlers.items():
        if isinstance(e, exception_type):
            return handler(e, logger)

    # Fallback for unrecognized exceptions
    if fallback_message:
        logger.error(fallback_message)
        print(f"Error: {fallback_message}", file=sys.stderr)
    return handle_unexpected_error(e, logger)
