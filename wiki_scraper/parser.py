"""HTML parsing helpers for wiki pages."""

from __future__ import annotations

from typing import Iterable, Optional

from bs4 import BeautifulSoup, Tag


def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def find_article_root(soup: BeautifulSoup) -> Tag:
    candidates = [
        soup.select_one("div.mw-content-ltr"),
        soup.select_one("div#mw-content-text"),
        soup.select_one("div.mw-parser-output"),
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        inner = candidate.select_one("div.mw-parser-output")
        return inner or candidate
    return soup.body or soup


def _iter_paragraphs(root: Tag) -> Iterable[Tag]:
    return root.find_all("p", recursive=True)


def extract_first_paragraph_text(root: Tag) -> str:
    for paragraph in _iter_paragraphs(root):
        text = paragraph.get_text(" ", strip=True)
        if text:
            return text
    return ""


def extract_all_text(root: Tag) -> str:
    return root.get_text(" ", strip=True)


def extract_links(root: Tag) -> list[str]:
    links = []
    for anchor in root.find_all("a", href=True):
        href = anchor.get("href")
        if href:
            links.append(href)
    return links


def extract_tables(root: Tag) -> list[Tag]:
    return list(root.find_all("table", recursive=True))
