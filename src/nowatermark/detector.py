import unicodedata

VARIATION_SELECTORS = [(0xFE00, 0xFE0F), (0xE0100, 0xE01EF)]
TAG_BLOCK = [(0xE0000, 0xE007F)]

# Derived from the full Unicode "Zs" (space separator) category rather than
# hand-listed: research on LLM watermarking (Innamark, IEEE Access 2025)
# shows watermarks substitute regular spaces with *any* visually-identical
# Zs character, so the blocklist must cover the whole category, not a
# hand-picked subset. U+0020 (the normal space) is excluded on purpose --
# it's the normalization target, not something to flag.
SPACE_VARIANTS = {
    cp for cp in range(0x110000)
    if cp != 0x20 and unicodedata.category(chr(cp)) == "Zs"
}

# NEL, LINE SEPARATOR, PARAGRAPH SEPARATOR: alternate line-break encodings
# with zero visual difference from "\n" in a rendered document -- a watermark
# can pick between them to encode bits the same way it picks between spaces.
LINE_SEPARATOR_VARIANTS = {0x0085, 0x2028, 0x2029}

OTHER_INVISIBLE = {
    0x00AD,  # soft hyphen
    0x180E,  # Mongolian vowel separator
    0x034F,  # combining grapheme joiner -- invisible, category Mn like
             # variation selectors, but not a legitimate diacritic itself
    0x3164,  # Hangul filler (Hangul Compatibility Jamo block) -- unlike the
             # Hangul Jamo fillers at U+115F/1160, this one has no script-glue
             # role; it's a legacy IME placeholder with no legitimate use in
             # prose, and is independently flagged as always-strip (no
             # adjacency check) by a second reference tool
             # (mikiane/claude-watermark-cleaner).
}
EMOJI_RANGES = [(0x1F300, 0x1FAFF), (0x2600, 0x27BF), (0x1F1E6, 0x1F1FF)]

# Private Use Area (BMP + both supplementary PUA planes): no portable meaning
# across systems -- renders as tofu/blank without a custom font mapping --
# and a documented steganography vector (arbitrary payload as a PUA
# codepoint sequence). Cross-checked against the leading open-source tool in
# this space (guillaumemeyer/watermarks-remover, 13k+ stars) which strips
# the same ranges for the same reason.
PRIVATE_USE_RANGES = [(0xE000, 0xF8FF), (0xF0000, 0xFFFFD), (0x100000, 0x10FFFD)]


def _in_ranges(cp, ranges):
    return any(lo <= cp <= hi for lo, hi in ranges)


def is_emoji(cp: int) -> bool:
    return _in_ranges(cp, EMOJI_RANGES)


def classify(cp: int) -> str | None:
    if _in_ranges(cp, VARIATION_SELECTORS):
        return "variation-selector"
    if _in_ranges(cp, TAG_BLOCK):
        return "tag-block"
    if cp in SPACE_VARIANTS:
        return "space-variant"
    if cp in LINE_SEPARATOR_VARIANTS:
        return "line-separator-variant"
    if cp in OTHER_INVISIBLE:
        return "other-invisible"
    if unicodedata.category(chr(cp)) == "Cf":
        return "format-char"
    if _in_ranges(cp, PRIVATE_USE_RANGES):
        return "private-use"
    return None


def scan(text: str) -> list[dict]:
    matches = []
    for i, ch in enumerate(text):
        cp = ord(ch)
        category = classify(cp)
        if category is not None:
            matches.append({
                "index": i,
                "codepoint": f"U+{cp:04X}",
                "name": unicodedata.name(ch, "UNKNOWN"),
                "category": category,
            })
    return matches
