
"""Custom exception classes for the iMessage Extractor application."""

from typing import List, Optional


class IMessageExtractorError(Exception):
    """Base exception class for all iMessage Extractor errors."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class DatabaseError(IMessageExtractorError):
    """Base class for database-related errors."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when unable to connect to the database."""

    def __init__(self, path: str, original_error: Optional[Exception] = None) -> None:
        self.path = path
        self.original_error = original_error
        message = f"Failed to connect to database at {path}"
        details = str(original_error) if original_error else None
        super().__init__(message, details)


class DatabasePermissionError(DatabaseConnectionError):
    """Raised when permission is denied accessing the database."""

    def __init__(self, path: str) -> None:
        message = f"Permission denied accessing database at {path}"
        details = (
            "Please ensure you have granted Full Disk Access to your terminal application "
            "in System Settings > Privacy & Security > Full Disk Access."
        )
        super().__init__(path)
        self.message = message
        self.details = details


class DatabaseLockedError(DatabaseConnectionError):
    """Raised when the database is locked."""

    def __init__(self, path: str) -> None:
        message = f"Database is locked: {path}"
        details = "Please ensure the Messages app is completely quit before running this tool."
        super().__init__(path)
        self.message = message
        self.details = details


class DatabaseNotFoundError(DatabaseConnectionError):
    """Raised when the database file is not found."""

    def __init__(self, path: str) -> None:
        message = f"Database file not found: {path}"
        details = "Please check that the path is correct and the file exists."
        super().__init__(path)
        self.message = message
        self.details = details


class ParsingError(IMessageExtractorError):
    """Base class for parsing-related errors."""
    pass


class TextExtractionError(ParsingError):
    """Raised when text extraction from attributedBody fails."""

    def __init__(self, message_id: Optional[int] = None, details: Optional[str] = None) -> None:
        self.message_id = message_id
        if message_id:
            message = f"Failed to extract text from message {message_id}"
        else:
            message = "Failed to extract text from attributedBody data"
        super().__init__(message, details)


class InvalidDataFormatError(ParsingError):
    """Raised when data format is invalid or unexpected."""

    def __init__(self, data_type: str, expected_format: str, actual_data: Optional[str] = None) -> None:
        self.data_type = data_type
        self.expected_format = expected_format
        self.actual_data = actual_data
        message = f"Invalid {data_type} format. Expected: {expected_format}"
        details = f"Actual data: {actual_data}" if actual_data else None
        super().__init__(message, details)


class ValidationError(IMessageExtractorError):
    """Base class for validation-related errors."""
    pass


class MissingRequiredFieldError(ValidationError):
    """Raised when required fields are missing from data structures."""

    def __init__(self, missing_fields: List[str], data_type: str = "data structure") -> None:
        self.missing_fields = missing_fields
        self.data_type = data_type
        message = f"{data_type.title()} is incomplete. Missing required fields: {', '.join(missing_fields)}"
        super().__init__(message)


class InvalidChoiceError(ValidationError):
    """Raised when user makes an invalid selection choice."""

    def __init__(self, choice: int, valid_range: tuple[int, int]) -> None:
        self.choice = choice
        self.valid_range = valid_range
        message = f"Invalid choice: {choice}. Please select a number between {valid_range[0]} and {valid_range[1]}."
        super().__init__(message)


class FileOperationError(IMessageExtractorError):
    """Base class for file operation errors."""
    pass


class FileWriteError(FileOperationError):
    """Raised when writing to a file fails."""

    def __init__(self, file_path: str, original_error: Optional[Exception] = None) -> None:
        self.file_path = file_path
        self.original_error = original_error
        message = f"Failed to write to file: {file_path}"
        details = str(original_error) if original_error else None
        super().__init__(message, details)


class FileReadError(FileOperationError):
    """Raised when reading from a file fails."""

    def __init__(self, file_path: str, original_error: Optional[Exception] = None) -> None:
        self.file_path = file_path
        self.original_error = original_error
        message = f"Failed to read from file: {file_path}"
        details = str(original_error) if original_error else None
        super().__init__(message, details)


class UserInputError(IMessageExtractorError):
    """Base class for user input-related errors."""
    pass


class NoChatsFoundError(UserInputError):
    """Raised when no chats are found for the given participant."""

    def __init__(self, participant: str) -> None:
        self.participant = participant
        message = f"No chats found with the specified participant: {participant}"
        super().__init__(message)


class ConfigurationError(IMessageExtractorError):
    """Raised when there are configuration-related errors."""
    pass


class UnsupportedOperationError(IMessageExtractorError):
    """Raised when an unsupported operation is attempted."""

    def __init__(self, operation: str, reason: Optional[str] = None) -> None:
        self.operation = operation
        self.reason = reason
        message = f"Unsupported operation: {operation}"
        details = reason
        super().__init__(message, details)
