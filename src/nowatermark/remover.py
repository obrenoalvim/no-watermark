from .detector import classify, is_emoji

ZWJ = 0x200D
ZWNJ = 0x200C
TAG_BASE_EMOJI = 0x1F3F4
TAG_RANGE_LOW = 0xE0000
TAG_RANGE_HIGH = 0xE007F


def _is_flag_tag_sequence_char(text: str, i: int) -> bool:
    j = i
    while j >= 0 and TAG_RANGE_LOW <= ord(text[j]) <= TAG_RANGE_HIGH:
        j -= 1
    return j >= 0 and ord(text[j]) == TAG_BASE_EMOJI


def clean(text: str, emoji_guard: bool = True) -> tuple[str, list[dict]]:
    result = []
    report = []
    n = len(text)
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

        if emoji_guard and category == "tag-block":
            if _is_flag_tag_sequence_char(text, i):
                result.append(ch)
                continue

        if category == "space-variant":
            result.append(" ")
        elif category == "line-separator-variant":
            result.append("\n")
        report.append({"codepoint": f"U+{cp:04X}", "category": category})

    return "".join(result), report
