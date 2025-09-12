
# Constants for the iMessage Extractor application

# Database and File Paths
DEFAULT_DB_PATH = "~/Library/Messages/chat.db"
DEFAULT_ATTACHMENTS_PATH = "~/Library/Messages/Attachments/"

# Default Output Files
DEFAULT_CSV_FILENAME = "imessage_chat.csv"
DEFAULT_JSON_FILENAME = "imessage_all.json"

# Timestamp Conversion Constants
APPLE_EPOCH_OFFSET = 978307200  # Seconds between Unix epoch (1970) and Apple epoch (2001)
NANOSECONDS_THRESHOLD = 10**12  # Threshold to detect nanoseconds vs seconds

# Database Column Names
COL_MESSAGE_ID = "message_id"
COL_TIMESTAMP_LOCAL_ISO = "timestamp_local_iso"
COL_FROM_ME = "from_me"
COL_SENDER_IDENTIFIER = "sender_identifier"
COL_TEXT = "text"
COL_SERVICE = "service"
COL_ATTACHMENT_NAME = "attachment_name"
COL_ATTACHMENT_MIME = "attachment_mime"
COL_ATTACHMENT_PATH = "attachment_path"

# Database Table and Column Names
TABLE_CHAT = "chat"
TABLE_MESSAGE = "message"
TABLE_HANDLE = "handle"
TABLE_CHAT_MESSAGE_JOIN = "chat_message_join"
TABLE_CHAT_HANDLE_JOIN = "chat_handle_join"
TABLE_MESSAGE_ATTACHMENT_JOIN = "message_attachment_join"
TABLE_ATTACHMENT = "attachment"

# Message Column Names
MSG_ROWID = "rowid"
MSG_TEXT = "text"
MSG_ATTRIBUTED_BODY = "attributedBody"
MSG_IS_FROM_ME = "is_from_me"
MSG_HANDLE_ID = "handle_id"
MSG_SERVICE = "service"
MSG_DATE = "date"
MSG_DATE_READ = "date_read"
MSG_DATE_DELIVERED = "date_delivered"
MSG_ASSOCIATED_MESSAGE_GUID = "associated_message_guid"
MSG_THREAD_ORIGINATOR_GUID = "thread_originator_guid"
MSG_ITEM_TYPE = "item_type"

# Chat Column Names
CHAT_ROWID = "rowid"
CHAT_GUID = "guid"
CHAT_IDENTIFIER = "chat_identifier"
CHAT_DISPLAY_NAME = "display_name"
CHAT_PARTICIPANTS = "participants"

# Handle Column Names
HANDLE_ROWID = "rowid"
HANDLE_ID = "id"

# Attachment Column Names
ATTACHMENT_ROWID = "rowid"
ATTACHMENT_FILENAME = "filename"
ATTACHMENT_TRANSFER_NAME = "transfer_name"
ATTACHMENT_MIME_TYPE = "mime_type"

# Unicode Characters
OBJECT_REPLACEMENT_CHAR = "\uFFFC"  # Placeholder for attachments
HAIR_SPACE = "\u200a"
ZERO_WIDTH_SPACE = "\u200b"
ZERO_WIDTH_NON_JOINER = "\u200c"

# Service Types
SERVICE_IMESSAGE = "iMessage"
SERVICE_SMS = "SMS"
SERVICE_RCS = "RCS"

# Exit Codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"

# SQL Query Fragments
SQL_GROUP_CONCAT_SEPARATOR = ", "
SQL_LIKE_WILDCARD = "%"

# Error Messages
ERR_PERMISSION_DENIED = "Permission denied accessing {path}. Please ensure you have granted Full Disk Access to your terminal application in System Settings > Privacy & Security > Full Disk Access."
ERR_DATABASE_LOCKED = "Database is locked: {path}. Please ensure the Messages app is completely quit before running this tool."
ERR_DATABASE_NOT_FOUND = "Database file not found: {path}. Please check that the path is correct and the file exists."
ERR_NO_CHATS_FOUND = "No chats found with the specified participant."
ERR_INVALID_CHOICE = "Invalid choice."
ERR_MISSING_KEYS = "Chat data structure is incomplete. Missing keys: {keys}"

# User Guidance Messages
GUIDANCE_PERMISSION_ERROR = """
To resolve this issue:
1. Open System Settings > Privacy & Security > Full Disk Access
2. Add your terminal application (Terminal, iTerm, etc.) to the list
3. Restart your terminal application
4. Quit the Messages app completely
5. Try running the command again
"""

GUIDANCE_FILE_NOT_FOUND = """
To resolve this issue:
1. Verify the file path is correct
2. Ensure the file exists and you have access to it
3. Expand any '~' or environment variables to full paths
"""

# Validation Constants
REQUIRED_CHAT_KEYS = ["rowid", "display_name", "chat_identifier", "participants"]
MAX_CHOICE_INDEX = 1000  # Reasonable upper bound for user selection

# Encoding
UTF8_ENCODING = "utf-8"
UTF8_ERROR_HANDLING = "ignore"

# File Operations
CSV_NEWLINE = ""
JSON_INDENT = 2

# Alias for backward compatibility
COL_CHAT_IDENTIFIER = CHAT_IDENTIFIER
COL_DISPLAY_NAME = CHAT_DISPLAY_NAME
COL_PARTICIPANTS = CHAT_PARTICIPANTS
