import gzip
import plistlib

import pytest

from imessage_extractor.database import IMessageDatabase


@pytest.fixture
def archived_message():
    """Return a message row with text stored in ``attributedBody``."""
    text = "Hello from attributed body"
    plist = {
        "$version": 100000,
        "$archiver": "NSKeyedArchiver",
        "$objects": [
            "$null",
            {"NS.string": text},
        ],
        "$top": {"root": 1},
    }
    data = plistlib.dumps(plist, fmt=plistlib.FMT_BINARY)
    return {"text": None, "attributedBody": gzip.compress(data), "expected": text}


def test_extract_text_from_attributed_body(archived_message):
    db = IMessageDatabase(db_path=":memory:")
    result = db._extract_text_from_attributed_body(archived_message["attributedBody"])
    assert result == archived_message["expected"]
