from .detector import classify, is_emoji

ZWJ = 0x200D
ZWNJ = 0x200C
TAG_BASE_EMOJI = 0x1F3F4
TAG_CHAR_LOW = 0xE0020
TAG_CHAR_HIGH = 0xE007E
TAG_CANCEL = 0xE007F


def _valid_flag_tag_indices(text: str) -> set[int]:
    """Indices belonging to a complete, well-formed subdivision-flag tag
    sequence: base flag emoji, one or more tag chars, and the terminating
    cancel tag. A naive "any tag-block char reachable by walking backward to
    a flag emoji" check (the previous approach here) would also preserve
    payload chars appended right after a real sequence's cancel tag, since
    the cancel tag is itself in the tag-block range and doesn't break that
    backward walk. Forward-scanning for exact, terminated sequences closes
    that hole."""
    valid: set[int] = set()
    i = 0
    n = len(text)
    while i < n:
        if ord(text[i]) != TAG_BASE_EMOJI:
            i += 1
            continue
        j = i + 1
        while j < n and TAG_CHAR_LOW <= ord(text[j]) <= TAG_CHAR_HIGH:
            j += 1
        if j > i + 1 and j < n and ord(text[j]) == TAG_CANCEL:
            valid.update(range(i + 1, j + 1))
            i = j + 1
        else:
            i += 1
    return valid


def clean(text: str, emoji_guard: bool = True) -> tuple[str, list[dict]]:
    result = []
    report = []
    n = len(text)
    valid_flag_tags = _valid_flag_tag_indices(text) if emoji_guard else set()
    for i, ch in enumerate(text):
        cp = ord(ch)
        category = classify(cp)
        if category is None:
            result.append(ch)
            continue

        if emoji_guard and cp in (ZWJ, ZWNJ):
            prev_cp = ord(text[i - 1]) if i > 0 else None
            next_cp = ord(text[i + 1]) if i + 1 < n else None
            if (prev_cp is not None and is_emoji(prev_cp)) or (
                next_cp is not None and is_emoji(next_cp)
            ):
                result.append(ch)
                continue

        if emoji_guard and category == "tag-block" and i in valid_flag_tags:
            result.append(ch)
            continue

        if category == "space-variant":
            result.append(" ")
        elif category == "line-separator-variant":
            result.append("\n")
        report.append({"codepoint": f"U+{cp:04X}", "category": category})

    return "".join(result), report
