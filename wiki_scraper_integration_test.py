"""Integration test runner.

Runs a single feature using a local HTML file. Exits with non-zero code on failure.
"""

from __future__ import annotations

import sys

from wiki_scraper.controller import ControllerConfig, WikiController


def main() -> int:
    config = ControllerConfig(
        use_local_html_file=True,
        local_html_path="tests/fixtures/team_rocket_minimal.html",
    )
    controller = WikiController(config)

    text = controller.summary("Team Rocket")
    assert text.startswith("Team Rocket"), "summary should start with phrase"
    assert text.endswith("Sevii Islands."), "summary should end with expected sentence"
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
