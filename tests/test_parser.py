import unittest
from pathlib import Path

from wiki_scraper import parser


class TestParser(unittest.TestCase):
    def test_extract_first_paragraph_text_from_fixture(self) -> None:
        html = Path("tests/fixtures/team_rocket_minimal.html").read_text(encoding="utf-8")
        soup = parser.parse_html(html)
        root = parser.find_article_root(soup)
        text = parser.extract_first_paragraph_text(root)
        self.assertTrue(text.startswith("Team Rocket"))
        self.assertTrue(text.endswith("Sevii Islands."))


if __name__ == "__main__":
    unittest.main()
