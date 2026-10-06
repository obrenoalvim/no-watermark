<div align="center">

<img src=".github/logo.svg" alt="no-watermark logo" width="120" height="120">

# no-watermark

**Find and strip the invisible characters hidden in your text.**<br>
Zero-width characters, variation selectors, tag-block steganography, bidi controls and look-alike spaces. A Python CLI and an agent skill.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/obrenoalvim/no-watermark?style=flat&logo=github&color=f472b6)](https://github.com/obrenoalvim/no-watermark/stargazers)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)

**English** · [Português](README.pt-BR.md) · [Español](README.es.md)

[Quick start](#quick-start) · [Example](#example) · [CLI usage](#cli-usage) · [What it removes](#what-it-removes) · [Emoji safety](#emoji-safety) · [Agent skill](#agent-skill) · [FAQ](#faq)

</div>

---

Detect and remove invisible-Unicode text watermarks: zero-width characters, variation selectors, Unicode tag-block steganography, bidi controls, and anomalous space substitution. Removal is 100% deterministic within this scope, and legitimate emoji sequences stay untouched by default.

Hidden characters can carry a payload you never see: a text watermark, or an instruction aimed at an AI model (known as ASCII smuggling or prompt injection through invisible characters). `nowatermark` shows you what is in the text and strips it.

**Out of scope:** statistical token-distribution watermarks (e.g. Kirchenbauer-style green/red list watermarking). Those require paraphrasing and cannot be removed with a removal guarantee, so this tool does not address them.

## Quick start

```bash
pip install git+https://github.com/obrenoalvim/no-watermark.git
nowatermark detect suspicious.txt
```

Needs Python 3.10 or newer. There is no PyPI release yet.

## Example

Try it on the fixture that ships with the repo (`tests/fixtures/watermarked_sample.txt`):

```console
$ nowatermark detect tests/fixtures/watermarked_sample.txt
U+200B ZERO WIDTH SPACE [format-char] x1
U+200C ZERO WIDTH NON-JOINER [format-char] x1
U+200D ZERO WIDTH JOINER [format-char] x1
U+FEFF ZERO WIDTH NO-BREAK SPACE [format-char] x1
U+3000 IDEOGRAPHIC SPACE [space-variant] x1
U+00AD SOFT HYPHEN [other-invisible] x1
total: 6 watermark character(s) found

$ nowatermark clean tests/fixtures/watermarked_sample.txt -o clean.txt --report
removed U+200B [format-char] x1
removed U+200C [format-char] x1
removed U+200D [format-char] x1
removed U+FEFF [format-char] x1
removed U+3000 [space-variant] x1
removed U+00AD [other-invisible] x1
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

Exit codes: `0` clean/success, `1` `detect` found watermark characters, `2` usage/IO error (missing file, invalid UTF-8, path is a directory). Errors print as a plain message to stderr, not as a Python traceback.

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

Space coverage comes from the full Unicode "Zs" category, not a hand-picked list. This matters because current LLM-watermarking research (e.g. [Innamark, IEEE Access 2025](https://arxiv.org/html/2502.12710)) watermarks text by substituting regular spaces with *any* visually identical Zs character, so partial coverage is easy to bypass.

## Homoglyph detection

`nowatermark detect` also flags words that mix Latin letters with visually identical Cyrillic or Greek ones (for example, a Cyrillic `а` swapped for a Latin `a`). This is a real technique for hiding a payload without any invisible character, and [independent research into the August 2026 wave of AI-watermark-remover tools](https://www.bleepingcomputer.com/news/security/ai-watermark-removers-flood-the-web-almost-none-can-prove-they-work/) confirms it is in use.

The report appears separately and never affects `detect`'s exit code. Mixing scripts inside a single word is rare in legitimate text but not impossible, so treat it as a signal to check, not a finding. `clean` does not touch these words, because rewriting visible characters is a lossier guarantee than stripping invisible ones (tracked in [TODO IMPROVEMENTS.md](TODO%20IMPROVEMENTS.md)).

## Emoji safety

ZWJ/ZWNJ and tag-block characters are also used legitimately in emoji (family/couple sequences, flag sequences) and in some scripts (ZWNJ in Indic text). By default, `nowatermark clean` will not strip these when adjacent to emoji codepoints or inside a valid flag-emoji tag sequence. Pass `--no-emoji-guard` to strip unconditionally.

`detect` reports every candidate character it finds, including a ZWJ inside an emoji sequence. A family emoji, for example, lists three ZERO WIDTH JOINER characters, and `clean` keeps them. So `detect` can exit with `1` on text that `clean` leaves unchanged. Read the report before acting on the exit code.

## Agent skill

`skill/SKILL.md` packages this as an installable skill for AI coding agents that support the SKILL.md format. Drop it into your agent's skills directory and it detects and cleans watermarks in text automatically during a session. The skill also calls the `stop-slop` skill for stylistic cleanup of the wording.

## Development

```bash
git clone https://github.com/obrenoalvim/no-watermark.git
cd no-watermark
pip install -e ".[dev]"
pytest -v
```

---

## FAQ

**Does it remove statistical AI-text watermarks?**
No. Those live in word choice, not in characters. Removing them takes paraphrasing, and no tool can promise a clean result.

**Will it break my emoji or non-Latin text?**
`clean` keeps ZWJ and flag sequences next to emoji by default. ZWJ and ZWNJ also appear legitimately in some scripts (ZWNJ in Indic text), so check the `--report` output before cleaning text in those scripts.

**Why does `detect` exit with 1 on a text that looks fine?**
Invisible characters are invisible. Run `detect` to see exactly which code points it found and where they sit.

## Related projects

[guillaumemeyer/watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) is a popular open-source app in the same space. Cross-checking against it added Private Use Area coverage here and tightened the flag-emoji preservation check.

## More Claude Code skills by the same author

- [**zero-drift**](https://github.com/obrenoalvim/zero-drift): keeps long sessions grounded with named replies and a living `TASK.md`.
- [**keep-improving**](https://github.com/obrenoalvim/keep-improving): an autonomous improvement loop with a ten-role review panel.
- [**unblock**](https://github.com/obrenoalvim/unblock): a 13-tool free fallback chain for web research that keeps trying.
- [**findable**](https://github.com/obrenoalvim/findable): SEO and GEO research that applies the safe fixes.

## Contributing

Found a character class that slips through, or a legitimate sequence that gets stripped? Open an issue or a PR. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [changelog](CHANGELOG.md).

## License

[MIT](LICENSE)

---

<div align="center">

If no-watermark found something hiding in your text, a ⭐ helps other people find it too.

<sub>**Topics:** unicode · zero-width-characters · invisible-characters · watermark · steganography · ascii-smuggling · prompt-injection · text-sanitizer · cli · python · security · claude-skill</sub>

</div>
