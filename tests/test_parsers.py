"""Tests for parser utility functions."""

from imessage_extractor.parsers import TextParser


def test_extract_urls_from_text():
    """URLs should be extracted from text content."""
    text = "See https://example.com and http://test.com/path?query=1"
    urls = TextParser.extract_urls_from_text(text)
    assert urls == [
        "https://example.com",
        "http://test.com/path?query=1",
    ]


def test_extract_mentions_from_text():
    """Mentions should be extracted from text content."""
    text = "Hello @alice and @bob!"
    mentions = TextParser.extract_mentions_from_text(text)
    assert mentions == ["alice", "bob"]
