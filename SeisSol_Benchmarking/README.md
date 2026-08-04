# SeisSol_Benchmarking

Log-log strong-scaling chart (measured vs. ideal) for SeisSol runs, styled
after a LUMI-G reference chart: dashed lines with markers for measured
runtime, solid lines for ideal (perfect linear) scaling, plain-number tick
labels on both log axes.

## Data

- `data/SeisSol_Benchmarking_AltoTiberinaCatalog_SuperMUCNGPhase1.csv` --
  total Slurm job time (minutes) by node count, one row per
  (version, precision, order). Missing node counts for a row (e.g. order5
  above 60 nodes) are left blank.

## Usage

```bash
pip install -r requirements.txt
python seissol_benchmark_plot.py
```

Writes `seissol_benchmark.png` and `seissol_benchmark.pdf`. The "ideal"
line for each order is derived from that order's own smallest measured
node count (perfect linear speedup), computed only over the node-count
range where that order actually has measured data.

## Customizing colors

`ORDER_COLORS` in `seissol_benchmark_plot.py` sets one dark/light color
pair per order (dark for measured, light for ideal).
