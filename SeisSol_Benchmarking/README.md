# SeisSol_Benchmarking

Two charts for SeisSol runs, once combining every (version, order) series
in the data and once per individual series:

- A log-log strong-scaling chart (measured vs. ideal), styled after a
  LUMI-G reference chart: solid lines with markers for measured runtime,
  dashed lines for ideal (perfect linear) scaling, plain-number tick
  labels on both log axes.
- A parallel efficiency chart (ideal time / measured time, in %) vs. node
  count, starting at 50% with solid gridlines every 10% and dashed
  gridlines every 5%.

## Data

- `data/SeisSol_Benchmarking_AltoTiberinaCatalog_SuperMUCNGPhase1.csv` --
  total Slurm job time (minutes) by node count, two rows per
  (version, precision, order): `Total job time (Slurm) [mins]` (measured)
  and `ideal scaling` (perfect linear speedup from that series' smallest
  measured node count). Missing node counts for a row (e.g. above 72
  nodes for v1.1.3 order4) are left blank.

## Usage

```bash
pip install -r requirements.txt
python seissol_benchmark_plot.py
```

Writes, for the combined data:
- `seissol_benchmark.png`/`.pdf` (strong scaling)
- `seissol_efficiency.png`/`.pdf` (parallel efficiency)

and one more pair of each, per (version, order) series found in the CSV,
named `seissol_benchmark_<version>_<order>.png`/`.pdf` and
`seissol_efficiency_<version>_<order>.png`/`.pdf`.

## Customizing colors

`SERIES_PALETTE` in `seissol_benchmark_plot.py` is a list of dark/light
color pairs (dark for measured, light for ideal), assigned in order to
each (version, order) series as it first appears in the CSV.
