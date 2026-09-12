from nowatermark.homoglyphs import find_mixed_script_words


def test_pure_latin_word_not_flagged():
    assert find_mixed_script_words("hello world") == []


def test_pure_cyrillic_word_not_flagged():
    # a legitimate Russian word on its own is not suspicious
    text = "Привет мир"
    assert find_mixed_script_words(text) == []


def test_word_mixing_latin_and_cyrillic_is_flagged():
    # "hello" with Cyrillic а (U+0430) instead of Latin a
    text = "this word has an аttack inside it"
    matches = find_mixed_script_words(text)
    assert len(matches) == 1
    assert matches[0]["word"] == "аttack"
    assert set(matches[0]["scripts"]) == {"Latin", "Cyrillic"}


def test_word_mixing_latin_and_greek_is_flagged():
    # Greek omicron (U+03BF) instead of Latin o
    text = "lοgin page"
    matches = find_mixed_script_words(text)
    assert len(matches) == 1
    assert set(matches[0]["scripts"]) == {"Latin", "Greek"}


def test_multiple_mixed_words_all_flagged():
    text = "аpple and micrοsoft both compromised"
    matches = find_mixed_script_words(text)
    assert len(matches) == 2
