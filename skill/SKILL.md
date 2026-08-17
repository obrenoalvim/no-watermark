---
name: no-watermark
description: Detect and remove invisible-Unicode text watermarks (zero-width chars, variation selectors, tag-block steganography, anomalous spaces). Use when the user asks to strip AI text watermarks, clean hidden Unicode characters, or remove invisible characters from text/files, or mentions "marca d'água", "watermark", "zero-width", "invisible characters".
---

# no-watermark

Detects and deterministically strips invisible-Unicode watermarking from text: zero-width characters, variation selectors, Unicode tag-block steganography, bidi controls, and anomalous space variants. Does not touch legitimate emoji sequences (ZWJ emoji, flag sequences) unless `--no-emoji-guard` is passed.

Out of scope: statistical token-distribution watermarks (Kirchenbauer-style) — those require paraphrasing and have no guaranteed-clean removal.

## Usage

Requires the `nowatermark` CLI on PATH (`pip install -e .` from the project root, or `pip install nowatermark` once published).

**Detect only:**
```bash
nowatermark detect <file>
# or: echo "$TEXT" | nowatermark detect -
```
Exit code 0 = clean, 1 = watermark characters found (prints a report to stdout).

**Clean text the user pasted or a file they reference:**
```bash
nowatermark clean <file> -o <file>.clean.txt --report
# or via stdin/stdout:
echo "$TEXT" | nowatermark clean -
```

## Workflow

1. Get the text — either a file path the user gives, or text they pasted directly (write it to a temp file or pipe via stdin).
2. Run `nowatermark detect` first and show the user what was found (codepoints + categories), so they know what was removed.
3. Run `nowatermark clean` to produce the cleaned version.
4. Report the diff in character count and which categories were stripped. Do not silently overwrite the user's original file — write to a new path unless they ask to replace in place.
