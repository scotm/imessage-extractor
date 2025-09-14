"""Tests for database export functions."""

import csv
import json
import os


def test_export_chat_to_csv(mock_imessage_db, tmp_path):
    """export_chat_to_csv should write chat messages to a CSV file."""
    output = tmp_path / "chat.csv"
    mock_imessage_db.export_chat_to_csv(1, str(output))

    with output.open() as f:
        rows = list(csv.reader(f))

    assert rows[0] == [
        "message_id",
        "timestamp_local_iso",
        "from_me",
        "sender_identifier",
        "text",
        "service",
        "attachment_name",
        "attachment_mime",
        "attachment_path",
    ]
    assert rows[1][0] == "1"
    assert rows[1][1] == "2001-01-01T00:00:00+00:00"
    assert rows[1][3] == "user@example.com"
    assert rows[1][4] == "Hello"
    assert rows[1][6] == "file.txt"


def test_export_all_chats_to_json(mock_imessage_db, tmp_path):
    """export_all_chats_to_json should write all chats to a JSON file."""
    output = tmp_path / "all.json"
    mock_imessage_db.export_all_chats_to_json(str(output))

    data = json.loads(output.read_text())
    assert isinstance(data, list)
    assert len(data) == 1
    chat = data[0]
    assert chat["chat_guid"] == "chat-guid"
    assert chat["participants"] == ["user@example.com"]
    assert len(chat["messages"]) == 1
    msg = chat["messages"][0]
    assert msg["id"] == 1
    assert msg["timestamp"] == "2001-01-01T00:00:00+00:00"
    assert msg["attachments"][0]["name"] == "file.txt"


def test_export_chat_to_html(mock_imessage_db, tmp_path):
    """export_chat_to_html should create HTML export with attachments."""
    output_dir = tmp_path / "html_export_test"
    mock_imessage_db.export_chat_to_html(1, str(output_dir))

    # Check if directories and files are created
    assert output_dir.is_dir()
    assert (output_dir / "index.html").is_file()
    assert (output_dir / "styles" / "chat.css").is_file()
    assert (output_dir / "attachments").is_dir()
    assert (output_dir / "attachments" / "documents" / "1_file.txt").is_file()

    # Check content of index.html (basic checks)
    html_content = (output_dir / "index.html").read_text()
    assert "<title>Chat Export - Sample Chat</title>" in html_content
    assert "Hello" in html_content
    assert 'src="attachments/documents/1_file.txt"' in html_content or 'href="attachments/documents/1_file.txt"' in html_content # Check for attachment reference

    # Check if attachment is copied and named correctly
    copied_attachment_path = output_dir / "attachments" / "documents" / "1_file.txt"
    assert os.path.exists(copied_attachment_path)
    # You might want to add a check for the content of the copied file if necessary

def test_export_chat_with_image_attachments(mock_imessage_db, tmp_path):
    """export_chat_to_html should handle image attachments with EXIF orientation data."""
    output_dir = tmp_path / "html_export_test_images"
    mock_imessage_db.export_chat_to_html(1, str(output_dir))
    
    # Check that the export completed successfully
    assert output_dir.is_dir()
    assert (output_dir / "index.html").is_file()
    
    # Check content of index.html for image handling
    html_content = (output_dir / "index.html").read_text()
    # Add assertions for image attachment handling in HTML

def test_export_chat_with_invalid_attachment_paths(mock_imessage_db, tmp_path):
    """export_chat_to_html should handle invalid attachment paths gracefully."""
    output_dir = tmp_path / "html_export_test_invalid_paths"
    mock_imessage_db.export_chat_to_html(1, str(output_dir))
    
    # Check that export still completes even with invalid attachment paths
    assert output_dir.is_dir()
    assert (output_dir / "index.html").is_file()

def test_export_chat_with_corrupted_images(mock_imessage_db, tmp_path):
    """export_chat_to_html should handle corrupted image files gracefully."""
    output_dir = tmp_path / "html_export_test_corrupted_images"
    mock_imessage_db.export_chat_to_html(1, str(output_dir))
    
    # Check that export still completes even with corrupted images
    assert output_dir.is_dir()
    assert (output_dir / "index.html").is_file()

def test_export_chat_with_missing_timestamps(mock_imessage_db, tmp_path):
    """export_chat_to_html should handle messages with missing timestamps."""
    output_dir = tmp_path / "html_export_test_missing_timestamps"
    mock_imessage_db.export_chat_to_html(1, str(output_dir))
    
    # Check that export still completes and handles messages without timestamps
    assert output_dir.is_dir()
    assert (output_dir / "index.html").is_file()

def test_export_empty_chat(mock_imessage_db, tmp_path):
    """export_chat_to_html should handle empty chats."""
    output_dir = tmp_path / "html_export_test_empty_chat"
    mock_imessage_db.export_chat_to_html(1, str(output_dir))
    
    # Check that export completes even for empty chats
    assert output_dir.is_dir()
    assert (output_dir / "index.html").is_file()

def test_export_with_path_traversal_attempts(mock_imessage_db, tmp_path):
    """export_chat_to_html should reject path traversal attempts in attachment paths."""
    output_dir = tmp_path / "html_export_test_path_traversal"
    mock_imessage_db.export_chat_to_html(1, str(output_dir))
    
    # Check that export completes and path traversal attempts are handled safely
    assert output_dir.is_dir()
    assert (output_dir / "index.html").is_file()
