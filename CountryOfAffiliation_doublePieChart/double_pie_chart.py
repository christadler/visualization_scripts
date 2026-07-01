"""Nested (double) pie chart of participants' country of affiliation, grouped by region.

Reads:
  - a participants CSV with a "Country of Affiliation" column
    (path given on the command line, defaults to data/SDL_Trg.csv)
  - data/Countries.csv  country -> region/category lookup table

Steps:
  1. Count participants per country, sorted alphabetically.
  2. Map each country to its region via data/Countries.csv, then aggregate per
     region. Regions are ordered with Europe, widening countries and
     associated countries first (in that order), followed by the remaining
     regions sorted by participant count (descending). Countries within a
     region are sorted by participant count (descending).
  3. Plot a nested donut chart: inner ring = regions, outer ring = countries.
     Countries are colored as shades of their region's base color.
"""
import argparse
import colorsys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import to_rgb

PROJECT_DIR = Path(__file__).parent
PARTICIPANTS_FILE = PROJECT_DIR / "data" / "SDL_Trg.csv"
COUNTRIES_FILE = PROJECT_DIR / "data" / "Countries.csv"
OUTPUT_FILE = PROJECT_DIR / "country_of_affiliation_double_pie_chart.png"

COUNTRY_COLUMN = "Country of Affiliation"

# Europe, widening countries and associated countries are always shown first,
# in this order, using a related blue/green color family.
FIXED_REGION_ORDER = ["Europe", "widening countries", "associated countries"]
FIXED_REGION_COLORS = {
    "Europe": "#1B5FA8",
    "widening countries": "#2F8F8F",
    "associated countries": "#4CAF6D",
}

# All other regions are ordered by participant count (descending) and colored
# along a yellow -> orange gradient, largest region gets the darkest shade.
OTHER_REGION_DARK = "#D9700E"
OTHER_REGION_LIGHT = "#FFE29A"

DEFAULT_REGION_COLOR = "#999999"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "participants_file",
        nargs="?",
        default=str(PARTICIPANTS_FILE),
        help=(
            f"Path to the participants CSV with a '{COUNTRY_COLUMN}' column "
            f"(default: {PARTICIPANTS_FILE})"
        ),
    )
    return parser.parse_args()


def load_country_counts(participants_file) -> pd.Series:
    df = pd.read_csv(participants_file)
    return (
        df[COUNTRY_COLUMN]
        .dropna()
        .str.strip()
        .value_counts()
        .sort_index()
    )


def load_region_lookup() -> dict:
    countries = pd.read_csv(COUNTRIES_FILE)
    countries["Country_lower"] = countries["Country"].str.strip().str.lower()
    return countries.set_index("Country_lower")["Category"].to_dict()


def build_region_country_table(country_counts: pd.Series, region_lookup: dict):
    records = [
        {
            "Country": country,
            "Region": region_lookup.get(country.lower(), "unknown"),
            "Count": count,
        }
        for country, count in country_counts.items()
    ]
    table = pd.DataFrame.from_records(records)
    region_totals = table.groupby("Region")["Count"].sum().sort_values(ascending=False)
    return table, region_totals


def interpolate_gradient(dark_hex: str, light_hex: str, n: int):
    """n colors from dark_hex (i=0) to light_hex (i=n-1), linearly interpolated."""
    if n <= 1:
        return [to_rgb(dark_hex)] * n
    dark, light = to_rgb(dark_hex), to_rgb(light_hex)
    return [
        tuple(d + (l - d) * (i / (n - 1)) for d, l in zip(dark, light))
        for i in range(n)
    ]


def order_regions_and_assign_colors(region_totals: pd.Series):
    """Europe / widening countries / associated countries first (blue/green),
    then the rest sorted by count descending (yellow -> orange gradient)."""
    fixed_present = [r for r in FIXED_REGION_ORDER if r in region_totals.index]
    other_regions = [r for r in region_totals.index if r not in FIXED_REGION_ORDER]

    region_order = fixed_present + other_regions
    region_colors = {r: FIXED_REGION_COLORS[r] for r in fixed_present}
    region_colors.update(
        zip(other_regions, interpolate_gradient(OTHER_REGION_DARK, OTHER_REGION_LIGHT, len(other_regions)))
    )
    return region_order, region_colors


def shade_color(base_color, factor: float):
    """Lighten a base color. factor=1.0 -> base color, factor towards 0 -> lighter tint."""
    r, g, b = to_rgb(base_color)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = l + (1 - l) * (1 - factor) * 0.75
    return colorsys.hls_to_rgb(h, min(l, 0.93), s)


def assign_country_colors(table: pd.DataFrame, region_colors: dict):
    colors = []
    for region, group in table.groupby("Region", sort=False):
        base = region_colors.get(region, DEFAULT_REGION_COLOR)
        n = len(group)
        for i in range(n):
            factor = 1 - (i / max(n, 1)) * 0.7
            colors.append(shade_color(base, factor))
    return colors


def print_step1(country_counts: pd.Series):
    print("=" * 60)
    print("Schritt 1: Teilnehmer je Land (alphabetisch)")
    print("=" * 60)
    for country, count in country_counts.items():
        print(f"{country:30s} {count:3d}")
    print(f"{'Gesamt':30s} {country_counts.sum():3d}\n")


def print_step2(table: pd.DataFrame, region_totals: pd.Series):
    total = region_totals.sum()
    print("=" * 60)
    print("Schritt 2: Teilnehmer je Region, je Land innerhalb der Region")
    print("(Europe / widening countries / associated countries zuerst, dann")
    print("die restlichen Regionen absteigend nach Teilnehmerzahl)")
    print("=" * 60)
    for region in region_totals.index:
        count = region_totals[region]
        pct = count / total * 100
        print(f"\n{region} ({count}, {pct:.1f}%)")
        for _, row in table[table["Region"] == region].iterrows():
            print(f"  {row['Country']:28s} {row['Count']:3d}")
    print(f"\n{'Gesamt':30s} {total:3d}\n")


def plot_double_pie(table: pd.DataFrame, region_totals: pd.Series, region_colors: dict):
    fig, ax = plt.subplots(figsize=(11, 10), subplot_kw=dict(aspect="equal"))

    total = region_totals.sum()
    ordered_colors = [region_colors[r] for r in region_totals.index]
    country_colors = assign_country_colors(table, region_colors)

    outer_labels = [f"{c} ({n})" for c, n in zip(table["Country"], table["Count"])]

    ax.pie(
        table["Count"],
        radius=1.3,
        colors=country_colors,
        labels=outer_labels,
        labeldistance=1.08,
        wedgeprops=dict(width=0.3, edgecolor="white", linewidth=1.2),
        textprops=dict(fontsize=8),
        startangle=90,
        counterclock=False,
    )
    inner_wedges, _ = ax.pie(
        region_totals,
        radius=1.0,
        colors=ordered_colors,
        wedgeprops=dict(width=0.5, edgecolor="white", linewidth=1.2),
        startangle=90,
        counterclock=False,
    )

    # Small region slices would overlap if labeled in-wedge, so regions are
    # explained via a legend instead of inline text.
    region_legend_labels = [
        f"{r} ({n}, {n / total * 100:.1f}%)" for r, n in region_totals.items()
    ]
    ax.legend(
        inner_wedges,
        region_legend_labels,
        title="Region",
        loc="center left",
        bbox_to_anchor=(1.08, 0.5),
        fontsize=9,
        title_fontsize=10,
        frameon=False,
    )

    ax.set_xlim(-1.7, 1.7)
    ax.set_ylim(-1.7, 1.8)
    fig.suptitle("Country of Affiliation je Region", fontsize=15, y=0.97)
    fig.savefig(OUTPUT_FILE, dpi=200, bbox_inches="tight")
    print(f"Chart gespeichert unter: {OUTPUT_FILE}")


def main():
    args = parse_args()

    country_counts = load_country_counts(args.participants_file)
    print_step1(country_counts)

    region_lookup = load_region_lookup()
    table, region_totals = build_region_country_table(country_counts, region_lookup)

    region_order, region_colors = order_regions_and_assign_colors(region_totals)
    region_totals = region_totals.reindex(region_order)
    table["Region"] = pd.Categorical(table["Region"], categories=region_order, ordered=True)
    table = table.sort_values(["Region", "Count"], ascending=[True, False]).reset_index(drop=True)

    print_step2(table, region_totals)
    plot_double_pie(table, region_totals, region_colors)


if __name__ == "__main__":
    main()
