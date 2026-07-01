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
python double_pie_chart.py
```

The script prints two tables to the console before plotting:

1. Participants per country, sorted alphabetically.
2. Participants per region (sorted by region size, descending), with the
   countries in each region sorted by participant count (descending).

It then saves the chart to `country_of_affiliation_double_pie_chart.png`.

## Customizing colors

Region base colors are defined in `REGION_COLORS` in `double_pie_chart.py`.
Each country inherits a lighter/darker shade of its region's base color
(see `assign_country_colors`), so changing one region color updates all of
its countries consistently. Adjust `REGION_COLORS` to match your project's
branding.
