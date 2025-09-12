
"""Text parsing utilities for the iMessage Extractor application."""

from typing import Optional

from .constants import (
    OBJECT_REPLACEMENT_CHAR,
    HAIR_SPACE,
    ZERO_WIDTH_SPACE,
    ZERO_WIDTH_NON_JOINER,
    UTF8_ENCODING,
    UTF8_ERROR_HANDLING,
)
from .exceptions import TextExtractionError


class TextParser:
    """Parser for extracting text from various iMessage data formats."""

    @staticmethod
    def extract_text_from_attributed_body(attributed_body: bytes) -> str:
        """Extract plain text from attributedBody binary data.

        Messages stored in the ``attributedBody`` column are archived
        ``NSAttributedString`` objects. This method handles both binary plist
        (NSKeyedArchiver) and typedstream formats, returning the underlying string value.
        If the archive contains inline attachments they are represented
        by the object replacement character (``\uFFFC``); these segments are
        stripped from the result so that only the human‑readable text remains.

        Args:
            attributed_body: Binary data from the ``attributedBody`` column.

        Returns:
            Extracted plain text, or an empty string if decoding fails.

        Raises:
            TextExtractionError: If text extraction fails
        """
        if not attributed_body:
            return ""

        try:
            # First try to parse as binary plist (NSKeyedArchiver format)
            if attributed_body.startswith(b'bplist00'):
                import plistlib
                plist_data = plistlib.loads(attributed_body)

                # Extract text from NSKeyedArchiver format
                if "$objects" in plist_data and "$top" in plist_data:
                    objects = plist_data["$objects"]
                    top = plist_data["$top"]

                    # Get the root object
                    if "root" in top:
                        root_ref = top["root"]
                        if isinstance(root_ref, dict) and "CF$UID" in root_ref:
                            root_uid = root_ref["CF$UID"]
                            if root_uid < len(objects):
                                root_obj = objects[root_uid]
                                if isinstance(root_obj, dict) and "NS.string" in root_obj:
                                    string_ref = root_obj["NS.string"]
                                    if isinstance(string_ref, dict) and "CF$UID" in string_ref:
                                        string_uid = string_ref["CF$UID"]
                                        if string_uid < len(objects):
                                            string_obj = objects[string_uid]
                                            if isinstance(string_obj, str):
                                                # Clean up the text and remove object replacement characters
                                                text_str = TextParser._convert_escaped_characters(string_obj)
                                                return text_str.replace(OBJECT_REPLACEMENT_CHAR, "")
                return ""

            # Fall back to typedstream format
            import typedstream

            # Unarchive the NSAttributedString stored in the blob
            stream = typedstream.unarchive_from_data(attributed_body)

            # Extract text from the contents attribute
            if hasattr(stream, 'contents') and stream.contents:
                # The first element in contents is typically the text string
                first_content = stream.contents[0]
                # If it's a TypedValue, get its value
                if hasattr(first_content, 'value'):
                    text = first_content.value
                    # If it's a string object with a 'string' attribute, use that
                    if hasattr(text, 'string'):
                        text = text.string
                    elif isinstance(text, bytes):
                        # Decode bytes to string
                        text = text.decode(UTF8_ENCODING, errors=UTF8_ERROR_HANDLING)
                    elif not isinstance(text, str):
                        # Convert other objects to string
                        text = str(text)

                    # Clean up the text representation for NSString/NSMutableString objects
                    text_str = TextParser._clean_string_object(text)
                    # Convert escaped characters to actual characters
                    text_str = TextParser._convert_escaped_characters(text_str)
                    # Remove placeholders for attachments (NSTextAttachment)
                    return text_str.replace(OBJECT_REPLACEMENT_CHAR, "")
                else:
                    # If first_content is already the text
                    text = str(first_content)
                    return text.replace(OBJECT_REPLACEMENT_CHAR, "")
            return ""
        except Exception as e:
            raise TextExtractionError(details=str(e))

    @staticmethod
    def _clean_string_object(text: str) -> str:
        """Clean up string object representation.

        Args:
            text: Raw text from string object

        Returns:
            Cleaned text string
        """
        text_str = str(text)
        # Remove object wrapper notation like NSString("...") or NSMutableString('...')
        if text_str.startswith(('NSString(', 'NSMutableString(')) and text_str.endswith(')'):
            # Extract the inner content between the outermost parentheses
            inner_content = text_str[text_str.find('(')+1:text_str.rfind(')')]
            # Remove surrounding quotes if present
            if (inner_content.startswith('"') and inner_content.endswith('"')) or \
               (inner_content.startswith("'") and inner_content.endswith("'")):
                text_str = inner_content[1:-1]
            else:
                text_str = inner_content
        return text_str

    @staticmethod
    def _convert_escaped_characters(text: str) -> str:
        """Convert escaped characters to actual characters.

        Args:
            text: Text with escaped characters

        Returns:
            Text with unescaped characters
        """
        # Handle common escape sequences
        text = text.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
        # Handle specific unicode escape sequences we commonly see
        text = text.replace('\\u200a', HAIR_SPACE).replace('\\u200b', ZERO_WIDTH_SPACE).replace('\\u200c', ZERO_WIDTH_NON_JOINER)
        return text

    @staticmethod
    def clean_text_for_csv(text: str) -> str:
        """Clean text for CSV output.

        Args:
            text: Raw text content

        Returns:
            Cleaned text suitable for CSV
        """
        if not text:
            return ""

        # Replace carriage return + line feed with just line feed
        return text.replace('\r\n', '\n')

    @staticmethod
    def extract_urls_from_text(text: str) -> list[str]:
        """Extract URLs from text content.

        Args:
            text: Text content to search for URLs

        Returns:
            List of URLs found in the text
        """
        import re

        # Basic URL regex pattern
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))*)?'
        urls = re.findall(url_pattern, text, re.IGNORECASE)

        return urls

    @staticmethod
    def extract_mentions_from_text(text: str) -> list[str]:
        """Extract user mentions from text content.

        Args:
            text: Text content to search for mentions

        Returns:
            List of mentions found in the text
        """
        import re

        # Basic mention pattern (e.g., @username)
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, text)

        return mentions

    @staticmethod
    def detect_mime_type(file_path: str) -> str:
        """Detect MIME type of a file by examining its content.

        Uses multiple methods to determine the correct MIME type:
        1. `file` command (most reliable)
        2. `magic` library for content-based detection
        3. Python's mimetypes module as fallback
        4. Manual detection for common file types

        Args:
            file_path: Path to the file to examine

        Returns:
            Detected MIME type string, or 'application/octet-stream' if unknown
        """
        import os
        import subprocess

        if not os.path.exists(file_path):
            return "application/octet-stream"

        # Method 1: Use the `file` command if available
        try:
            result = subprocess.run(
                ["file", "--mime-type", "-b", file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                mime_type = result.stdout.strip()
                if mime_type != "application/octet-stream":
                    return mime_type
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass

        # Method 2: Try python-magic if available
        try:
            import magic  # type: ignore
            mime_type = magic.from_file(file_path, mime=True)
            if mime_type and mime_type != "application/octet-stream":
                return mime_type
        except (ImportError, AttributeError):
            pass

        # Method 3: Use mimetypes based on file extension
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type

        # Method 4: Manual detection for common file types without extensions
        try:
            with open(file_path, 'rb') as f:
                header = f.read(64)  # Read first 64 bytes

            # Check for common file signatures
            if header.startswith(b'\xff\xd8\xff'):  # JPEG
                return "image/jpeg"
            elif header.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                return "image/png"
            elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):  # GIF
                return "image/gif"
            elif header.startswith(b'BM'):  # BMP
                return "image/bmp"
            elif header.startswith(b'RIFF') and header[8:12] == b'WEBP':  # WebP
                return "image/webp"
            elif header.startswith(b'%PDF'):  # PDF
                return "application/pdf"
            elif header.startswith(b'PK\x03\x04'):  # ZIP
                return "application/zip"
            elif header.startswith(b'\x1f\x8b'):  # GZIP
                return "application/gzip"
            elif header.startswith(b'BZh'):  # BZIP2
                return "application/x-bzip2"
            elif header.startswith(b'7z\xbc\xaf\x27\x1c'):  # 7Z
                return "application/x-7z-compressed"
            elif header.startswith(b'Rar!\x1a\x07'):  # RAR
                return "application/x-rar-compressed"
            elif header.startswith(b'fLaC'):  # FLAC audio
                return "audio/flac"
            elif header.startswith(b'ID3') or header.startswith(b'\xff\xfb') or header.startswith(b'\xff\xf3'):  # MP3
                return "audio/mpeg"
            elif header.startswith(b'\x00\x00\x00\x20ftypM4A'):  # M4A
                return "audio/mp4"
            elif header.startswith(b'\x00\x00\x00\x20ftypmp4'):  # MP4 video
                return "video/mp4"
            elif header.startswith(b'\x1a\x45\xdf\xa3'):  # WebM/MKV
                return "video/webm"
            elif header.startswith(b'FLV\x01'):  # FLV
                return "video/x-flv"
            elif header.startswith(b'\x00\x00\x00\x14ftyp'):  # Generic MP4
                return "video/mp4"
            elif header.startswith(b'MOVI'):  # MOV
                return "video/quicktime"

        except (OSError, IOError):
            pass

        # Default fallback
        return "application/octet-stream"

    @staticmethod
    def format_timestamp_for_display(unix_ts: Optional[float]) -> str:
        """Format Unix timestamp as ISO string in local timezone.

        Args:
            unix_ts: Unix timestamp in seconds

        Returns:
            ISO formatted timestamp string in local timezone, or empty string if None
        """
        from datetime import datetime, timezone

        if unix_ts is None:
            return ""
        return datetime.fromtimestamp(unix_ts, tz=timezone.utc).astimezone().isoformat()
