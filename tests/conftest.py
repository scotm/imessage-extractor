import os
import sqlite3
import sys
import pytest

# Ensure package root is importable when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from imessage_extractor.database import IMessageDatabase


@pytest.fixture
def mock_imessage_db(monkeypatch):
    """Create an in-memory iMessage database with sample data."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Create tables
    cur.executescript(
        """
        CREATE TABLE chat (
            rowid INTEGER PRIMARY KEY,
            guid TEXT,
            chat_identifier TEXT,
            display_name TEXT
        );
        CREATE TABLE handle (
            rowid INTEGER PRIMARY KEY,
            id TEXT
        );
        CREATE TABLE chat_handle_join (
            chat_id INTEGER,
            handle_id INTEGER
        );
        CREATE TABLE message (
            rowid INTEGER PRIMARY KEY,
            text TEXT,
            attributedBody BLOB,
            is_from_me INTEGER,
            handle_id INTEGER,
            service TEXT,
            date INTEGER,
            date_read INTEGER,
            date_delivered INTEGER,
            associated_message_guid TEXT,
            thread_originator_guid TEXT,
            item_type INTEGER
        );
        CREATE TABLE chat_message_join (
            chat_id INTEGER,
            message_id INTEGER
        );
        CREATE TABLE attachment (
            rowid INTEGER PRIMARY KEY,
            filename TEXT,
            transfer_name TEXT,
            mime_type TEXT
        );
        CREATE TABLE message_attachment_join (
            message_id INTEGER,
            attachment_id INTEGER
        );
        """
    )

    # Insert sample data
    cur.executescript(
        """
        INSERT INTO chat(rowid, guid, chat_identifier, display_name)
        VALUES (1, 'chat-guid', 'chat-identifier', 'Sample Chat');

        INSERT INTO handle(rowid, id)
        VALUES (1, 'user@example.com');

        INSERT INTO chat_handle_join(chat_id, handle_id)
        VALUES (1, 1);

        INSERT INTO message(rowid, text, attributedBody, is_from_me, handle_id, service, date,
                            date_read, date_delivered, associated_message_guid, thread_originator_guid, item_type)
        VALUES (1, 'Hello', NULL, 1, 1, 'iMessage', 0, NULL, NULL, NULL, NULL, 0);

        INSERT INTO chat_message_join(chat_id, message_id)
        VALUES (1, 1);

        INSERT INTO attachment(rowid, filename, transfer_name, mime_type)
        VALUES (1, '/path/to/file.txt', 'file.txt', 'text/plain');

        INSERT INTO message_attachment_join(message_id, attachment_id)
        VALUES (1, 1);
        """
    )
    conn.commit()

    db = IMessageDatabase(db_path=":memory:")
    monkeypatch.setattr(IMessageDatabase, "get_connection", lambda self: conn)

    yield db

    conn.close()
