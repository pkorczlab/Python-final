"""Utility helpers for the WikiScraper project."""

from __future__ import annotations

from urllib.parse import unquote


def normalize_phrase(phrase: str) -> str:
    """Normalize phrase for URL usage by replacing spaces with underscores."""
    return "_".join(phrase.strip().split())


def build_article_url(base_url: str, phrase: str, prefix: str) -> str:
    """Build article URL from base URL, prefix, and phrase."""
    base = base_url.rstrip("/")
    normalized = normalize_phrase(phrase)
    return f"{base}{prefix}{normalized}"


def phrase_to_csv_filename(phrase: str) -> str:
    return f"{normalize_phrase(phrase)}.csv"


def is_wiki_article_href(href: str, *, prefix: str) -> bool:
    if not href.startswith(prefix):
        return False
    if href.startswith("//") or href.startswith("http://") or href.startswith("https://"):
        return False
    if ":" in href[len(prefix) :].split("#", 1)[0]:
        # Skip special namespaces like File:, Category:, Help:, etc.
        return False
    return True


def href_to_phrase(href: str, *, prefix: str) -> str:
    raw = href[len(prefix) :].split("#", 1)[0].split("?", 1)[0]
    raw = unquote(raw)
    return raw.replace("_", " ").strip()
