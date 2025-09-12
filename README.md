# imessage-extractor

[![PyPI](https://img.shields.io/pypi/v/imessage-extractor.svg)](https://pypi.org/project/imessage-extractor/)
[![Changelog](https://img.shields.io/github/v/release/scotm/imessage-extractor?include_prereleases&label=changelog)](https://github.com/scotm/imessage-extractor/releases)
[![Tests](https://github.com/scotm/imessage-extractor/actions/workflows/test.yml/badge.svg)](https://github.com/scotm/imessage-extractor/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/scotm/imessage-extractor/blob/master/LICENSE)

Extract and parse iMessage conversations from your Mac's database

## Installation

Install this tool using `pip`:
```bash
pip install imessage-extractor
```

## Usage

For help, run:
```bash
imessage-extractor --help
```

You can also use:
```bash
python -m imessage_extractor --help
```

### Export a specific chat to CSV

Export conversations with a specific participant to a CSV file:
```bash
# Export chat by phone number or email substring
imessage-extractor export-chat "+1234567890" -o conversation.csv

# Use a custom database path (useful if you've copied the database)
imessage-extractor export-chat "john@example.com" -d /path/to/chat.db -o conversation.csv
```

### Export all chats to JSON

Export all conversations as a single JSON file:
```bash
# Export all chats to JSON
imessage-extractor export-all -o all_conversations.json

# Use a custom database path
imessage-extractor export-all -d /path/to/chat.db -o all_conversations.json
```

### List available chats

List all chats that match a participant identifier without exporting:
```bash
# List all chats with participants matching a substring
imessage-extractor list-chats "+1234567890"
```

## Permissions and Preparation

Before using this tool, you need to:

1. Grant Terminal or your Python runtime Full Disk Access in System Settings
2. Close the Messages app to avoid database locks
3. (Optional) Copy the database to avoid contention:
   ```bash
   cp ~/Library/Messages/chat.db /tmp/chat.db
   ```

### Granting Full Disk Access

macOS restricts access to sensitive locations like `~/Library/Messages/` for security reasons.
To grant the necessary permissions:

1. Open **System Settings** > **Privacy & Security** > **Full Disk Access**
2. Click the lock icon and authenticate with your password
3. Click the **+** button to add an application
4. Press **Cmd+Shift+G** and enter `/Applications/Utilities/Terminal.app` (or your terminal app)
5. Select **Terminal** (or your terminal app) and click **Open**
6. If using an IDE or other Python environment, add that as well
7. Completely quit and restart your terminal application

### For iCloud Messages users

The local database still reflects synced messages, but some items may be archived. 
To ensure you have the most complete data:

```bash
cp ~/Library/Messages/chat.db* /tmp/
```

This copies the main database file along with the WAL and SHM files which contain 
recent messages that haven't been fully committed to the main database yet.

### Troubleshooting Permission Errors

If you encounter permission errors:

1. Double-check that your terminal application has been added to Full Disk Access
2. Ensure you've restarted your terminal after granting permissions
3. Verify the Messages app is completely quit (check Activity Monitor if needed)
4. Try copying the database files to a different location and using the `-d` option:
   ```bash
   # Copy all database files
   mkdir -p /tmp/messages-db
   cp ~/Library/Messages/chat.db* /tmp/messages-db/
   
   # Use with the tool
   imessage-extractor export-chat "+1234567890" -d /tmp/messages-db/chat.db
   ```

## Data Format

The exported data includes:

### CSV Export
- `message_id`: Unique identifier for the message
- `timestamp_local_iso`: Message timestamp in ISO format (local timezone)
- `from_me`: Boolean indicating if the message was sent by you (1) or received (0)
- `sender_identifier`: Phone number or email of the message sender
- `text`: Message content
- `service`: Service used (e.g., iMessage, SMS)
- `attachment_name`: Name of any attached file
- `attachment_mime`: MIME type of any attached file
- `attachment_path`: Path to any attached file

### JSON Export
The JSON export groups messages by conversation thread and includes:
- `chat_guid`: Unique identifier for the chat
- `display_name`: Display name of the chat (for group chats)
- `chat_identifier`: Internal identifier for the chat
- `participants`: List of participants in the chat
- `messages`: List of messages in chronological order, each with:
  - `id`: Message identifier
  - `timestamp`: Message timestamp in ISO format
  - `from_me`: Boolean indicating if the message was sent by you
  - `sender`: Phone number or email of the sender
  - `service`: Service used (e.g., iMessage, SMS)
  - `text`: Message content
  - `item_type`: Type of message (regular message, reaction, etc.)
  - `associated_message_guid`: Reference to another message (for reactions/replies)
  - `thread_originator_guid`: Reference to thread root message (for replies)
  - `attachments`: List of attachments with name, MIME type, and path

## Synthetic Sample Data

If you want to experiment without using real messages, you can create a tiny
CSV file with two mock entries:

```csv
message_id,timestamp_local_iso,from_me,sender_identifier,text,service,attachment_name,attachment_mime,attachment_path
1,2024-01-01T00:00:00,1,+1234567890,Hello world,iMessage,,,
2,2024-01-01T00:01:00,0,+0987654321,Hi!,iMessage,,,
```

Save the above as `sample.csv`, or generate it using Python:

```bash
python - <<'PY'
import csv
rows = [
    {"message_id": 1, "timestamp_local_iso": "2024-01-01T00:00:00", "from_me": 1, "sender_identifier": "+1234567890", "text": "Hello world", "service": "iMessage", "attachment_name": "", "attachment_mime": "", "attachment_path": ""},
    {"message_id": 2, "timestamp_local_iso": "2024-01-01T00:01:00", "from_me": 0, "sender_identifier": "+0987654321", "text": "Hi!", "service": "iMessage", "attachment_name": "", "attachment_mime": "", "attachment_path": ""},
]
with open("sample.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
PY
```

This writes `sample.csv` in the current directory.

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd imessage-extractor
python -m venv venv
source venv/bin/activate
```

Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```

To run the tests:
```bash
python -m pytest
```

The test suite covers input validation helpers, database export functions, and
parser utilities (such as URL and mention extraction).

## How It Works

This tool directly reads your iMessage database file (chat.db) which is maintained by macOS. 
Key tables used:

- `handle`: stores contact identifiers (phone numbers/emails)
- `chat`: represents a conversation thread
- `message`: individual messages in conversations
- `chat_handle_join`: links chats to participants
- `chat_message_join`: links chats to messages
- `attachment`: file attachments
- `message_attachment_join`: links messages to attachments

Timestamps are converted from Apple's epoch format (nanoseconds since 2001-01-01) to standard 
Unix timestamps and then formatted as ISO strings in your local timezone.

For group chats, the `display_name` field contains the chat's name when available, and all 
participants are listed in the `participants` field.

Attachments are referenced by relative paths which are typically within the 
`~/Library/Messages/Attachments/` directory.

## Common Issues

- **Permission denied**: Make sure you've granted Full Disk Access to your terminal application
- **Empty text fields**: Some messages (like stickers or images without captions) may have empty text
- **Missing recent messages**: For iCloud users, copy all database files (chat.db*) to ensure complete data
- **Database locked**: Make sure Messages app is completely quit before running extraction
