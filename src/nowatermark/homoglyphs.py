"""Detects (but never modifies) suspected homoglyph substitution -- swapping
Latin letters for visually-identical Cyrillic/Greek ones to encode a payload
without any invisible character at all. Confirmed as a real, currently-used
technique by independent research into the August 2026 wave of AI-watermark
tooling (pasqualepillitteri.it's text analyzer flags exactly this class).

Detection only, by design: a mixed-script word is a strong signal but not
proof (legitimate text can mix scripts, e.g. a Russian name mid-sentence).
Auto-normalizing would be lossy and is deliberately not implemented here --
see TODO IMPROVEMENTS.md.
"""
import unicodedata

SCRIPT_RANGES = {
    "Latin": [(0x0041, 0x024F)],
    "Cyrillic": [(0x0400, 0x04FF)],
    "Greek": [(0x0370, 0x03FF)],
}


def _scripts_of(ch: str) -> set[str]:
    cp = ord(ch)
    return {
        name for name, ranges in SCRIPT_RANGES.items()
        if any(lo <= cp <= hi for lo, hi in ranges)
    }


def find_mixed_script_words(text: str) -> list[dict]:
    matches = []
    word_start = None
    word_scripts: set[str] = set()

    def flush(end):
        if word_start is not None and len(word_scripts) > 1:
            matches.append({
                "index": word_start,
                "word": text[word_start:end],
                "scripts": sorted(word_scripts),
            })

    for i, ch in enumerate(text):
        if unicodedata.category(ch).startswith("L"):
            if word_start is None:
                word_start = i
                word_scripts = set()
            word_scripts |= _scripts_of(ch)
        else:
            flush(i)
            word_start = None
            word_scripts = set()
    flush(len(text))

    return matches
