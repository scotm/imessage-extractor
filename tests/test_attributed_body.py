import plistlib

from imessage_extractor.database import IMessageDatabase


def _sample_attributed_body() -> bytes:
    plist = {
        "$archiver": "NSKeyedArchiver",
        "$version": 100000,
        "$top": {"root": {"CF$UID": 1}},
        "$objects": [
            "$null",
            {
                "NS.string": {"CF$UID": 2},
                "NS.attributes": {"CF$UID": 0},
                "$class": {"CF$UID": 3},
            },
            "Hello\uFFFCWorld",
            {
                "$classes": ["NSAttributedString", "NSObject"],
                "$classname": "NSAttributedString",
            },
        ],
    }
    return plistlib.dumps(plist, fmt=plistlib.FMT_BINARY)


def test_extract_text_from_attributed_body():
    db = IMessageDatabase()
    blob = _sample_attributed_body()
    assert db._extract_text_from_attributed_body(blob) == "HelloWorld"
