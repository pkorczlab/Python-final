"""Word tokenization and persistent word counting."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Iterable


try:
    # Third-party `regex` supports Unicode properties like \p{L}.
    import regex as _re

    _WORD_RE = _re.compile(r"[\p{L}\p{M}]+(?:[’'][\p{L}\p{M}]+)?")
except Exception:
    # Fallback to stdlib re: match Unicode letters but exclude digits/underscore.
    import re as _re

    _WORD_RE = _re.compile(r"[^\W\d_]+(?:[’'][^\W\d_]+)?")


def tokenize_words(text: str) -> list[str]:
    """Tokenize text into (lowercased) words.

    Supports Latin letters with diacritics (e.g. pl/es/fr) and internal apostrophes.
    """

    return [m.group(0).casefold() for m in _WORD_RE.finditer(text)]


def count_words(words: Iterable[str]) -> Counter[str]:
    return Counter(words)


def load_word_counts(path: str = "word-counts.json") -> dict[str, int]:
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("word-counts.json must contain a JSON object")

    result: dict[str, int] = {}
    for key, value in data.items():
        if not isinstance(key, str) or not isinstance(value, int):
            continue
        result[key] = value
    return result


def save_word_counts(counts: dict[str, int], path: str = "word-counts.json") -> None:
    p = Path(path)
    p.write_text(
        json.dumps(counts, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def merge_word_counts(
    existing: dict[str, int],
    new_counts: Counter[str],
) -> dict[str, int]:
    merged = dict(existing)
    for word, count in new_counts.items():
        merged[word] = merged.get(word, 0) + int(count)
    return merged
