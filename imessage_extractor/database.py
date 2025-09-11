import os
import sqlite3
import csv
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


class IMessageDatabase:
    """A class to handle extraction of messages from the iMessage database.

    This class provides methods to connect to the iMessage SQLite database,
    query chat information, and export messages in various formats.
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the iMessage database handler.

        Args:
            db_path: Path to the chat.db file. If None, uses the default location
                    at ~/Library/Messages/chat.db

        Attributes:
            db_path (str): The path to the iMessage database file
            attachment_path (str): The path to the iMessage attachments directory
        """
        if db_path is None:
            self.db_path = os.path.expanduser("~/Library/Messages/chat.db")
        else:
            self.db_path = db_path

        self.attachment_path = os.path.expanduser("~/Library/Messages/Attachments/")

    def apple_to_unix(self, ts: Optional[int]) -> Optional[float]:
        """Convert Apple timestamp to Unix timestamp.

        Apple timestamps are measured in seconds or nanoseconds since
        2001-01-01 00:00:00 UTC, while Unix timestamps are measured
        since 1970-01-01 00:00:00 UTC. This function detects whether
        the input is in seconds or nanoseconds and converts accordingly.

        Args:
            ts: Apple timestamp (nanoseconds or seconds since 2001-01-01)

        Returns:
            Unix timestamp (seconds since 1970-01-01) or None if input is None

        Note:
            The conversion adds 978,307,200 seconds (the difference between
            Apple's epoch and Unix epoch).
        """
        if ts is None:
            return None

        # Heuristic: nanoseconds vs seconds
        if ts > 10**12:  # clearly nanoseconds
            return ts / 1e9 + 978307200
        else:
            return ts + 978307200

    def format_timestamp(self, unix_ts: Optional[float]) -> str:
        """Format Unix timestamp as ISO string in local timezone.

        Converts a Unix timestamp to an ISO 8601 formatted string in the
        local timezone. If the input is None, returns an empty string.

        Args:
            unix_ts: Unix timestamp in seconds

        Returns:
            ISO formatted timestamp string in local timezone, or empty string if None
        """
        if unix_ts is None:
            return ""
        return datetime.fromtimestamp(unix_ts, tz=timezone.utc).astimezone().isoformat()

    def get_connection(self) -> sqlite3.Connection:
        """Get a connection to the iMessage database.

        Establishes a connection to the SQLite database file with row factory
        set to sqlite3.Row for easier data access.

        Returns:
            SQLite connection object to the iMessage database

        Raises:
            sqlite3.OperationalError: If there's a permission issue or database is locked
            sqlite3.Error: If there's any other issue connecting to the database
            FileNotFoundError: If the database file doesn't exist
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.OperationalError as e:
            if "permission denied" in str(e).lower():
                raise PermissionError(
                    f"Permission denied accessing {self.db_path}. "
                    "Please ensure you have granted Full Disk Access to your terminal application "
                    "in System Settings > Privacy & Security > Full Disk Access."
                ) from e
            elif "database is locked" in str(e).lower():
                raise sqlite3.OperationalError(
                    f"Database is locked: {self.db_path}. "
                    "Please ensure the Messages app is completely quit before running this tool."
                ) from e
            else:
                raise
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Database file not found: {self.db_path}. "
                "Please check that the path is correct and the file exists."
            ) from e

    def find_chat_by_participant(self, identifier_substring: str) -> List[Dict[str, Any]]:
        """Find chats by participant identifier (phone number or email).

        Searches for chat threads that include a participant whose identifier
        (phone number or email) contains the provided substring. Joins the chat,
        chat_handle_join, and handle tables to retrieve chat information along
        with all participants.

        Args:
            identifier_substring: Partial phone number or email to search for participants

        Returns:
            List of dictionaries containing chat information:
            - rowid: Database row identifier for the chat
            - guid: Global unique identifier for the chat
            - chat_identifier: Internal identifier for the chat
            - display_name: Display name of the chat (for group chats)
            - participants: Comma-separated string of all participant identifiers
        """
        conn = self.get_connection()
        try:
            q = """
            SELECT c.rowid, c.guid, c.chat_identifier, c.display_name,
                   GROUP_CONCAT(h.id, ', ') AS participants
            FROM chat c
            JOIN chat_handle_join chj ON chj.chat_id = c.rowid
            JOIN handle h ON h.rowid = chj.handle_id
            WHERE h.id LIKE ?
            GROUP BY c.rowid, c.guid, c.chat_identifier, c.display_name
            """
            rows = conn.execute(q, (f"%{identifier_substring}%",)).fetchall()
            # Ensure all required keys are present in each row
            result = []
            for row in rows:
                row_dict = dict(row)
                # Handle the case where rowid might be returned as ROWID (uppercase)
                if "rowid" not in row_dict and "ROWID" in row_dict:
                    row_dict["rowid"] = row_dict["ROWID"]
                # Make sure all expected keys are present
                expected_keys = ["rowid", "guid", "chat_identifier", "display_name", "participants"]
                for key in expected_keys:
                    if key not in row_dict:
                        row_dict[key] = None
                result.append(row_dict)
            return result
        finally:
            conn.close()

    def export_chat_to_csv(self, chat_rowid: int, csv_path: str) -> None:
        """Export a specific chat to CSV format.

        Retrieves all messages from a specific chat thread and exports them
        to a CSV file with detailed information including timestamps, sender
        information, message content, and attachment details.

        Args:
            chat_rowid: The rowid of the chat to export from the chat table
            csv_path: Path to output CSV file

        Note:
            The messages are ordered chronologically by date and rowid.
            Attachments are included with their file paths, names, and MIME types.
        """
        conn = self.get_connection()
        try:
            q = """
            SELECT
                m.rowid AS message_id,
                m.text,
                m.attributedBody,
                m.is_from_me,
                m.handle_id,
                h.id AS handle_identifier,
                m.service,
                m.date,
                m.date_read,
                m.date_delivered,
                m.associated_message_guid,
                m.thread_originator_guid,
                m.item_type,
                a.filename AS attachment_path,
                a.transfer_name AS attachment_name,
                a.mime_type AS attachment_mime
            FROM chat_message_join cmj
            JOIN message m ON m.rowid = cmj.message_id
            LEFT JOIN handle h ON h.rowid = m.handle_id
            LEFT JOIN message_attachment_join maj ON maj.message_id = m.rowid
            LEFT JOIN attachment a ON a.rowid = maj.attachment_id
            WHERE cmj.chat_id = ?
            ORDER BY m.date ASC, m.rowid ASC
            """

            rows = conn.execute(q, (chat_rowid,)).fetchall()

            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([
                    "message_id", "timestamp_local_iso", "from_me", "sender_identifier",
                    "text", "service", "attachment_name", "attachment_mime", "attachment_path"
                ])

                for r in rows:
                    unix_ts = self.apple_to_unix(r["date"])
                    # Extract text from either text column or attributedBody
                    message_text = ""
                    if r["text"]:
                        message_text = r["text"]
                    elif r["attributedBody"]:
                        message_text = self._extract_text_from_attributed_body(r["attributedBody"])

                    w.writerow([
                        r["message_id"],
                        self.format_timestamp(unix_ts),
                        int(r["is_from_me"] or 0),
                        r["handle_identifier"] or "",
                        (message_text or "").replace("\r\n", "\n"),
                        r["service"] or "",
                        r["attachment_name"] or "",
                        r["attachment_mime"] or "",
                        r["attachment_path"] or ""
                    ])
        finally:
            conn.close()

    def export_all_chats_to_json(self, json_path: str) -> None:
        """Export all chats to JSON format grouped by thread.

        Retrieves all chat threads and their messages from the database and
        exports them to a JSON file. Messages are grouped by chat thread and
        include detailed metadata. Chats are sorted by most recent message.

        Args:
            json_path: Path to output JSON file

        Note:
            The output JSON is sorted by chat threads with the most recently
            active threads appearing first. Each message includes timestamp
            conversion and attachment information.
        """
        conn = self.get_connection()
        try:
            # Get all chats with their participants
            chats = conn.execute("""
                SELECT
                    c.rowid, c.guid, c.chat_identifier, c.display_name,
                    GROUP_CONCAT(h.id, ',') AS participants
                FROM chat c
                LEFT JOIN chat_handle_join chj ON chj.chat_id = c.rowid
                LEFT JOIN handle h ON h.rowid = chj.handle_id
                GROUP BY c.rowid, c.guid, c.chat_identifier, c.display_name
                ORDER BY c.rowid
            """).fetchall()

            # Get all messages
            messages = conn.execute("""
                SELECT
                    cmj.chat_id,
                    m.rowid AS message_id,
                    m.text, m.is_from_me, m.handle_id,
                    h.id AS sender,
                    m.service, m.date,
                    m.associated_message_guid, m.thread_originator_guid, m.item_type
                FROM chat_message_join cmj
                JOIN message m ON m.rowid = cmj.message_id
                LEFT JOIN handle h ON h.rowid = m.handle_id
                ORDER BY m.date ASC, m.rowid ASC
            """).fetchall()

            # Get all attachments
            atts = conn.execute("""
                SELECT
                    cmj.chat_id,
                    maj.message_id,
                    a.transfer_name AS name,
                    a.mime_type AS mime,
                    a.filename AS path
                FROM message_attachment_join maj
                JOIN attachment a ON a.rowid = maj.attachment_id
                JOIN chat_message_join cmj ON cmj.message_id = maj.message_id
            """).fetchall()

            # Index attachments per message
            att_map = {}
            for a in atts:
                att_map.setdefault(a["message_id"], []).append({
                    "name": a["name"], "mime": a["mime"], "path": a["path"]
                })

            # Group messages per chat
            chat_map = {}
            for c in chats:
                chat_map[c["rowid"]] = {
                    "chat_guid": c["guid"],
                    "display_name": c["display_name"],
                    "chat_identifier": c["chat_identifier"],
                    "participants": [p for p in (c["participants"] or "").split(",") if p],
                    "messages": []
                }

            # Add messages to their respective chats
            for m in messages:
                ts = self.apple_to_unix(m["date"])
                chat_map[m["chat_id"]]["messages"].append({
                    "id": m["message_id"],
                    "timestamp": self.format_timestamp(ts) if ts else None,
                    "from_me": bool(m["is_from_me"]),
                    "sender": m["sender"],
                    "service": m["service"],
                    "text": m["text"],
                    "item_type": m["item_type"],
                    "associated_message_guid": m["associated_message_guid"],
                    "thread_originator_guid": m["thread_originator_guid"],
                    "attachments": att_map.get(m["message_id"], [])
                })

            # Convert to list and sort by last message time
            result = list(chat_map.values())
            for chat in result:
                chat["messages"].sort(key=lambda x: x["timestamp"] or "")
            result.sort(key=lambda c: (c["messages"][-1]["timestamp"] if c["messages"] else ""), reverse=True)

            # Write to JSON file
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        finally:
            conn.close()

    def _extract_text_from_attributed_body(self, attributed_body: bytes) -> str:
        """Extract plain text from attributedBody binary data.

        The attributedBody column contains text in a binary format that needs to be parsed.
        This method attempts to extract the plain text content using a targeted approach.

        Args:
            attributed_body: Binary data from the attributedBody column

        Returns:
            Extracted plain text or empty string if extraction fails
        """
        if not attributed_body:
            return ""

        try:
            # Simpler approach: extract readable text from the binary data
            # Based on observations from the debug output, the actual message text
            # is embedded in the binary data as readable strings

            # Convert to string, ignoring errors
            decoded = attributed_body.decode('utf-8', errors='ignore')

            # Split on null bytes which are common separators in the binary data
            parts = decoded.split('\x00')

            # Look for parts that contain readable text
            for part in parts:
                # Clean the part by removing control characters
                clean_part = ''.join(c for c in part if ord(c) >= 32 or c in '\n\r\t ')
                clean_part = clean_part.strip()

                # Check if this part looks like a message (reasonable length, mostly printable)
                if 10 <= len(clean_part) <= 1000:  # Reasonable message length
                    printable_ratio = sum(1 for c in clean_part if c.isalnum() or c.isspace() or c in '.,!?;:-()"\'') / len(clean_part)
                    # If mostly printable characters and doesn't contain binary markers
                    if printable_ratio > 0.7 and not any(marker in clean_part for marker in ['streamtyped', 'NSAttributedString', 'NSObject', 'NSString', '__kIM', 'NSNumber']):
                        # Additional check: look for sentence-like structure
                        if any(ending in clean_part for ending in ['.', '!', '?']) or len(clean_part.split()) > 3:
                            # Return the cleanest part - one that starts with a letter and doesn't end with binary artifacts
                            clean_part = clean_part.split('iI')[0].strip()  # Remove trailing binary artifacts
                            if clean_part and clean_part[0].isalpha():
                                return clean_part

            # If no clear message found, return empty string
            return ""
        except Exception:
            # If parsing fails, return empty string
            return ""
