from nowatermark.detector import classify, is_emoji, scan


def test_classify_zero_width_space_is_format_char():
    assert classify(0x200B) == "format-char"


def test_classify_variation_selector():
    assert classify(0xFE0F) == "variation-selector"
    assert classify(0xE0100) == "variation-selector"


def test_classify_tag_block():
    assert classify(0xE0001) == "tag-block"


def test_classify_space_variant():
    assert classify(0x00A0) == "space-variant"
    assert classify(0x3000) == "space-variant"


def test_classify_soft_hyphen_and_mongolian_separator():
    assert classify(0x00AD) == "other-invisible"
    assert classify(0x180E) == "other-invisible"


def test_classify_normal_ascii_returns_none():
    assert classify(ord("a")) is None
    assert classify(ord(" ")) is None


def test_is_emoji():
    assert is_emoji(0x1F600) is True
    assert is_emoji(ord("a")) is False


def test_scan_finds_zero_width_space():
    text = "hello​world"
    matches = scan(text)
    assert len(matches) == 1
    assert matches[0]["codepoint"] == "U+200B"
    assert matches[0]["category"] == "format-char"
    assert matches[0]["index"] == 5


def test_scan_clean_text_returns_empty():
    assert scan("hello world, café") == []
