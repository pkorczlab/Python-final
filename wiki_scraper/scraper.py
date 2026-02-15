"""Scraper for fetching wiki pages."""

from __future__ import annotations

from pathlib import Path
from time import sleep
from typing import Optional

import requests

from wiki_scraper.config import ARTICLE_PATH_PREFIX, DEFAULT_HEADERS
from wiki_scraper.utils import build_article_url


class Scraper:
    """Fetches HTML content for a given wiki phrase."""

    def __init__(
        self,
        base_url: str,
        phrase: str,
        *,
        use_local_html_file_instead: bool = False,
        local_html_path: Optional[str] = None,
        timeout_seconds: int = 15,
        max_retries: int = 3,
        retry_backoff_seconds: float = 1.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url
        self.phrase = phrase
        self.use_local_html_file_instead = use_local_html_file_instead
        self.local_html_path = local_html_path
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.session = session or requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    @property
    def article_url(self) -> str:
        return build_article_url(self.base_url, self.phrase, ARTICLE_PATH_PREFIX)

    def fetch_html(self) -> str:
        if self.use_local_html_file_instead:
            return self._read_local_html()
        return self._fetch_remote_html()

    def _read_local_html(self) -> str:
        if not self.local_html_path:
            raise ValueError("Local HTML path not provided")
        path = Path(self.local_html_path)
        if not path.exists():
            raise FileNotFoundError(f"Local HTML file not found: {path}")
        return path.read_text(encoding="utf-8")

    def _fetch_remote_html(self) -> str:
        last_status: int | None = None
        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(self.article_url, timeout=self.timeout_seconds)
                last_status = response.status_code
            except Exception as exc:
                last_exc = exc
                last_status = None
            else:
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding
                    return response.text

                # Typical transient errors / rate limiting.
                if response.status_code not in {429, 500, 502, 503, 504}:
                    break

            if attempt < self.max_retries:
                sleep(self.retry_backoff_seconds * (2**attempt))

        if last_exc is not None:
            raise ValueError(f"Failed to fetch article: {self.article_url}") from last_exc

        raise ValueError(f"Failed to fetch article ({last_status}): {self.article_url}")
