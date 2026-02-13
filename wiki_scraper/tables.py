"""Table extraction and conversion helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from bs4 import Tag


@dataclass(frozen=True)
class TableExtractionResult:
    dataframe: pd.DataFrame
    value_counts: pd.DataFrame


def get_nth_table(tables: list[Tag], number: int) -> Tag:
    if number < 1:
        raise ValueError("Table number must be >= 1")
    if number > len(tables):
        raise ValueError(f"Table number {number} out of range (found {len(tables)})")
    return tables[number - 1]


def html_table_to_dataframe(table: Tag, *, first_row_is_header: bool) -> pd.DataFrame:
    header = 0 if first_row_is_header else None

    # read_html returns a list; in our case the snippet should contain exactly one table.
    html = str(table)

    # Prefer treating first column as row headers (index), as required by the assignment.
    try:
        frames = pd.read_html(html, header=header, index_col=0)
    except ValueError:
        frames = pd.read_html(html, header=header)

    if not frames:
        raise ValueError("No tables could be parsed by pandas")

    df = frames[0]

    # Drop fully empty rows/columns that sometimes appear after parsing.
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
    return df


def compute_value_counts(df: pd.DataFrame) -> pd.DataFrame:
    # Count values in data cells only (headers are not part of df values; index is excluded).
    series = df.stack(dropna=True)
    series = series.astype(str).str.strip()
    series = series[series != ""]
    counts = series.value_counts().rename_axis("value").reset_index(name="count")
    return counts


def extract_table_result(table: Tag, *, first_row_is_header: bool) -> TableExtractionResult:
    df = html_table_to_dataframe(table, first_row_is_header=first_row_is_header)
    counts = compute_value_counts(df)
    return TableExtractionResult(dataframe=df, value_counts=counts)
