"""Controller orchestrating CLI commands."""

from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from time import sleep

import pandas as pd

from wiki_scraper import parser
from wiki_scraper.config import ARTICLE_PATH_PREFIX, DEFAULT_BASE_URL
from wiki_scraper.scraper import Scraper
from wiki_scraper.tables import extract_table_result, get_nth_table
from wiki_scraper.utils import (
    href_to_phrase,
    is_wiki_article_href,
    phrase_to_csv_filename,
)
from wiki_scraper.words import (
    count_words,
    load_word_counts,
    merge_word_counts,
    save_word_counts,
    tokenize_words,
)
from wiki_scraper.relative_frequency import analyze_relative_word_frequency


@dataclass(frozen=True)
class ControllerConfig:
    base_url: str = DEFAULT_BASE_URL
    use_local_html_file: bool = False
    local_html_path: str | None = None


class WikiController:
    def __init__(self, config: ControllerConfig) -> None:
        self.config = config
        self._word_counts_path = "word-counts.json"

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

    def table(
        self,
        phrase: str,
        *,
        number: int,
        first_row_is_header: bool,
    ) -> tuple[pd.DataFrame, pd.DataFrame, str]:
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

    def count_words(self, phrase: str, *, json_path: str = "word-counts.json") -> int:
        scraper = Scraper(
            self.config.base_url,
            phrase,
            use_local_html_file_instead=self.config.use_local_html_file,
            local_html_path=self.config.local_html_path,
        )
        html = scraper.fetch_html()
        soup = parser.parse_html(html)
        root = parser.find_article_root(soup)
        text = parser.extract_all_text(root)

        return self._update_word_counts(text, json_path=json_path)

    def auto_count_words(self, start_phrase: str, *, depth: int, wait_seconds: float) -> int:
        if depth < 0:
            raise ValueError("depth must be >= 0")
        if wait_seconds < 0:
            raise ValueError("wait must be >= 0")

        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque()
        queue.append((start_phrase, 0))

        existing = load_word_counts(self._word_counts_path)
        processed = 0
        while queue:
            phrase, dist = queue.popleft()
            key = normalize_phrase_for_visit(phrase)
            if key in visited:
                continue
            visited.add(key)

            print(phrase)
            processed += 1

            scraper = Scraper(
                self.config.base_url,
                phrase,
                use_local_html_file_instead=self.config.use_local_html_file,
                local_html_path=self.config.local_html_path,
            )
            html = scraper.fetch_html()
            soup = parser.parse_html(html)
            root = parser.find_article_root(soup)

            if dist < depth:
                for href in parser.extract_links(root):
                    if not is_wiki_article_href(href, prefix=ARTICLE_PATH_PREFIX):
                        continue
                    next_phrase = href_to_phrase(href, prefix=ARTICLE_PATH_PREFIX)
                    next_key = normalize_phrase_for_visit(next_phrase)
                    if next_key in visited:
                        continue
                    queue.append((next_phrase, dist + 1))

            text = parser.extract_all_text(root)
            existing, _ = self._update_word_counts_with_existing(existing, text)
            save_word_counts(existing, self._word_counts_path)

            sleep(wait_seconds)

        return processed

    def analyze_relative_word_frequency(
        self,
        *,
        mode: str,
        count: int,
        language_code: str,
        chart_path: str | None,
        word_counts_path: str = "word-counts.json",
    ) -> pd.DataFrame:
        word_counts = load_word_counts(word_counts_path)
        if not word_counts:
            raise ValueError(
                f"No word counts found in {word_counts_path}. Run --count-words first."
            )
        return analyze_relative_word_frequency(
            word_counts,
            language_code=language_code,
            mode=mode,
            count=count,
            chart_path=chart_path,
        )

    def _update_word_counts(self, text: str, *, json_path: str) -> int:
        words = tokenize_words(text)
        counts = count_words(words)

        existing = load_word_counts(json_path)
        merged = merge_word_counts(existing, counts)
        save_word_counts(merged, json_path)
        return sum(counts.values())

    def _update_word_counts_with_existing(
        self,
        existing: dict[str, int],
        text: str,
    ) -> tuple[dict[str, int], int]:
        words = tokenize_words(text)
        counts = count_words(words)

        merged = merge_word_counts(existing, counts)
        return merged, sum(counts.values())


def normalize_phrase_for_visit(phrase: str) -> str:
    return " ".join(phrase.strip().lower().split())
