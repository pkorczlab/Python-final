"""Utility helpers for the WikiScraper project."""

from __future__ import annotations


def normalize_phrase(phrase: str) -> str:
    """Normalize phrase for URL usage by replacing spaces with underscores."""
    return "_".join(phrase.strip().split())


def build_article_url(base_url: str, phrase: str, prefix: str) -> str:
    """Build article URL from base URL, prefix, and phrase."""
    base = base_url.rstrip("/")
    normalized = normalize_phrase(phrase)
    return f"{base}{prefix}{normalized}"
