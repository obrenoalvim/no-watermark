from nowatermark.remover import clean


def test_clean_removes_zero_width_space():
    text = "hello​world"
    cleaned, report = clean(text)
    assert cleaned == "helloworld"
    assert len(report) == 1
    assert report[0]["codepoint"] == "U+200B"


def test_clean_leaves_normal_text_untouched():
    text = "hello world, café, naïve"
    cleaned, report = clean(text)
    assert cleaned == text
    assert report == []


def test_clean_normalizes_space_variants_to_ascii_space():
    text = "hello world　again"
    cleaned, report = clean(text)
    assert cleaned == "hello world again"
    assert len(report) == 1


def test_clean_removes_variation_selector():
    text = "text️more"
    cleaned, report = clean(text)
    assert cleaned == "textmore"


def test_clean_normalizes_ogham_space_mark():
    text = "hello" + chr(0x1680) + "world"
    cleaned, report = clean(text)
    assert cleaned == "hello world"
    assert report[0]["category"] == "space-variant"


def test_clean_normalizes_line_separator_variants_to_newline():
    text = (
        "line one" + chr(0x2028)
        + "line two" + chr(0x2029)
        + "line three" + chr(0x0085)
        + "line four"
    )
    cleaned, report = clean(text)
    assert cleaned == "line one\nline two\nline three\nline four"
    assert all(r["category"] == "line-separator-variant" for r in report)


def test_clean_removes_combining_grapheme_joiner():
    text = "a" + chr(0x034F) + "b"
    cleaned, report = clean(text)
    assert cleaned == "ab"
    assert report[0]["category"] == "other-invisible"


def test_clean_removes_hangul_compat_filler():
    text = "a" + chr(0x3164) + "b"
    cleaned, report = clean(text)
    assert cleaned == "ab"
    assert report[0]["category"] == "other-invisible"


def test_clean_preserves_zwj_adjacent_to_emoji():
    family = "\U0001F468‍\U0001F469‍\U0001F467‍\U0001F466"
    cleaned, report = clean(family)
    assert cleaned == family
    assert report == []


def test_clean_strips_zwj_not_adjacent_to_emoji():
    text = "a‍b"
    cleaned, report = clean(text)
    assert cleaned == "ab"
    assert len(report) == 1


def test_clean_preserves_flag_emoji_tag_sequence():
    england = "\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F"
    cleaned, report = clean(england)
    assert cleaned == england
    assert report == []


def test_clean_strips_incomplete_flag_tag_sequence():
    # Base flag emoji + tag chars but no terminating cancel tag -- not a
    # complete sequence, so the tag chars are contraband and get stripped;
    # the base emoji itself is never touched (it isn't in any blocklist).
    raw = "\U0001F3F4\U000E0067\U000E0062"
    cleaned, report = clean(raw)
    assert cleaned == "\U0001F3F4"
    assert len(report) == 2
    assert all(r["category"] == "tag-block" for r in report)


def test_clean_removes_private_use_area_chars():
    text = "hello" + chr(0xE000) + "world" + chr(0xF0000) + "!"
    cleaned, report = clean(text)
    assert cleaned == "helloworld!"
    assert all(r["category"] == "private-use" for r in report)


def test_clean_strips_payload_appended_after_valid_flag_sequence():
    # A complete, well-formed England flag (base + tags + cancel) followed
    # directly by MORE tag-range chars that are NOT part of any flag
    # sequence (no base emoji of their own). A naive "walk backward to any
    # flag emoji" check would wrongly preserve these too, since they're
    # contiguous tag-block chars connected back to the same base -- this is
    # exactly the gap closed this cycle by validating complete terminated
    # sequences instead.
    england = "\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F"
    smuggled_payload = "\U000E0078\U000E0079"  # tag chars 'x','y' -- no base, no cancel
    text = england + smuggled_payload
    cleaned, report = clean(text)
    assert cleaned == england  # flag intact, smuggled tail gone
    assert len(report) == 2
    assert all(r["category"] == "tag-block" for r in report)


def test_clean_no_emoji_guard_strips_everything():
    family = "\U0001F468‍\U0001F469"
    cleaned, report = clean(family, emoji_guard=False)
    assert cleaned == "\U0001F468\U0001F469"
    assert len(report) == 1


def test_clean_is_idempotent():
    text = "hello​world test️"
    once, _ = clean(text)
    twice, report_twice = clean(once)
    assert once == twice
    assert report_twice == []
