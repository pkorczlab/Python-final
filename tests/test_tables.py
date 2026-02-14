import unittest
from pathlib import Path

from wiki_scraper import parser

try:
    import pandas as _pandas  # noqa: F401
except Exception:  # noqa: BLE001
    _pandas = None


@unittest.skipIf(_pandas is None, "pandas is not installed")
class TestTables(unittest.TestCase):
    def test_html_table_to_dataframe_and_value_counts(self) -> None:
        from wiki_scraper.tables import compute_value_counts, get_nth_table, html_table_to_dataframe

        html = Path("tests/fixtures/team_rocket_minimal.html").read_text(encoding="utf-8")
        soup = parser.parse_html(html)
        root = parser.find_article_root(soup)
        tables = parser.extract_tables(root)

        table = get_nth_table(tables, 2)
        df = html_table_to_dataframe(table, first_row_is_header=False)

        # Expect row headers in first column (Fire/Water).
        self.assertIn("Fire", df.index.astype(str).tolist())
        self.assertIn("Water", df.index.astype(str).tolist())

        counts = compute_value_counts(df)
        # "2" appears multiple times in the sample table.
        self.assertTrue((counts["value"] == "2").any())


if __name__ == "__main__":
    unittest.main()
