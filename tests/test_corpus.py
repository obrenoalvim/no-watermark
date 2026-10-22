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
    assert len(scan(text)) > 0
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


def _encode_variation_selector_payload(message: str) -> str:
    out = []
    for byte in message.encode("utf-8"):
        if byte < 16:
            out.append(chr(0xFE00 + byte))
        else:
            out.append(chr(0xE0100 + (byte - 16)))
    return "".join(out)


def test_full_variation_selector_payload_is_completely_destroyed():
    payload = _encode_variation_selector_payload("SECRET-PAYLOAD-42")
    text = f"This looks like ordinary text.{payload} Nothing to see here."
    assert len(payload) > 10
    assert len(scan(text)) >= len(payload)

    cleaned, report = clean(text)
    assert scan(cleaned) == []
    assert all(chr(cp) not in cleaned for cp in range(0xFE00, 0xFE10))
    assert not any(0xE0100 <= ord(ch) <= 0xE01EF for ch in cleaned)
    assert cleaned == "This looks like ordinary text. Nothing to see here."


def _encode_sneaky_bits_payload(message: str) -> str:
    bits = "".join(f"{byte:08b}" for byte in message.encode("utf-8"))
    return "".join(chr(0x2064) if b == "1" else chr(0x2062) for b in bits)


def test_sneaky_bits_payload_is_completely_destroyed():
    payload = _encode_sneaky_bits_payload("hidden")
    text = f"Nothing unusual here.{payload} Just a normal sentence."
    assert len(payload) == 6 * 8
    assert len(scan(text)) == len(payload)

    cleaned, report = clean(text)
    assert scan(cleaned) == []
    assert chr(0x2062) not in cleaned and chr(0x2064) not in cleaned
    assert cleaned == "Nothing unusual here. Just a normal sentence."


SLOP_BANNED_PHRASES = [
    "it's important to note", "it's worth noting", "furthermore,",
    "nevertheless,", "in conclusion,", "streamline", "unlock", "landscape",
    "fast-paced", "seamless", "boundless", "delve", "moreover",
]


def test_ai_slop_draft_has_em_dashes_and_banned_phrases():
    draft = (FIXTURES / "ai_slop_draft.txt").read_text(encoding="utf-8")
    assert "—" in draft
    low = draft.lower()
    assert any(p in low for p in SLOP_BANNED_PHRASES)


def test_ai_slop_cleaned_has_no_em_dash_or_banned_phrases():
    cleaned = (FIXTURES / "ai_slop_cleaned.txt").read_text(encoding="utf-8")
    assert "—" not in cleaned
    low = cleaned.lower()
    assert not any(p in low for p in SLOP_BANNED_PHRASES)
