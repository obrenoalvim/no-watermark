import argparse
import sys
from collections import Counter

from .detector import scan
from .remover import clean


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _cmd_detect(args) -> int:
    text = _read_input(args.input)
    matches = scan(text)
    if not matches:
        print("clean: no watermark characters found")
        return 0
    counts = Counter((m["codepoint"], m["name"], m["category"]) for m in matches)
    for (codepoint, name, category), count in counts.items():
        print(f"{codepoint} {name} [{category}] x{count}")
    print(f"total: {len(matches)} watermark character(s) found")
    return 1


def _cmd_clean(args) -> int:
    text = _read_input(args.input)
    cleaned, report = clean(text, emoji_guard=not args.no_emoji_guard)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(cleaned)
    else:
        print(cleaned, end="")

    if args.report:
        counts = Counter((r["codepoint"], r["category"]) for r in report)
        for (codepoint, category), count in counts.items():
            print(f"removed {codepoint} [{category}] x{count}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nowatermark")
    sub = parser.add_subparsers(dest="command", required=True)

    p_detect = sub.add_parser("detect", help="scan text for watermark characters")
    p_detect.add_argument("input", help="file path or - for stdin")
    p_detect.set_defaults(func=_cmd_detect)

    p_clean = sub.add_parser("clean", help="strip watermark characters")
    p_clean.add_argument("input", help="file path or - for stdin")
    p_clean.add_argument("-o", "--output", help="output file path (default: stdout)")
    p_clean.add_argument("--report", action="store_true", help="print removal summary to stderr")
    p_clean.add_argument("--no-emoji-guard", action="store_true", help="disable emoji-adjacency guard")
    p_clean.set_defaults(func=_cmd_clean)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
