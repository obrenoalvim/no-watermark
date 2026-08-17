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
