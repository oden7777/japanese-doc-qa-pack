"""Generate cases/archive-001: a ZIP whose entry names mix UTF-8 and CP932.

Python's zipfile always writes non-ASCII names as UTF-8 with the UTF-8 flag
(general purpose bit 11) set, so this script writes the ZIP by hand: stored
(uncompressed) entries, a fixed 1980-01-01 00:00:00 timestamp, local headers,
a central directory and the end record. Some names are UTF-8 with the flag
set; others are CP932 bytes without the flag, as written by older Japanese
Windows tools.

Usage: python tools/gen/archive_001.py
"""

from __future__ import annotations

import hashlib
import io
import struct
import unicodedata
import zipfile
import zlib

from common import case_dir, text_value, write_expected

CASE_ID = "archive-001"
UTF8_FLAG = 0x0800
DOS_TIME = 0                          # 00:00:00
DOS_DATE = (0 << 9) | (1 << 5) | 1    # 1980-01-01
VERSION = 20                          # 2.0, MS-DOS host
# (name, encoding). UTF-8 names get the UTF-8 flag; CP932 names do not.
ENTRIES = [
    ("日本語ファイル.txt", "utf-8"),
    ("space in name.txt", "utf-8"),
    ("全角\u3000空白.txt", "utf-8"),
    ("ｶﾀｶﾅ.txt", "utf-8"),
    (unicodedata.normalize("NFD", "が.txt"), "utf-8"),
    ("emoji_😀.txt", "utf-8"),
    ("表示.txt", "cp932"),    # 表 is 95 5C: second byte equals ASCII backslash
    ("ソフト.txt", "cp932"),  # ソ is 83 5C
]


def content(n: int) -> bytes:
    return f"sample {n}\n".encode("ascii")


def build() -> tuple[bytes, list[dict[str, object]]]:
    out = io.BytesIO()
    central = []
    facts = []
    for n, (name, encoding) in enumerate(ENTRIES, start=1):
        raw_name = name.encode(encoding)
        flag = UTF8_FLAG if encoding == "utf-8" else 0
        data = content(n)
        crc = zlib.crc32(data)
        offset = out.tell()
        out.write(struct.pack("<IHHHHHIIIHH", 0x04034B50, VERSION, flag, 0, DOS_TIME, DOS_DATE,
                              crc, len(data), len(data), len(raw_name), 0))
        out.write(raw_name)
        out.write(data)
        central.append(struct.pack("<IHHHHHHIIIHHHHHII", 0x02014B50, VERSION, VERSION, flag, 0,
                                   DOS_TIME, DOS_DATE, crc, len(data), len(data), len(raw_name),
                                   0, 0, 0, 0, 0, offset) + raw_name)
        facts.append({
            "raw_name_hex": raw_name.hex(),
            "utf8_flag": bool(flag),
            "name_encoding": encoding,
            "name": text_value(name),
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "crc32": f"{crc:08x}",
        })
    cd_offset = out.tell()
    for record in central:
        out.write(record)
    cd_size = out.tell() - cd_offset
    out.write(struct.pack("<IHHHHIIH", 0x06054B50, 0, 0, len(ENTRIES), len(ENTRIES), cd_size, cd_offset, 0))
    return out.getvalue(), facts


def self_check(raw: bytes, facts: list[dict[str, object]]) -> None:
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None, "CRC check failed"
        infos = z.infolist()
        assert len(infos) == len(facts)
        for info, fact, (name, encoding) in zip(infos, facts, ENTRIES):
            flag = bool(info.flag_bits & UTF8_FLAG)
            assert flag == fact["utf8_flag"] == (encoding == "utf-8"), name
            # zipfile decodes unflagged names as cp437; re-encoding gives the raw bytes.
            raw_name = info.filename.encode("utf-8" if flag else "cp437")
            assert raw_name.hex() == fact["raw_name_hex"] and raw_name.decode(encoding) == name
            data = z.read(info)
            assert len(data) == fact["size"] and hashlib.sha256(data).hexdigest() == fact["sha256"]
            assert info.compress_type == zipfile.ZIP_STORED and not info.is_dir()
            assert ".." not in name and not name.startswith(("/", "\\")) and name[1:2] != ":", name
    assert any(not f["utf8_flag"] and "5c" in [f["raw_name_hex"][i:i + 2] for i in range(0, len(f["raw_name_hex"]), 2)]
               for f in facts), "need a CP932 name containing byte 0x5C"


def main() -> None:
    directory = case_dir(CASE_ID)
    directory.mkdir(parents=True, exist_ok=True)
    raw, facts = build()
    self_check(raw, facts)
    (directory / "input.zip").write_bytes(raw)
    assert (directory / "input.zip").read_bytes() == raw
    write_expected(
        CASE_ID,
        category="archive",
        description=(
            "Uncompressed ZIP whose entry names mix UTF-8 (with the UTF-8 flag, general purpose "
            "bit 11) and CP932 (without the flag). Names contain Japanese, ASCII and ideographic "
            "spaces, half-width katakana, an NFD-decomposed kana, an emoji, and CP932 names whose "
            "second byte is 0x5C."
        ),
        input_file="input.zip",
        mime_type="application/zip",
        encoding=None,
        features=["zip", "utf8-filename-flag", "cp932-filename", "mixed-filename-encodings",
                  "0x5c-trail-byte", "nfd-filename", "emoji-filename", "space-in-filename"],
        ground_truth={
            "entry_count": len(facts),
            "compression": "stored",
            "timestamp": "1980-01-01T00:00:00 (DOS date/time, no timezone)",
            "entries": facts,
        },
    )


if __name__ == "__main__":
    main()
