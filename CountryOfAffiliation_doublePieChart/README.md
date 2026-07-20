# CountryOfAffiliation_doublePieChart

Nested double pie chart showing participants' country of affiliation,
grouped by region.

- Inner disk: region/category totals, labeled in-wedge as `Region (%)`
  (some region names are abbreviated in this label only, see
  `INNER_LABEL_ABBREVIATIONS`)
- Outer ring: countries, colored as shades of their region's color, labeled
  in-wedge as `Country (count)`
- No donut hole; inner and outer ring labels share the same font size
- Inner-ring labels are measured after rendering and pulled toward the
  center if needed, so long region labels never poke into the outer ring
- A region legend is still built in code but hidden (`legend.set_visible(False)`
  in `plot_double_pie`) since regions are now labeled directly in the ring

## Data

- `data/SDL_Trg.csv` — participant export with a `Country of Affiliation` column
- `data/Countries.csv` — lookup table mapping each country to a region/category
  (`Country`, `Category`, `Color`)
- `data/geoI_Participants_test.xlsx` — full workbook with one sheet per
  training/event, used by `generate_all_charts.py` (see below)

Country matching against `Countries.csv` is case-insensitive; unmatched
countries fall back to the `unknown` region.

## Usage

```bash
pip install -r requirements.txt
python double_pie_chart.py [path/to/participants.csv]
```

The participants CSV path is optional and defaults to `data/SDL_Trg.csv`.
Any CSV with a `Country of Affiliation` column can be passed instead.

The script prints two tables to the console before plotting:

1. Participants per country, sorted alphabetically.
2. Participants per region, with participant count and percentage of the
   total. Regions always appear in this fixed order: Europe, widening
   countries, associated countries, Africa, Asia, Middle East,
   Middle/South America, Oceania, U.S. + Canada. Countries within a region
   are sorted by participant count (descending).

It then saves the chart to `country_of_affiliation_double_pie_chart.png`.
The chart has no title and no visible legend.

## Generating a chart per sheet from a workbook

`generate_all_charts.py` processes every sheet of an xlsx workbook in one go:

```bash
python generate_all_charts.py [path/to/workbook.xlsx] [output_dir]
```

Defaults to `data/geoI_Participants_test.xlsx` and `charts/`. For each sheet
with a `Country of Affiliation` column (any casing) that actually has data,
it writes `<output_dir>/<SheetName>.png`. Sheets without that column, or
where the column is present but empty (overview/summary sheets, the
`Countries` lookup sheet, differently-shaped surveys, etc.), are skipped and
listed at the end.

## Customizing colors

`FIXED_REGION_COLORS` in `double_pie_chart.py` sets one color per region,
inspired by the Geo-INQUIRE branding: blue/green (from the logo) for Europe,
widening countries and associated countries; warm orange/red/yellow tones
(from the project infographic) for the remaining world regions. Any region
not listed there falls back to a grey gradient, sorted by count.

Each country inherits a lighter/darker shade of its region's color (see
`assign_country_colors`), so changing a region's base color updates all of
its countries consistently.

## Associated-countries label highlighting

Within "associated countries", `ASSOCIATED_COUNTRIES_HIGHLIGHT` (Iceland,
Israel, New Zealand, Norway, United Kingdom) are counted a bit differently
and get yellow label text (`ASSOCIATED_COUNTRIES_HIGHLIGHT_COLOR`); every
other associated country's label is a very dark green instead (the
widening-countries green, darkened via `darken_color`). This only changes
label text color, not the wedge fill.
