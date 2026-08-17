"""Runs text through independent AI-detection tools to check whether stylistic
AI tells got fully removed. Not part of the nowatermark package itself --
a dev/test helper for validating the no-watermark skill's stop-slop pass.

Usage: python scripts/verify_humanization.py <file>

Detectors, in order of how different their approach is:
  1. aifingerprint  (pip install aifingerprint)      - heuristic style scorer
  2. ai-slop-detect (pip install git+https://github.com/antydizajn/ai-slop-detect)
                                                       - deterministic phrase/char matcher
  3. roberta-base-openai-detector (needs torch+transformers, ~500MB model download)
                                                       - real ML classifier (optional, heavy)

Each is optional -- missing ones are skipped, not fatal.
"""
import sys

path = sys.argv[1]
text = open(path, encoding="utf-8").read()
print(f"##### {path} #####")

try:
    import aifingerprint
    score, results = aifingerprint.analyze(text)
    print(f"\n--- aifingerprint (style heuristic) ---")
    print(f"score: {score} ({aifingerprint.score_label(score)})")
    for category, (hits, raw) in results.items():
        if hits:
            print(f"  [{category}] raw={raw} hits={hits[:5]}")
except ImportError:
    print("\n--- aifingerprint: not installed (pip install aifingerprint) ---")

try:
    from ai_slop_detect import scan_text, score as slop_score
    hits = scan_text(text)
    print(f"\n--- ai-slop-detect (phrase/pattern) ---")
    print(slop_score(text, hits))
    for h in hits[:15]:
        print(f"  {h}")
except ImportError:
    print("\n--- ai-slop-detect: not installed "
          "(pip install git+https://github.com/antydizajn/ai-slop-detect) ---")

try:
    from transformers import pipeline
    clf = pipeline("text-classification", model="openai-community/roberta-base-openai-detector")
    result = clf(text[:512])
    print(f"\n--- roberta-base-openai-detector (ML classifier) ---")
    print(result)
except ImportError:
    print("\n--- roberta-base-openai-detector: not installed (pip install torch transformers) ---")
