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


def _encode_variation_selector_payload(message: str) -> str:
    # Real-world technique (documented August 2026 in the AI-watermark-remover
    # coverage this cycle researched): map each byte of a hidden message to
    # one of the 256 variation-selector codepoints (16 in U+FE00-FE0F plus
    # 240 in U+E0100-E01EF) and append them after a visible base character.
    # A competing open-source cleaner was found to let this exact class of
    # payload survive its "cleaning" -- this test proves ours doesn't.
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
    assert len(payload) > 10  # sanity: payload actually has many VS chars
    assert len(scan(text)) >= len(payload)

    cleaned, report = clean(text)
    # every single variation-selector byte must be gone, not just some
    assert scan(cleaned) == []
    assert all(chr(cp) not in cleaned for cp in range(0xFE00, 0xFE10))
    assert not any(0xE0100 <= ord(ch) <= 0xE01EF for ch in cleaned)
    assert cleaned == "This looks like ordinary text. Nothing to see here."


def _encode_sneaky_bits_payload(message: str) -> str:
    # "Sneaky Bits" (Johann Rehberger, embracethered.com, 2025; now a named
    # NVIDIA garak probe -- encoding.InjectSneakyBits): encodes each bit of
    # a message as one of two invisible Unicode math operators -- U+2062
    # INVISIBLE TIMES for 0, U+2064 INVISIBLE PLUS for 1. No dedicated
    # handling was ever added for this on purpose: both codepoints are
    # already Unicode category Cf, so the tool's generic Cf fallback (in
    # place since the very first version of detector.py) catches them
    # without needing to know the technique by name. This test makes that
    # coverage explicit and regression-proof.
    bits = "".join(f"{byte:08b}" for byte in message.encode("utf-8"))
    return "".join(chr(0x2064) if b == "1" else chr(0x2062) for b in bits)


def test_sneaky_bits_payload_is_completely_destroyed():
    payload = _encode_sneaky_bits_payload("hidden")
    text = f"Nothing unusual here.{payload} Just a normal sentence."
    assert len(payload) == 6 * 8  # sanity: 6 ASCII chars, 8 bits each
    assert len(scan(text)) == len(payload)

    cleaned, report = clean(text)
    assert scan(cleaned) == []
    assert chr(0x2062) not in cleaned and chr(0x2064) not in cleaned
    assert cleaned == "Nothing unusual here. Just a normal sentence."


# ai_slop_draft.txt / ai_slop_cleaned.txt are the actual before/after pair
# SKILL.md's "Humanization checklist" section cites for its validated
# detector-score claims (ai-slop-detect 54/LIKELY_AI -> 0/HUMAN_LIKE,
# aifingerprint 39 -> ~23). These assertions check the checklist's own
# stated rules against that pair so the fixtures stay load-bearing instead
# of silently drifting from what the docs claim about them.
SLOP_BANNED_PHRASES = [
    "it's important to note", "it's worth noting", "furthermore,",
    "nevertheless,", "in conclusion,", "streamline", "unlock", "landscape",
    "fast-paced", "seamless", "boundless", "delve", "moreover",
]


def test_ai_slop_draft_has_em_dashes_and_banned_phrases():
    # sanity: the "before" fixture must actually exhibit what the "after"
    # fixture and the checklist claim to fix, or this pair proves nothing.
    draft = (FIXTURES / "ai_slop_draft.txt").read_text(encoding="utf-8")
    assert "—" in draft
    low = draft.lower()
    assert any(p in low for p in SLOP_BANNED_PHRASES)


def test_ai_slop_cleaned_has_no_em_dash_or_banned_phrases():
    cleaned = (FIXTURES / "ai_slop_cleaned.txt").read_text(encoding="utf-8")
    assert "—" not in cleaned
    low = cleaned.lower()
    assert not any(p in low for p in SLOP_BANNED_PHRASES)
