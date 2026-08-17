---
name: no-watermark
description: Detect and remove invisible-Unicode text watermarks (zero-width chars, variation selectors, tag-block steganography, anomalous spaces) AND stylistic AI-writing tells (em dashes, formulaic structure) that trip AI-content detectors. Use when the user asks to strip AI text watermarks, generate text that must pass as human-written, clean hidden Unicode characters, or remove invisible characters from text/files, or mentions "marca d'água", "watermark", "zero-width", "invisible characters", "detector".
dependencies:
  - stop-slop
---

# no-watermark

Two independent layers of AI-text detection, both must be cleared:

1. **Invisible-Unicode watermarking** — zero-width characters, variation selectors, Unicode tag-block steganography, bidi controls, anomalous space variants. Handled by the `nowatermark` CLI below. Deterministic, 100% removal within this scope. Does not touch legitimate emoji sequences (ZWJ emoji, flag sequences) unless `--no-emoji-guard` is passed.
2. **Stylistic AI-writing tells** — em dashes, formulaic structure, passive voice, adverb overuse, throat-clearing openers — the patterns AI-content detectors and human readers actually key on. Handled by the **stop-slop** skill (dependency — invoke it, don't reimplement its rules here).

Skipping either layer means the text still gets flagged. Both are required.

Out of scope: statistical token-distribution watermarks (Kirchenbauer-style) — those require paraphrasing and have no guaranteed-clean removal.

## Hard rule: no em dash

Never output `—` (em dash) in any text this skill touches, at generation time or during cleanup. This is the single most common AI tell. Use a period, comma, or parentheses instead. This rule applies even if stop-slop somehow misses one — check for it explicitly before delivering the final text.

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

1. Draft/obtain the text. If generating it yourself, write it without em dashes from the start.
2. **Invoke the stop-slop skill on the draft** to strip stylistic AI tells (em dashes, passive voice, formulaic structure, filler). Do this before the Unicode pass — stop-slop rewrites wording, `nowatermark` only strips characters, running them in the other order can reintroduce nothing but wastes a pass.
3. Scan the stop-slop output for `—` by hand and rewrite any that slipped through. Do not proceed until there are zero.
4. Get the text into a file or stdin, then run `nowatermark detect` and show the user what was found (codepoints + categories).
5. Run `nowatermark clean` to strip it.
6. Run `nowatermark detect` again on the cleaned output to confirm exit code 0 (zero matches). If it's not zero, something in step 5 failed — do not deliver the text as "clean" until this check passes.
7. Report to the user: what stylistic patterns stop-slop removed, what Unicode categories were stripped, and confirmation both checks are now clean. Do not silently overwrite the user's original file — write to a new path unless they ask to replace in place.
