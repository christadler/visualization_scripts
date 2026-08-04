# SeisSol_Benchmarking

Log-log strong-scaling chart (measured vs. ideal) for SeisSol runs, styled
after a LUMI-G reference chart: solid lines with markers for measured
runtime, dashed lines for ideal (perfect linear) scaling, plain-number tick
labels on both log axes.

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

Writes `seissol_benchmark.png` and `seissol_benchmark.pdf`.

## Customizing colors

`ORDER_COLORS` in `seissol_benchmark_plot.py` sets one dark/light color
pair per order (dark for measured, light for ideal).
