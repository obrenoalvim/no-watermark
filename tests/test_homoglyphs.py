from nowatermark.homoglyphs import find_mixed_script_words


def test_pure_latin_word_not_flagged():
    assert find_mixed_script_words("hello world") == []


def test_pure_cyrillic_word_not_flagged():
    text = "Привет мир"
    assert find_mixed_script_words(text) == []


def test_word_mixing_latin_and_cyrillic_is_flagged():
    text = "this word has an аttack inside it"
    matches = find_mixed_script_words(text)
    assert len(matches) == 1
    assert matches[0]["word"] == "аttack"
    assert set(matches[0]["scripts"]) == {"Latin", "Cyrillic"}


def test_word_mixing_latin_and_greek_is_flagged():
    text = "lοgin page"
    matches = find_mixed_script_words(text)
    assert len(matches) == 1
    assert set(matches[0]["scripts"]) == {"Latin", "Greek"}


def test_multiple_mixed_words_all_flagged():
    text = "аpple and micrοsoft both compromised"
    matches = find_mixed_script_words(text)
    assert len(matches) == 2
