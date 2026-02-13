"""Controller orchestrating CLI commands."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from wiki_scraper import parser
from wiki_scraper.config import DEFAULT_BASE_URL
from wiki_scraper.scraper import Scraper
from wiki_scraper.tables import extract_table_result, get_nth_table
from wiki_scraper.utils import phrase_to_csv_filename


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

    def table(self, phrase: str, *, number: int, first_row_is_header: bool) -> tuple[pd.DataFrame, pd.DataFrame, str]:
        scraper = Scraper(
            self.config.base_url,
            phrase,
            use_local_html_file_instead=self.config.use_local_html_file,
            local_html_path=self.config.local_html_path,
        )
        html = scraper.fetch_html()
        soup = parser.parse_html(html)
        root = parser.find_article_root(soup)

        tables = parser.extract_tables(root)
        table_tag = get_nth_table(tables, number)
        result = extract_table_result(table_tag, first_row_is_header=first_row_is_header)

        csv_name = phrase_to_csv_filename(phrase)
        result.dataframe.to_csv(csv_name, index=True, encoding="utf-8")
        return result.dataframe, result.value_counts, csv_name
