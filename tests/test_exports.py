"""Tests for database export functions."""

import csv
import json


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
