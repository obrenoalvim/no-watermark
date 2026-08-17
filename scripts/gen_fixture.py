text = (
    "This is AI​ generated‌ text with‍ watermark﻿ chars. "
    "It has non-breaking spaces　too, and­soft hyphens."
)
with open("tests/fixtures/watermarked_sample.txt", "w", encoding="utf-8") as f:
    f.write(text)
print(repr(text))
