import unicodedata

VARIATION_SELECTORS = [(0xFE00, 0xFE0F), (0xE0100, 0xE01EF)]
TAG_BLOCK = [(0xE0000, 0xE007F)]

SPACE_VARIANTS = {
    cp for cp in range(0x110000)
    if cp != 0x20 and unicodedata.category(chr(cp)) == "Zs"
}

LINE_SEPARATOR_VARIANTS = {0x0085, 0x2028, 0x2029}

OTHER_INVISIBLE = {
    0x00AD,
    0x180E,
    0x034F,
    0x3164,
}
EMOJI_RANGES = [(0x1F300, 0x1FAFF), (0x2600, 0x27BF), (0x1F1E6, 0x1F1FF)]

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
