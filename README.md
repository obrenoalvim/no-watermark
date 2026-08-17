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

`clean` exits 0 always. `detect` exits 1 if it found anything (useful in scripts/CI).

## What it removes

| Category | Examples | Action |
|---|---|---|
| Format chars (Unicode Cf) | zero-width space/joiner/non-joiner, word joiner, BOM, bidi controls | removed |
| Variation selectors | U+FE00–FE0F, U+E0100–E01EF | removed |
| Tag block | U+E0000–E007F | removed (unless part of a flag-emoji sequence) |
| Anomalous spaces | all 16 non-ASCII Unicode "Zs" space characters (NBSP, Ogham space mark, thin/hair/em/en spaces, ideographic space, etc.) | normalized to a regular space |
| Line separator variants | NEL (U+0085), LINE SEPARATOR (U+2028), PARAGRAPH SEPARATOR (U+2029) | normalized to `\n` |
| Other | soft hyphen, Mongolian vowel separator, combining grapheme joiner | removed |

Space coverage is derived from the full Unicode "Zs" category, not a hand-picked list — this matters because current LLM-watermarking research (e.g. [Innamark, IEEE Access 2025](https://arxiv.org/html/2502.12710)) watermarks text by substituting regular spaces with *any* visually-identical Zs character, so partial coverage is easy to bypass.

## Emoji safety

ZWJ/ZWNJ and tag-block characters are also used legitimately in emoji (family/couple sequences, flag sequences) and in some scripts (ZWNJ in Indic text). By default, `nowatermark` will not strip these when adjacent to emoji codepoints or inside a valid flag-emoji tag sequence. Pass `--no-emoji-guard` to strip unconditionally.

## agent skill

See `skill/SKILL.md` — install into your agent skills directory to let the AI agent detect/clean watermarks in text you paste or reference during a conversation.

## Development

```bash
pip install -e ".[dev]"
pytest -v
```
