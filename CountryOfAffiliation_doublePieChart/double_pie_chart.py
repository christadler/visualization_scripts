"""Nested (double) pie chart of participants' country of affiliation, grouped by region.

Reads:
  - data/SDL_Trg.csv    participant list with a "Country of Affiliation" column
  - data/Countries.csv  country -> region/category lookup table

Steps:
  1. Count participants per country (data/SDL_Trg.csv), sorted alphabetically.
  2. Map each country to its region via data/Countries.csv, then aggregate per
     region. Regions are sorted by total participant count (descending), and
     countries within a region are sorted by participant count (descending).
  3. Plot a nested donut chart: inner ring = regions, outer ring = countries.
     Countries are colored as shades of their region's base color.
"""
import colorsys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_DIR = Path(__file__).parent
PARTICIPANTS_FILE = PROJECT_DIR / "data" / "SDL_Trg.csv"
COUNTRIES_FILE = PROJECT_DIR / "data" / "Countries.csv"
OUTPUT_FILE = PROJECT_DIR / "country_of_affiliation_double_pie_chart.png"

COUNTRY_COLUMN = "Country of Affiliation"

# Base color per region/category. Adjust these to match your project's
# branding -- countries inherit a shade of their region's color (see
# assign_country_colors), so changing a value here updates the whole region.
REGION_COLORS = {
    "Europe": "#3B7DD8",
    "Asia": "#E0A72E",
    "Africa": "#4FA05A",
    "Middle East": "#B5533C",
    "Middle/South America": "#8E5AA5",
    "U.S. + Canada": "#3EAFA4",
    "Oceania": "#D25C9B",
    "associated countries": "#7A8B99",
    "widening countries": "#C9A15A",
    "outermost region": "#5C6BC0",
    "unknown": "#B0B0B0",
}
DEFAULT_REGION_COLOR = "#999999"


def load_country_counts() -> pd.Series:
    df = pd.read_csv(PARTICIPANTS_FILE)
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
    table["Region"] = pd.Categorical(table["Region"], categories=region_totals.index, ordered=True)
    table = table.sort_values(["Region", "Count"], ascending=[True, False]).reset_index(drop=True)
    return table, region_totals


def shade_color(hex_color: str, factor: float):
    """Lighten a base color. factor=1.0 -> base color, factor towards 0 -> lighter tint."""
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = l + (1 - l) * (1 - factor) * 0.75
    return colorsys.hls_to_rgb(h, min(l, 0.93), s)


def assign_country_colors(table: pd.DataFrame):
    colors = []
    for region, group in table.groupby("Region", sort=False):
        base = REGION_COLORS.get(region, DEFAULT_REGION_COLOR)
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
    print("=" * 60)
    print("Schritt 2: Teilnehmer je Region (absteigend), je Land innerhalb der Region")
    print("=" * 60)
    for region in region_totals.index:
        print(f"\n{region} ({region_totals[region]})")
        for _, row in table[table["Region"] == region].iterrows():
            print(f"  {row['Country']:28s} {row['Count']:3d}")
    print(f"\n{'Gesamt':30s} {region_totals.sum():3d}\n")


def plot_double_pie(table: pd.DataFrame, region_totals: pd.Series):
    fig, ax = plt.subplots(figsize=(11, 10), subplot_kw=dict(aspect="equal"))

    region_colors = [REGION_COLORS.get(r, DEFAULT_REGION_COLOR) for r in region_totals.index]
    country_colors = assign_country_colors(table)

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
        colors=region_colors,
        wedgeprops=dict(width=0.5, edgecolor="white", linewidth=1.2),
        startangle=90,
        counterclock=False,
    )

    # Small region slices would overlap if labeled in-wedge, so regions are
    # explained via a legend instead of inline text.
    region_legend_labels = [f"{r} ({n})" for r, n in region_totals.items()]
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
    country_counts = load_country_counts()
    print_step1(country_counts)

    region_lookup = load_region_lookup()
    table, region_totals = build_region_country_table(country_counts, region_lookup)
    print_step2(table, region_totals)

    plot_double_pie(table, region_totals)


if __name__ == "__main__":
    main()
