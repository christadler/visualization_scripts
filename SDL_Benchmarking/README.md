# SDL_Benchmarking

Bar charts of SDL (Simulation Data Lake) transfer performance: upload and
download times from three network environments (Leonardo, University,
Home office), for a small, medium and large test file.

Styled like a plain Google Sheets column chart: no data labels, no bar
borders, no axis border, light horizontal gridlines only.

## Data

- `data/SDL_Benchmarking_2025.csv` -- mean of 10 runs per file, per
  direction, per environment (seconds). Row index is the file/test name;
  columns are `<Location> <Down|Up>`.

## Usage

```bash
pip install -r requirements.txt
python sdl_benchmark_plot.py
```

Writes two charts (each as `.png` and `.pdf`):

- `sdl_benchmark` -- transfer time (s), log scale
- `sdl_throughput` -- effective throughput (MB/s), log scale; shows that
  small files are overhead-limited and large files bandwidth-limited

## Customizing colors

`SERIES_COLORS` in `sdl_benchmark_plot.py` sets one light/dark color pair
per environment (down/up).
