"""CLI entrypoint for the WikiScraper project."""

from __future__ import annotations

import argparse

from wiki_scraper.config import DEFAULT_BASE_URL
from wiki_scraper.controller import ControllerConfig, WikiController


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WikiScraper CLI")
    parser.add_argument(
        "--summary",
        metavar="PHRASE",
        help="Print the first paragraph summary for a phrase.",
    )
    parser.add_argument(
        "--count-words",
        metavar="PHRASE",
        help="Count words in the article and update ./word-counts.json.",
    )
    parser.add_argument(
        "--auto-count-words",
        metavar="PHRASE",
        help="Crawl wiki links starting from a phrase and update ./word-counts.json.",
    )
    parser.add_argument(
        "--analyze-relative-word-frequency",
        action="store_true",
        help="Compare collected word counts with language word frequencies.",
    )
    parser.add_argument(
        "--table",
        metavar="PHRASE",
        help="Extract N-th <table> from the article and save it to CSV.",
    )
    parser.add_argument(
        "--number",
        type=int,
        help="Table number (1-based) used with --table.",
    )
    parser.add_argument(
        "--first-row-is-header",
        action="store_true",
        help="Treat first row as column headers (used with --table).",
    )
    parser.add_argument(
        "--depth",
        type=int,
        help="Crawl depth (used with --auto-count-words).",
    )
    parser.add_argument(
        "--wait",
        type=float,
        help="Seconds to wait between requests (used with --auto-count-words).",
    )
    parser.add_argument(
        "--mode",
        choices=["article", "language"],
        help="Sorting mode (used with --analyze-relative-word-frequency).",
    )
    parser.add_argument(
        "--count",
        type=int,
        help="Number of rows (used with --analyze-relative-word-frequency).",
    )
    parser.add_argument(
        "--chart",
        help="Path to save bar chart PNG (used with --analyze-relative-word-frequency).",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Language code for word frequencies (default: en).",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL of the selected wiki.",
    )
    parser.add_argument(
        "--use-local-html",
        action="store_true",
        help="Load article HTML from a local file instead of HTTP.",
    )
    parser.add_argument(
        "--local-html",
        help="Path to a local HTML file (used with --use-local-html).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not any(
        [
            args.summary,
            args.table,
            args.count_words,
            args.auto_count_words,
            args.analyze_relative_word_frequency,
        ]
    ):
        parser.print_help()
        raise SystemExit(2)

    if args.use_local_html and not args.local_html:
        raise SystemExit("--local-html is required with --use-local-html")

    config = ControllerConfig(
        base_url=args.base_url,
        use_local_html_file=args.use_local_html,
        local_html_path=args.local_html,
    )
    controller = WikiController(config)

    if args.summary:
        try:
            text = controller.summary(args.summary)
        except Exception as exc:
            raise SystemExit(str(exc)) from exc
        print(text)
        return

    if args.count_words:
        try:
            total = controller.count_words(args.count_words)
        except Exception as exc:
            raise SystemExit(str(exc)) from exc
        print(f"Counted {total} words and updated word-counts.json")
        return

    if args.table:
        if args.number is None:
            raise SystemExit("--number is required with --table")
        try:
            df, counts, csv_name = controller.table(
                args.table,
                number=args.number,
                first_row_is_header=args.first_row_is_header,
            )
        except Exception as exc:
            raise SystemExit(str(exc)) from exc
        print(df)
        print()
        print(counts)
        print()
        print(f"Saved CSV: {csv_name}")
        return

    if args.auto_count_words:
        if args.depth is None:
            raise SystemExit("--depth is required with --auto-count-words")
        if args.wait is None:
            raise SystemExit("--wait is required with --auto-count-words")
        try:
            processed = controller.auto_count_words(
                args.auto_count_words,
                depth=args.depth,
                wait_seconds=args.wait,
            )
        except Exception as exc:
            raise SystemExit(str(exc)) from exc
        print(f"Processed {processed} pages and updated word-counts.json")
        return

    if args.analyze_relative_word_frequency:
        if args.mode is None:
            raise SystemExit("--mode is required with --analyze-relative-word-frequency")
        if args.count is None:
            raise SystemExit("--count is required with --analyze-relative-word-frequency")
        try:
            df = controller.analyze_relative_word_frequency(
                mode=args.mode,
                count=args.count,
                language_code=args.language,
                chart_path=args.chart,
            )
        except Exception as exc:
            raise SystemExit(str(exc)) from exc
        print(df)
        if args.chart:
            print()
            print(f"Saved chart: {args.chart}")
        return

    raise SystemExit("No valid command provided")


if __name__ == "__main__":
    main()
