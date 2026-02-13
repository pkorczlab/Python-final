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
    if not any([args.summary, args.table]):  # Placeholder for future commands
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
        except Exception as exc:  # noqa: BLE001 - CLI boundary
            raise SystemExit(str(exc)) from exc
        print(text)
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
        except Exception as exc:  # noqa: BLE001 - CLI boundary
            raise SystemExit(str(exc)) from exc
        print(df)
        print()
        print(counts)
        print()
        print(f"Saved CSV: {csv_name}")
        return

    raise SystemExit("No valid command provided")


if __name__ == "__main__":
    main()
