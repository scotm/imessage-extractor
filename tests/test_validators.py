"""Tests for validator utility functions."""

import os
import pytest

from imessage_extractor.validators import (
    validate_chat_candidates,
    validate_user_choice,
    validate_file_path,
    validate_participant_identifier,
    validate_database_row,
    validate_output_format,
    validate_positive_integer,
)
from imessage_extractor.exceptions import (
    MissingRequiredFieldError,
    InvalidChoiceError,
    InvalidDataFormatError,
)
from imessage_extractor.constants import REQUIRED_CHAT_KEYS


def test_validate_chat_candidates_valid():
    """Ensure validate_chat_candidates returns True for valid input."""
    candidates = [{key: 1 for key in REQUIRED_CHAT_KEYS}]
    assert validate_chat_candidates(candidates) is True


def test_validate_chat_candidates_missing():
    """Missing required keys should raise MissingRequiredFieldError."""
    candidates = [{"rowid": 1, "display_name": "name", "chat_identifier": "id"}]
    with pytest.raises(MissingRequiredFieldError):
        validate_chat_candidates(candidates)


def test_validate_user_choice():
    """validate_user_choice converts to zero-based index and enforces bounds."""
    assert validate_user_choice(1, 3) == 0
    with pytest.raises(InvalidChoiceError):
        validate_user_choice(0, 3)
    with pytest.raises(InvalidChoiceError):
        validate_user_choice(4, 3)


def test_validate_file_path(tmp_path):
    """validate_file_path expands paths and checks existence."""
    file = tmp_path / "file.txt"
    file.write_text("data")
    assert validate_file_path(str(file), must_exist=True) == str(file)
    with pytest.raises(FileNotFoundError):
        validate_file_path(str(file.with_name("missing.txt")), must_exist=True)
    with pytest.raises(InvalidDataFormatError):
        validate_file_path("", must_exist=False)


def test_validate_participant_identifier():
    """Participant identifiers must contain alphanumeric characters."""
    assert validate_participant_identifier("user@example.com") == "user@example.com"
    with pytest.raises(InvalidDataFormatError):
        validate_participant_identifier("@@@")


def test_validate_database_row():
    """validate_database_row checks for presence of required keys."""
    row = {"id": 1, "name": "Alice"}
    assert validate_database_row(row, ["id", "name"]) == row
    with pytest.raises(MissingRequiredFieldError):
        validate_database_row({"id": 1}, ["id", "name"])


def test_validate_output_format():
    """validate_output_format ensures file extension is allowed."""
    path = validate_output_format("output.csv", ["csv", "json"])
    assert path.endswith("output.csv")
    with pytest.raises(InvalidDataFormatError):
        validate_output_format("output.txt", ["csv", "json"])


def test_validate_positive_integer():
    """validate_positive_integer enforces positive integers."""
    assert validate_positive_integer("5", "test") == 5
    with pytest.raises(InvalidDataFormatError):
        validate_positive_integer("-1", "test")
    with pytest.raises(InvalidDataFormatError):
        validate_positive_integer("abc", "test")
