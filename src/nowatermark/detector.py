import unicodedata

VARIATION_SELECTORS = [(0xFE00, 0xFE0F), (0xE0100, 0xE01EF)]
TAG_BLOCK = [(0xE0000, 0xE007F)]
SPACE_VARIANTS = {
    0x00A0, 0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005,
    0x2006, 0x2007, 0x2008, 0x2009, 0x200A, 0x202F, 0x205F, 0x3000,
}
OTHER_INVISIBLE = {0x00AD, 0x180E}
EMOJI_RANGES = [(0x1F300, 0x1FAFF), (0x2600, 0x27BF), (0x1F1E6, 0x1F1FF)]


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
    if cp in OTHER_INVISIBLE:
        return "other-invisible"
    if unicodedata.category(chr(cp)) == "Cf":
        return "format-char"
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
