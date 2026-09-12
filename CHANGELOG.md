# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `nowatermark detect`/`clean` CLI for invisible-Unicode watermark scanning and removal (zero-width chars, variation selectors, Unicode tag-block, anomalous Zs spaces, line-separator variants, Private Use Area, bidi/format controls).
- Emoji-adjacency guard so ZWJ/ZWNJ and flag-emoji tag sequences survive `clean` by default (`--no-emoji-guard` to disable).
- Heuristic homoglyph detection: `detect` flags words mixing Latin with visually-identical Cyrillic/Greek letters (detection only, never affects exit code).
- `skill/SKILL.md` packaging this as an agent skill, with a `stop-slop` dependency for stylistic AI-writing tells and a validated humanization checklist.
- `scripts/verify_humanization.py` dev harness to check cleaned text against independent AI-text detectors.
- Portuguese translations of README and CONTRIBUTING.

### Fixed
- Flag-emoji tag-sequence preservation now validates complete, terminated sequences instead of a backward walk, closing a hole where payload characters appended right after a legitimate sequence's cancel tag were also preserved.
