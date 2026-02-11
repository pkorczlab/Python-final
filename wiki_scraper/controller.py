"""Controller orchestrating CLI commands."""

from __future__ import annotations

from dataclasses import dataclass

from wiki_scraper import parser
from wiki_scraper.config import DEFAULT_BASE_URL
from wiki_scraper.scraper import Scraper


@dataclass(frozen=True)
class ControllerConfig:
    base_url: str = DEFAULT_BASE_URL
    use_local_html_file: bool = False
    local_html_path: str | None = None


class WikiController:
    def __init__(self, config: ControllerConfig) -> None:
        self.config = config

    def summary(self, phrase: str) -> str:
        scraper = Scraper(
            self.config.base_url,
            phrase,
            use_local_html_file_instead=self.config.use_local_html_file,
            local_html_path=self.config.local_html_path,
        )
        html = scraper.fetch_html()
        soup = parser.parse_html(html)
        root = parser.find_article_root(soup)
        text = parser.extract_first_paragraph_text(root)
        if not text:
            raise ValueError("No paragraph text found in article")
        return text
