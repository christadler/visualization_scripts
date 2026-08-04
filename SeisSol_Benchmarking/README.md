# SeisSol_Benchmarking

Two charts for SeisSol runs, colored by discretization order:

- A log-log strong-scaling chart (measured vs. ideal), styled after a
  LUMI-G reference chart: solid lines with markers for measured runtime,
  dashed lines for ideal (perfect linear) scaling, plain-number tick
  labels on both log axes.
- A parallel efficiency chart (ideal time / measured time, in %) vs. node
  count, with a dashed 100% reference line.

## Data

- `data/SeisSol_Benchmarking_AltoTiberinaCatalog_SuperMUCNGPhase1.csv` --
  total Slurm job time (minutes) by node count, two rows per
  (version, precision, order): `Total job time (Slurm) [mins]` (measured)
  and `ideal scaling` (perfect linear speedup from that order's smallest
  measured node count). Missing node counts for a row (e.g. order5 above
  60 nodes) are left blank.

## Usage

```bash
pip install -r requirements.txt
python seissol_benchmark_plot.py
```

Writes `seissol_benchmark.png`/`.pdf` (strong scaling) and
`seissol_efficiency.png`/`.pdf` (parallel efficiency).

## Customizing colors

`ORDER_COLORS` in `seissol_benchmark_plot.py` sets one dark/light color
pair per order (dark for measured, light for ideal).
