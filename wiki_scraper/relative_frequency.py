"""Relative word frequency analysis against a language frequency list."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class RelativeFrequencyConfig:
    language_code: str
    mode: str  # "article" or "language"
    count: int
    word_counts_path: str = "word-counts.json"
    chart_path: str | None = None
    language_top_k: int = 50000


def _load_wordfreq():
    # Import lazily to keep module importable without optional deps installed.
    try:
        from wordfreq import top_n_list, word_frequency
    except Exception as exc:
        raise RuntimeError(
            "wordfreq is required for --analyze-relative-word-frequency. "
            "Install dependencies from requirements.txt"
        ) from exc
    return top_n_list, word_frequency


def _normalize(values: list[float | None]) -> list[float | None]:
    non_null = [v for v in values if v is not None]
    if not non_null:
        return values
    max_v = max(non_null)
    if max_v <= 0:
        return values
    out: list[float | None] = []
    for v in values:
        out.append(None if v is None else (v / max_v))
    return out


def _ensure_parent(path: str) -> None:
    p = Path(path)
    if p.parent and str(p.parent) not in {".", ""}:
        p.parent.mkdir(parents=True, exist_ok=True)


def analyze_relative_word_frequency(
    word_counts: dict[str, int],
    *,
    language_code: str,
    mode: str,
    count: int,
    chart_path: str | None = None,
    language_top_k: int = 50000,
) -> pd.DataFrame:
    if mode not in {"article", "language"}:
        raise ValueError("mode must be 'article' or 'language'")
    if count <= 0:
        raise ValueError("count must be > 0")

    top_n_list, word_frequency = _load_wordfreq()

    lang_n = max(1000, count, language_top_k)
    lang_words = top_n_list(language_code, lang_n)
    lang_freq_map = {w: float(word_frequency(w, language_code)) for w in lang_words}

    if mode == "article":
        items = sorted(word_counts.items(), key=lambda kv: kv[1], reverse=True)[:count]
        words = [w for w, _ in items]
    else:
        words = list(lang_words[:count])

    article_freq = [float(word_counts.get(w)) if w in word_counts else None for w in words]

    # As required: show gaps for words not present in the language list.
    language_freq = [lang_freq_map.get(w) for w in words]

    article_norm = _normalize(article_freq)
    language_norm = _normalize(language_freq)

    df = pd.DataFrame(
        {
            "word": words,
            "frequency_in_article": article_norm,
            "frequency_in_language": language_norm,
        }
    )

    if chart_path:
        _ensure_parent(chart_path)
        _save_chart(df, chart_path, mode=mode, language_code=language_code)

    return df


def _save_chart(df: pd.DataFrame, chart_path: str, *, mode: str, language_code: str) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise RuntimeError(
            "matplotlib is required for --chart. Install dependencies from requirements.txt"
        ) from exc

    words = df["word"].astype(str).tolist()
    a = df["frequency_in_article"].tolist()
    l = df["frequency_in_language"].tolist()

    x = list(range(len(words)))
    width = 0.4

    a_vals = [0.0 if v is None else float(v) for v in a]
    l_vals = [0.0 if v is None else float(v) for v in l]

    fig_w = max(10.0, min(24.0, 0.7 * len(words)))
    fig, ax = plt.subplots(figsize=(fig_w, 6.0))

    ax.bar([i - width / 2 for i in x], a_vals, width=width, label="article", color="#2E86AB")
    ax.bar([i + width / 2 for i in x], l_vals, width=width, label=f"language ({language_code})", color="#F18F01")

    ax.set_title(f"Relative word frequency (mode={mode})")
    ax.set_ylabel("normalized frequency")
    ax.set_xticks(x)
    ax.set_xticklabels(words, rotation=60, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)
