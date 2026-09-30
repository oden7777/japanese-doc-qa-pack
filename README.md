# Safe Japanese Document QA Pack Lite

Static, safe and reproducible test fixtures for QA of software that handles
Japanese documents: PDF, OCR, CSV, Unicode text and ZIP file names.

Each case is an input file plus an `expected.json` that records **objective
facts about that file** (its ground truth): exact text and Unicode code
points, CSV rows and values, PDF page count, rotation, page sizes and text
layers, archive entry names and their raw bytes. It does not record how a
particular library *should* behave; comparing your tool's output with the
ground truth is up to your own tests.

This is a static fixture collection, not a service. Everything works offline.

## Cases

| ID | Category | What it contains |
|----|----------|------------------|
| [pdf-001](cases/pdf-001/README.md) | pdf | Japanese vertical writing (true PDF WMode 1) with ruby; standard CID font, not embedded |
| [pdf-002](cases/pdf-002/README.md) | pdf | A4, A4 with `/Rotate 90`, and A5 pages in one file |
| [pdf-003](cases/pdf-003/README.md) | pdf | Scan-like image with an invisible (render mode 3) searchable text layer |
| [ocr-001](cases/ocr-001/README.md) | ocr | Image-only PDF of a fictional Japanese receipt; no text layer at all |
| [csv-001](cases/csv-001/README.md) | csv | Windows-31J CSV: quoted commas, escaped quotes, in-field newline, CP932 mapping differences |
| [csv-002](cases/csv-002/README.md) | csv | UTF-8 CSV with BOM: half-width katakana, full-width alphanumerics, compatibility characters |
| [txt-001](cases/txt-001/README.md) | txt | The same kana strings in NFC and NFD |
| [txt-002](cases/txt-002/README.md) | txt | Invisible characters: ZWSP, NBSP, IDEOGRAPHIC SPACE, mid-text U+FEFF, WORD JOINER |
| [txt-003](cases/txt-003/README.md) | txt | Strings whose NFC/NFD/NFKC/NFKD forms differ, with all four forms recorded |
| [archive-001](cases/archive-001/README.md) | archive | ZIP mixing UTF-8 (flagged) and CP932 (unflagged) entry names, incl. `0x5C` trail bytes |

Each case directory holds `input.*`, `expected.json` and a `README.md` that
explains the case on its own.

## Layout

```
cases/<id>/            input.*, expected.json, README.md
schema/                expected.schema.json (JSON Schema 2020-12 for every expected.json)
manifest.json          id, category, path and features of every case
tools/verify.py        integrity check (existence, schema, SHA-256)
tools/gen/             one small generation script per case, common.py (shared helpers) and manifest.py
fonts/                 BIZ UDGothic Regular and its license (used for generation only)
```

## Verify the pack

Requires Python 3.10 or later.

```sh
pip install -r requirements.txt
python tools/verify.py
```

For every case listed in `manifest.json`, `verify.py` checks only three
things: the listed files exist, `expected.json` passes
`schema/expected.schema.json`, and the SHA-256 of the input file matches
`input.sha256`. It prints `OK <id>` or `FAIL <id>: <reason>` per case and a
summary line, and exits with 0 when every case passes, 1 when any case fails,
and 2 when `manifest.json` or the schema cannot be read. It does not parse
PDFs, run OCR or read CSV content, and it never uses the network.

## Regenerate fixtures

The committed files are authoritative: their SHA-256 values are fixed in
`expected.json`. The scripts exist so the fixtures can be rebuilt or changed.
With the pinned versions they reproduce the committed files byte for byte,
but that is not guaranteed across library or font versions.

Generation uses Python 3.14 (Unicode 16.0.0), works offline and only uses
files in this repository.

```sh
pip install -r requirements-gen.txt
python tools/gen/pdf_001.py          # or any other tools/gen/<case>.py
python tools/gen/manifest.py
python tools/verify.py
```

Each script builds `cases/<id>/input.*`, checks those exact bytes against the
ground truth it is about to record (PDFs are read back with pypdf after
writing), and only then writes `expected.json`, including the new SHA-256. Case `README.md` files are hand-written and never
overwritten. If a regenerated input's SHA-256 changes, review the diff of
`input.*` and `expected.json` before committing both.

## Safety

- All names, shops, addresses, phone numbers and amounts are fictional.
- PDFs contain no JavaScript, actions, links, annotations or embedded files.
- CSV cells never start with `=`, `+`, `-` or `@`.
- The ZIP contains only short text files: no executables, links, nested
  archives, absolute paths or `..`.
- Text files contain no bidirectional control characters.

## License

- Code (`tools/`, `tests/`): MIT, see [LICENSE](LICENSE).
- Fixture data (`cases/`, `schema/`, `manifest.json`): CC0 1.0, see
  [LICENSE-DATA](LICENSE-DATA).
- Third-party material keeps its own license: BIZ UDGothic in `fonts/` is
  under the SIL Open Font License 1.1, see [fonts/OFL.txt](fonts/OFL.txt).

These licenses apply to this Lite edition only. They do not apply to any
future Pro edition, which will have its own separate commercial license.
