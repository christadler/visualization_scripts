# CountryOfAffiliation_doublePieChart

Nested (double) pie/donut chart showing participants' country of affiliation,
grouped by region.

- Inner ring: region/category totals
- Outer ring: countries, colored as shades of their region's color

## Data

- `data/SDL_Trg.csv` — participant export with a `Country of Affiliation` column
- `data/Countries.csv` — lookup table mapping each country to a region/category
  (`Country`, `Category`, `Color`)

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
   total. Europe, widening countries and associated countries are always
   listed first (in that order); the remaining regions follow sorted by
   participant count (descending). Countries within a region are sorted by
   participant count (descending).

It then saves the chart to `country_of_affiliation_double_pie_chart.png`.

## Customizing colors

- `FIXED_REGION_COLORS` in `double_pie_chart.py` sets the colors for Europe,
  widening countries and associated countries (a related blue/green family).
- All other regions are colored along a yellow -> orange gradient
  (`OTHER_REGION_DARK` / `OTHER_REGION_LIGHT`), with the largest region
  getting the darkest shade.

Each country inherits a lighter/darker shade of its region's color (see
`assign_country_colors`), so changing a region's base color updates all of
its countries consistently.
