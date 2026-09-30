# Japanese File Processing Fixtures Lite

**Safe, reproducible test fixtures for Japanese PDF, OCR, CSV, Unicode and ZIP QA.**

Catch Japanese file-processing edge cases before your users do.

This Lite edition contains **10 ready-to-use fixtures** covering problems such as:

- true PDF vertical writing (`WMode 1`)
- image-only and searchable scanned PDFs
- Windows-31J / CP932 CSV
- quoted fields and embedded newlines
- NFC / NFD / NFKC / NFKD differences
- invisible Unicode characters
- half-width katakana and compatibility characters
- UTF-8 and CP932 filenames inside ZIP archives

Each fixture includes the input file and machine-readable ground truth in `expected.json`.

Everything works offline. No API, account or external service is required.

---

## What is ground truth?

Each case is an input file plus an `expected.json` that records **objective facts about that file**.

Depending on the fixture, this can include:

- exact text and Unicode code points
- Unicode normalization forms
- CSV rows, columns and values
- PDF page count
- page rotation and dimensions
- presence or absence of text layers
- archive entry names
- raw filename bytes
- SHA-256 hashes

The pack deliberately does **not** define how a particular library *should* behave.

Your test code decides how your application should react and compares its output with the supplied ground truth.

---

## Who is this for?

This pack is intended for developers and engineering teams working on software that processes Japanese documents, including:

- PDF processing
- OCR and Document AI
- document ingestion pipelines
- CSV importers
- Unicode normalization
- archive extraction
- Japanese localization QA

---

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
| [archive-001](cases/archive-001/README.md) | archive | ZIP mixing UTF-8 (flagged) and CP932 (unflagged) entry names, including `0x5C` trail bytes |

Each case directory contains:

```text
input.*
expected.json
README.md
```

The case README explains what the fixture contains and what kind of failure it is designed to expose.

---

## Pro edition

A larger commercial edition is planned with **100+ curated Japanese file processing fixtures**, including more compound and production-oriented edge cases.

**Planned Pro features:**

- 100+ fixtures
- more PDF, OCR, CSV, Unicode and archive edge cases
- compound cases combining multiple failure conditions
- machine-readable ground truth
- integrity verification
- commercial-use license
- one-time purchase — no subscription

**Early access price: ¥4,500 (approximately US$29)**

> Pro is not available for download yet.  
> If you want to be notified when it becomes available, join the early-access list.

[Join the Pro early-access list →](https://docs.google.com/forms/d/e/1FAIpQLSfGc_Q2munmzZwWe7oiaPlwHi-ra1tWBkliqxOROvuSBJOxRg/viewform)

---

## Layout

```text
cases/<id>/            input.*, expected.json, README.md
schema/                expected.schema.json
manifest.json          id, category, path and features of every case
tools/verify.py        integrity verification
tools/gen/             fixture generation scripts and shared helpers
fonts/                 BIZ UDGothic Regular and its license
```

`schema/expected.schema.json` uses JSON Schema 2020-12 and validates every `expected.json`.

---

## Verify the pack

Requires Python 3.10 or later.

```sh
pip install -r requirements.txt
python tools/verify.py
```

For every case listed in `manifest.json`, `verify.py` checks:

1. required files exist
2. `expected.json` passes the JSON Schema
3. the SHA-256 of the input matches `input.sha256`

Example output:

```text
OK pdf-001
OK csv-001
OK archive-001
...
```

The verifier does **not** parse PDFs, run OCR, interpret CSV content or access the network.

It only verifies the integrity and structure of the fixture pack itself.

---

## Regenerate fixtures

The committed fixtures are authoritative.

Their SHA-256 values are recorded in `expected.json`. Generation scripts are included so fixtures can be reproduced or modified.

With the currently pinned dependencies, the scripts reproduce the committed files byte-for-byte. Byte-for-byte reproduction is not guaranteed across different library or font versions.

Generation uses Python 3.14 (Unicode 16.0.0) and works entirely offline.

```sh
pip install -r requirements-gen.txt

python tools/gen/pdf_001.py
# or another tools/gen/<case>.py

python tools/gen/manifest.py
python tools/verify.py
```

Each generator:

1. creates `cases/<id>/input.*`
2. reads the generated file back where appropriate
3. verifies the facts that will become ground truth
4. writes `expected.json`
5. records the resulting SHA-256

PDF fixtures are read back with `pypdf` after generation.

Case `README.md` files are maintained manually and are never overwritten.

If regeneration changes a fixture's SHA-256, review the changes to both `input.*` and `expected.json` before committing them.

---

## Safety

The fixtures are intentionally designed to exercise edge cases without containing active or executable payloads.

- All names, shops, addresses, phone numbers and amounts are fictional.
- PDFs contain no JavaScript, actions, links, annotations or embedded files.
- CSV cells never start with `=`, `+`, `-` or `@`.
- The ZIP contains only short text files.
- The ZIP contains no executables, links, nested archives, absolute paths or `..`.
- Text files contain no bidirectional control characters.

**"Safe" means that this repository does not intentionally include executable or active malicious payloads. It is not a security guarantee for software processing arbitrary files.**

---

## License

### Code

`tools/` and `tests/` are licensed under the MIT License.

See [LICENSE](LICENSE).

### Lite fixture data

`cases/`, `schema/` and `manifest.json` are released under CC0 1.0.

See [LICENSE-DATA](LICENSE-DATA).

### Third-party material

BIZ UDGothic in `fonts/` is distributed under the SIL Open Font License 1.1.

See [fonts/OFL.txt](fonts/OFL.txt).

These licenses apply to the **Lite edition only**.

They do not apply to the future Pro edition, which will use a separate commercial license.