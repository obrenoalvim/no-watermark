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
7. If `scripts/verify_humanization.py` and its detector libraries are available, run it on the final text as an extra check (see "Verification against real detectors" below). Not required to complete the task, but run it when available — it catches things the checklist misses.
8. Report to the user: what stylistic patterns stop-slop removed, what Unicode categories were stripped, and confirmation both checks are now clean. Do not silently overwrite the user's original file — write to a new path unless they ask to replace in place.

## Humanization checklist (validated against real detectors)

Tested against three independent tools with different detection approaches (heuristic style scoring, phrase/pattern matching, ML classifier) — a corporate-style AI-generated paragraph went from `ai-slop-detect` score 54/LIKELY_AI to 0/HUMAN_LIKE, and `aifingerprint` from 39 to ~23, by applying these on top of stop-slop's base rules:

- **No em dash.** Already a hard rule above, also the single most common flag across every tool tested.
- **No hedging openers**: "it's important to note", "it's worth noting". Say the thing directly.
- **No formulaic transition/closer words as sentence-openers**: "Furthermore,", "Nevertheless,", "In conclusion,". Cut them, the sentence usually stands fine without.
- **Avoid stock AI vocabulary**: streamline, unlock, enhance, landscape (as in "digital landscape"), fast-paced, robust, seamless, boundless, delve, moreover. Use a plain, specific word instead.
- **Vary sentence length inside a paragraph (burstiness).** Mixing one long sentence with two short ones beats three same-length sentences in a row. Chopping everything into uniform short sentences is itself a tell (metronomic rhythm) — don't overcorrect into that.
- **Vary sentence count between paragraphs.** All-3-sentence paragraphs read as templated. Let one run 2, another run 4.
- **Occasionally start a sentence with a conjunction** (But/And/So). AI text avoids this; human text does it naturally.
- **Vary punctuation beyond periods/commas** — a question mark, a semicolon, a parenthetical aside.
- **Replace vague declaratives with a specific claim.** Not "the implications are significant" — say which implication.
- **Keep at least one concrete, idiosyncratic detail per paragraph** where the topic allows it. Generic corporate-topic text scores high on some detectors' "compression similarity to known AI corpus" check regardless of style; specifics are the main lever for that one and it doesn't fully zero out on short generic text — don't chase a perfect score past this point, it's a property of the topic, not a sign the text still reads as AI.

## Verification against real detectors (optional, for testing)

`scripts/verify_humanization.py` in this repo runs a file through three independently-approached open-source detectors, none requiring a paid API key:

```bash
pip install aifingerprint
pip install git+https://github.com/antydizajn/ai-slop-detect
pip install torch transformers   # optional, heavy (~500MB model download) — real ML classifier
python scripts/verify_humanization.py path/to/text.txt
```

Each library is optional and skipped if not installed. This is a dev/test tool, not a runtime dependency of `nowatermark` — use it to validate the checklist above is actually working on real output, not to gate every single skill invocation.
