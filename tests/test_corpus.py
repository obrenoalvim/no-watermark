from pathlib import Path
from nowatermark.detector import scan
from nowatermark.remover import clean

FIXTURES = Path(__file__).parent / "fixtures"


def test_clean_sample_is_unchanged_by_clean():
    text = (FIXTURES / "clean_sample.txt").read_text(encoding="utf-8")
    cleaned, report = clean(text)
    assert cleaned == text
    assert report == []


def test_watermarked_sample_has_zero_matches_after_clean():
    text = (FIXTURES / "watermarked_sample.txt").read_text(encoding="utf-8")
    assert len(scan(text)) > 0  # sanity: fixture actually has watermark chars
    cleaned, _ = clean(text)
    assert scan(cleaned) == []


def test_family_emoji_survives_full_pipeline():
    family = "\U0001F468‍\U0001F469‍\U0001F467‍\U0001F466"
    text = f"before {family} after"
    cleaned, _ = clean(text)
    assert family in cleaned


def test_idempotent_on_corpus():
    for name in ("clean_sample.txt", "watermarked_sample.txt"):
        text = (FIXTURES / name).read_text(encoding="utf-8")
        once, _ = clean(text)
        twice, report2 = clean(once)
        assert once == twice
        assert report2 == []
