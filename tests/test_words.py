import unittest
from collections import Counter
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wiki_scraper.words import merge_word_counts, tokenize_words


class TestWords(unittest.TestCase):
    def test_tokenize_words_basic(self) -> None:
        text = "Hello, world! It's Team Rocket."
        self.assertEqual(tokenize_words(text), ["hello", "world", "it's", "team", "rocket"])

    def test_merge_word_counts_accumulates(self) -> None:
        existing = {"team": 2, "rocket": 1}
        new = Counter({"team": 3, "rocket": 2, "hello": 1})
        merged = merge_word_counts(existing, new)
        self.assertEqual(merged["team"], 5)
        self.assertEqual(merged["rocket"], 3)
        self.assertEqual(merged["hello"], 1)


if __name__ == "__main__":
    unittest.main()
