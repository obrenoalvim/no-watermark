# TODO IMPROVEMENTS

> Last updated: 2026-08-17

## Pending Changes

### Trailing-whitespace stripping (SNOW steganography)
- **Category:** Feature
- **Source:** https://darkside.com.au/snow/ (SNOW tool), https://arxiv.org/html/2502.12710 (Innamark, IEEE Access 2025)
- **What:** Strip trailing spaces/tabs at the end of each line. SNOW is a decades-old, well-documented steganography technique that hides a payload in trailing whitespace, which is invisible in virtually all text renderers.
- **Where:** New function in `src/nowatermark/remover.py` (e.g. `_strip_trailing_whitespace`), called from `clean()`; new `detector.py` category `"trailing-whitespace"`.
- **Why:** Currently completely undetected — `nowatermark` only classifies individual codepoints, and this technique uses ordinary space/tab characters at an unusual *position* (line end), not a special codepoint. Real gap in the tool's stated goal of "detect and remove invisible-Unicode watermarking."
- **Risk:** Markdown uses exactly two trailing spaces at end of line as a hard line-break convention (widely used). Blanket stripping would silently break that formatting for any Markdown source passed through `clean()`. Needs either an opt-in flag (default off) or a Markdown-aware exception (skip stripping when exactly 2 trailing spaces). Product call: is breaking that convention acceptable for a tool whose whole point is "strip anything invisible," or does it need the exception?
- **Effort:** Low (the strip itself is a few lines; the design decision is what takes judgment)

### Homoglyph / lookalike-character normalization
- **Category:** Feature
- **Source:** https://bunnylab.github.io/unicode-steganography (`pyUnicodeSteganography`, "lookalike" method), general research on Unicode confusables/homoglyph watermarking
- **What:** Detect and optionally normalize visually-identical cross-script substitutions (e.g. Cyrillic а/е/о/р/с/х swapped for Latin a/e/o/p/c/x) used to encode a payload without any invisible character at all.
- **Where:** New `src/nowatermark/homoglyphs.py` with a confusables table (Unicode publishes an official `confusables.txt`); new CLI flag, e.g. `nowatermark clean --normalize-homoglyphs`.
- **Why:** This is a real, documented watermarking/steganography technique the current tool has zero coverage for — it doesn't touch invisible characters at all, so no amount of Cf/Zs-category completeness catches it.
- **Risk:** This changes *visible* characters, not invisible ones — it's fundamentally different from the rest of the tool's guarantees. It's lossy for legitimate non-Latin-script text (Russian, Greek, Serbian names/words mixed into otherwise-English prose) and there's no reliable way to tell "3 legitimate Cyrillic characters in a quote" from "3 homoglyphs encoding a watermark bit" without added heuristics (script-consistency checks per word). Must ship opt-in only, off by default, clearly documented as lossy/heuristic — not part of the tool's "100% deterministic" claim.
- **Effort:** Medium (confusables table is available pre-built from Unicode; the false-positive-avoidance heuristic is the real work)
