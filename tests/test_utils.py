import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wiki_scraper.utils import (
    href_to_phrase,
    is_wiki_article_href,
    normalize_phrase,
)


class TestUtils(unittest.TestCase):
    def test_normalize_phrase_replaces_spaces(self) -> None:
        self.assertEqual(normalize_phrase("Team Rocket"), "Team_Rocket")
        self.assertEqual(normalize_phrase("  Team   Rocket  "), "Team_Rocket")

    def test_is_wiki_article_href_filters_namespaces_and_external(self) -> None:
        self.assertTrue(is_wiki_article_href("/wiki/James", prefix="/wiki/"))
        self.assertTrue(is_wiki_article_href("/wiki/Jessie#Section", prefix="/wiki/"))
        self.assertFalse(is_wiki_article_href("/wiki/File:Rocket.png", prefix="/wiki/"))
        self.assertFalse(is_wiki_article_href("https://example.com/wiki/A", prefix="/wiki/"))
        self.assertFalse(is_wiki_article_href("/w/index.php?title=Nope", prefix="/wiki/"))

    def test_href_to_phrase_decodes_and_cleans(self) -> None:
        self.assertEqual(href_to_phrase("/wiki/Team_Rocket", prefix="/wiki/"), "Team Rocket")
        self.assertEqual(
            href_to_phrase("/wiki/Jessie%27s_cat#Section", prefix="/wiki/"),
            "Jessie's cat",
        )


if __name__ == "__main__":
    unittest.main()
