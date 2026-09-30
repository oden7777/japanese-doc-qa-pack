# archive-001: ZIP entry names in mixed UTF-8 and CP932

## Purpose

Tests how an archive tool decodes ZIP entry names. The ZIP format stores
names as raw bytes. Bit 11 of the general purpose flag ("UTF-8 flag") says the
name is UTF-8; without it, names are traditionally read as CP437, while
Japanese Windows tools have long written CP932 without setting the flag.
This archive contains both kinds. Typical things to check: honouring the
UTF-8 flag, choosing an encoding for unflagged names, NFD names, emoji, spaces,
and names whose CP932 bytes contain `0x5C`.

## Input

- `input.zip`: 8 stored (uncompressed) entries, no directories, timestamps
  1980-01-01 00:00:00. Each entry holds a short ASCII text `sample <n>` + LF.

| # | Name | Name bytes | UTF-8 flag |
|---|------|------------|------------|
| 1 | 日本語ファイル.txt | UTF-8 | set |
| 2 | space in name.txt | ASCII space U+0020 | set |
| 3 | 全角　空白.txt | contains U+3000 IDEOGRAPHIC SPACE | set |
| 4 | ｶﾀｶﾅ.txt | half-width katakana | set |
| 5 | が.txt | NFD: U+304B U+3099 | set |
| 6 | emoji_😀.txt | U+1F600 (4-byte UTF-8) | set |
| 7 | 表示.txt | CP932 `95 5C 8E A6` + `.txt` | not set |
| 8 | ソフト.txt | CP932 `83 5C 83 74 83 67` + `.txt` | not set |

## Features

`zip`, `utf8-filename-flag`, `cp932-filename`, `mixed-filename-encodings`,
`0x5c-trail-byte`, `nfd-filename`, `emoji-filename`, `space-in-filename`

## Ground truth

`expected.json` → `ground_truth` records `entry_count`, `compression`
(`stored`), the fixed `timestamp`, and for every entry in archive order:

- `raw_name_hex`: the name bytes exactly as stored in the archive.
- `utf8_flag`: whether bit 11 is set.
- `name_encoding`: the encoding the name was written in (`utf-8` or `cp932`).
- `name`: the name decoded with that encoding (text plus code points).
- `size`, `sha256` and `crc32` of the entry content.

The ground truth states how each name was encoded. It does not say what a
tool should display for an unflagged name; guessing CP932 there is a choice
the tool makes.

## How it was generated

`python tools/gen/archive_001.py`. Python's `zipfile` always writes non-ASCII
names as flagged UTF-8, so the script writes the ZIP structure itself with
`struct`: local file headers, central directory and end record, no
compression, no extra fields. It then reads the bytes back with `zipfile` and
checks CRCs, flags, raw name bytes, sizes and hashes, that there are no
directory entries, absolute paths, `..` or drive letters, and that a CP932
name contains `0x5C`, before it writes the file and `expected.json`.

## Notes

- In entries 7 and 8 the second byte of `表` (`95 5C`) and `ソ` (`83 5C`)
  equals ASCII backslash `0x5C`. This case breaks implementations that do not
  decode CP932 correctly and instead handle the name byte by byte, for example
  when they look for path separators or escape characters in the raw bytes.
  Whether a given tool actually misreads it depends on that tool.
- Observed while generating (informative only, not ground truth): Python's
  `zipfile` shows entries 7 and 8 as CP437 mojibake; libarchive `bsdtar`
  decodes them correctly with `--options hdrcharset=CP932`; the `unzip` bundled
  with macOS displays the flagged UTF-8 names as mojibake.
- The archive contains no executables, links, nested archives or paths
  outside the extraction directory, and is far too small to be a
  decompression bomb.
