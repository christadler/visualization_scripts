"""Generate a double pie chart (see double_pie_chart.py) for every sheet in an
xlsx workbook that has a "Country of Affiliation" column with actual data.

Sheets without that column, or where the column is present but empty (e.g.
overview/summary sheets, the Countries lookup sheet, differently-shaped
surveys), are skipped and listed at the end.

Usage:
    python generate_all_charts.py [path/to/workbook.xlsx] [output_dir]

Defaults to data/geoI_Participants_test.xlsx and charts/.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

from double_pie_chart import (
    PROJECT_DIR,
    build_chart,
    country_counts_from_series,
    load_region_lookup,
)

WORKBOOK_FILE = PROJECT_DIR / "data" / "geoI_Participants_test.xlsx"
CHARTS_DIR = PROJECT_DIR / "charts"

COUNTRY_COLUMN_NORMALIZED = "country of affiliation"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "workbook_file", nargs="?", default=str(WORKBOOK_FILE),
        help=f"Path to the xlsx workbook (default: {WORKBOOK_FILE})",
    )
    parser.add_argument(
        "output_dir", nargs="?", default=str(CHARTS_DIR),
        help=f"Directory to write <SheetName>.png files into (default: {CHARTS_DIR})",
    )
    return parser.parse_args()


def find_country_column(columns) -> str | None:
    for col in columns:
        if " ".join(str(col).split()).strip().lower() == COUNTRY_COLUMN_NORMALIZED:
            return col
    return None


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    region_lookup = load_region_lookup()
    sheets = pd.read_excel(args.workbook_file, sheet_name=None)

    processed, skipped = [], []
    for sheet_name, df in sheets.items():
        country_column = find_country_column(df.columns)
        if country_column is None:
            skipped.append((sheet_name, "keine 'Country of Affiliation'-Spalte"))
            continue

        country_counts = country_counts_from_series(df[country_column])
        if country_counts.empty:
            skipped.append((sheet_name, "Spalte vorhanden, aber ohne Daten"))
            continue

        output_path = output_dir / f"{sheet_name}.png"
        table, region_totals = build_chart(country_counts, region_lookup, output_path)
        processed.append((sheet_name, int(region_totals.sum()), len(table)))
        print(f"{sheet_name:35s} {region_totals.sum():4d} Teilnehmer, {len(table):3d} Laender -> {output_path.name}")

    print(f"\n{len(processed)} Charts erstellt in {output_dir}/")
    if skipped:
        print(f"{len(skipped)} Tabellen uebersprungen:")
        for name, reason in skipped:
            print(f"  {name:35s} ({reason})")


if __name__ == "__main__":
    sys.exit(main())
