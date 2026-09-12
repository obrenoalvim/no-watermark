# no-watermark

*[Read in Portuguese / Leia em Português](README.pt-BR.md)*

Detect and remove invisible-Unicode text watermarks — zero-width characters, variation selectors, Unicode tag-block steganography, bidi controls, and anomalous space substitution. 100% deterministic removal within this scope; does not touch legitimate emoji sequences by default.

**Out of scope:** statistical token-distribution watermarks (e.g. Kirchenbauer-style green/red list watermarking). Those require paraphrasing and cannot be removed with a removal guarantee — not addressed by this tool.

## Install

```bash
pip install -e .
```

## CLI usage

```bash
# scan a file for watermark characters
nowatermark detect suspicious.txt

# clean a file, write to a new file, print what was removed
nowatermark clean suspicious.txt -o clean.txt --report

# pipe text through
echo "some text" | nowatermark clean -
```

Exit codes: `0` clean/success, `1` `detect` found watermark characters, `2` usage/IO error (missing file, invalid UTF-8, path is a directory) — printed as a plain message to stderr, not a Python traceback.

## What it removes

| Category | Examples | Action |
|---|---|---|
| Format chars (Unicode Cf) | zero-width space/joiner/non-joiner, word joiner, BOM, bidi controls | removed |
| Variation selectors | U+FE00–FE0F, U+E0100–E01EF | removed |
| Tag block | U+E0000–E007F | removed (unless part of a flag-emoji sequence) |
| Anomalous spaces | all 16 non-ASCII Unicode "Zs" space characters (NBSP, Ogham space mark, thin/hair/em/en spaces, ideographic space, etc.) | normalized to a regular space |
| Line separator variants | NEL (U+0085), LINE SEPARATOR (U+2028), PARAGRAPH SEPARATOR (U+2029) | normalized to `\n` |
| Private Use Area | U+E000–F8FF (BMP) plus both supplementary PUA planes | removed |
| Other | soft hyphen, Mongolian vowel separator, combining grapheme joiner, Hangul compatibility filler (U+3164) | removed |

Space coverage is derived from the full Unicode "Zs" category, not a hand-picked list — this matters because current LLM-watermarking research (e.g. [Innamark, IEEE Access 2025](https://arxiv.org/html/2502.12710)) watermarks text by substituting regular spaces with *any* visually-identical Zs character, so partial coverage is easy to bypass.

Cross-checked against [guillaumemeyer/watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) (13k+ stars, the leading open-source tool in this space as of August 2026) to close two gaps: Private Use Area coverage was missing entirely, and the flag-emoji preservation check used a backward walk that could be tricked into also preserving payload characters appended right after a legitimate flag sequence's terminating cancel tag. Both are fixed as of this cycle.

## Homoglyph detection (heuristic, detection-only)

`nowatermark detect` also flags words that mix Latin letters with visually-identical Cyrillic or Greek ones (e.g. Cyrillic `а` swapped for Latin `a`) — a real technique for hiding a payload without any invisible character at all, confirmed as currently in use by [independent research into the August 2026 AI-watermark-remover tooling wave](https://www.bleepingcomputer.com/news/security/ai-watermark-removers-flood-the-web-almost-none-can-prove-they-work/). This is reported separately and never affects `detect`'s exit code — mixing scripts within a single word is rare in legitimate text but not impossible, so it's a signal to check, not a deterministic finding. `clean` does not touch these (auto-rewriting visible characters is a different, lossier guarantee than stripping invisible ones — see `TODO IMPROVEMENTS.md`).

## Emoji safety

ZWJ/ZWNJ and tag-block characters are also used legitimately in emoji (family/couple sequences, flag sequences) and in some scripts (ZWNJ in Indic text). By default, `nowatermark` will not strip these when adjacent to emoji codepoints or inside a valid flag-emoji tag sequence. Pass `--no-emoji-guard` to strip unconditionally.

## Agent skill

`skill/SKILL.md` packages this as an installable skill for AI coding agents that support the SKILL.md format — drop it into your agent's skills directory to have it detect/clean watermarks in text automatically during a session.

## Development

```bash
pip install -e ".[dev]"
pytest -v
```
