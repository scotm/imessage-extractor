
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
        ``NSAttributedString`` objects. This method unarchives the blob using
        ``typedstream`` and returns the underlying string value.
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
