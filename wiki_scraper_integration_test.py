"""Integration test runner.

Runs a single feature using a local HTML file. Exits with non-zero code on failure.
"""

from __future__ import annotations

import re
import sys

from wiki_scraper.controller import ControllerConfig, WikiController


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text


def main() -> int:
    config = ControllerConfig(
        use_local_html_file=True,
        local_html_path="tests/fixtures/team_rocket_real.html",
    )
    controller = WikiController(config)

    text = normalize_text(controller.summary("Team Rocket"))
    assert text.startswith("Team Rocket"), f"summary should start with phrase; got: {text[:80]!r}"
    assert text.endswith("Sevii Islands."), f"summary should end with expected sentence; got: {text[-120:]!r}"
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
