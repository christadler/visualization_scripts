"""
SeisSol Strong Scaling Benchmark
Two charts, colored by discretization order:
  - Log-log strong-scaling chart (measured vs. ideal), in the style of the
    LUMI-G reference chart.
  - Parallel efficiency (ideal time / measured time, in %) vs. node count.

Reads data/SeisSol_Benchmarking_AltoTiberinaCatalog_SuperMUCNGPhase1.csv:
two rows per (version, precision, order) -- "Total job time (Slurm) [mins]"
(measured) and "ideal scaling" (perfect linear speedup from the smallest
measured node count) -- with total job time (minutes) per node count.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FixedFormatter, FixedLocator, NullLocator

PROJECT_DIR = Path(__file__).parent
DATA_FILE = PROJECT_DIR / "data" / "SeisSol_Benchmarking_AltoTiberinaCatalog_SuperMUCNGPhase1.csv"
SCALING_OUTPUT_FILE = PROJECT_DIR / "seissol_benchmark"
EFFICIENCY_OUTPUT_FILE = PROJECT_DIR / "seissol_efficiency"

META_COLUMNS = ["Version", "sp/dp", "order", "No. of Nodes"]

# One dark/light color pair per order: dark for measured, light for ideal.
ORDER_COLORS = {
    "o5": {"measured": "#1155CC", "ideal": "#6FA8DC"},  # blue
    "o4": {"measured": "#38761D", "ideal": "#93C47D"},  # green
}
ORDER_LABELS = {"o5": "order5", "o4": "order4"}

MEASURED_METRIC = "Total job time (Slurm) [mins]"
IDEAL_METRIC = "ideal scaling"


def load_data(csv_path=DATA_FILE) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def node_columns(df: pd.DataFrame) -> list[int]:
    return [int(c) for c in df.columns if c not in META_COLUMNS]


def row_series(row: pd.Series, nodes: list[int]) -> pd.Series:
    values = row[[str(n) for n in nodes]].astype(float)
    values.index = nodes
    return values.dropna()


def metric_row(df: pd.DataFrame, order: str, metric: str) -> pd.Series:
    return df[(df["order"] == order) & (df["No. of Nodes"] == metric)].iloc[0]


def style_node_axis(ax, nodes: list[int]):
    """Log x-axis (node count) with plain-number tick labels, like the
    reference chart."""
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(FixedLocator(nodes))
    ax.xaxis.set_major_formatter(FixedFormatter([str(n) for n in nodes]))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlabel("number of nodes")


def style_axes(ax, nodes: list[int], time_ticks: list[int]):
    """Log-log axes with plain-number tick labels, like the reference chart."""
    style_node_axis(ax, nodes)
    ax.set_yscale("log")

    ax.yaxis.set_major_locator(FixedLocator(time_ticks))
    ax.yaxis.set_major_formatter(FixedFormatter([str(t) for t in time_ticks]))
    ax.yaxis.set_minor_locator(NullLocator())

    ax.set_axisbelow(True)
    ax.grid(True, which="major", axis="y", color="#CCCCCC", linewidth=0.8)

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def make_plot(df: pd.DataFrame, save_pdf=True, save_png=True):
    nodes = node_columns(df)

    fig, ax = plt.subplots(figsize=(6.5, 5.5), constrained_layout=True)

    for order in df["order"].unique():
        colors = ORDER_COLORS[order]
        label = ORDER_LABELS[order]

        measured = row_series(metric_row(df, order, MEASURED_METRIC), nodes)
        ideal = row_series(metric_row(df, order, IDEAL_METRIC), nodes)

        ax.plot(
            measured.index, measured.values,
            linestyle="-", marker="o", markersize=5,
            color=colors["measured"], label=f"measured ({label})",
        )
        ax.plot(
            ideal.index, ideal.values,
            linestyle="--", marker="o", markersize=5,
            color=colors["ideal"], label=f"ideal ({label})",
        )

    time_ticks = [30, 60, 90, 120, 180, 240, 300, 360, 420]
    style_axes(ax, nodes, time_ticks)

    ax.set_ylabel("Simulation time (min)")
    ax.set_title("Strong Scaling (AltoTiberina Catalog, SuperMUC-NG-Phase1, dp, SeisSol v.1.3.1)")

    ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="none", framealpha=1)

    if save_pdf:
        fig.savefig(f"{SCALING_OUTPUT_FILE}.pdf", bbox_inches="tight")
    if save_png:
        fig.savefig(f"{SCALING_OUTPUT_FILE}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_efficiency_plot(df: pd.DataFrame, save_pdf=True, save_png=True):
    """Parallel efficiency (%) = ideal time / measured time, per order."""
    nodes = node_columns(df)

    fig, ax = plt.subplots(figsize=(6.5, 5.5), constrained_layout=True)

    for order in df["order"].unique():
        color = ORDER_COLORS[order]["measured"]
        label = ORDER_LABELS[order]

        measured = row_series(metric_row(df, order, MEASURED_METRIC), nodes)
        ideal = row_series(metric_row(df, order, IDEAL_METRIC), nodes)
        efficiency = ideal / measured * 100

        ax.plot(
            efficiency.index, efficiency.values,
            linestyle="-", marker="o", markersize=5,
            color=color, label=label,
        )

    style_node_axis(ax, nodes)
    ax.set_ylim(50, 100)
    ax.yaxis.set_major_locator(FixedLocator(range(50, 101, 10)))
    ax.yaxis.set_minor_locator(FixedLocator(range(55, 100, 10)))
    ax.set_axisbelow(True)
    ax.grid(True, which="major", axis="y", linestyle="-", color="#CCCCCC", linewidth=0.8)
    ax.grid(True, which="minor", axis="y", linestyle="--", color="#DDDDDD", linewidth=0.6)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    ax.set_ylabel("Parallel efficiency (%)")
    ax.set_title("Parallel Efficiency (AltoTiberina Catalog, SuperMUC-NG-Phase1, dp, SeisSol v.1.3.1)")

    ax.legend(loc="lower left", frameon=True, facecolor="white", edgecolor="none", framealpha=1)

    if save_pdf:
        fig.savefig(f"{EFFICIENCY_OUTPUT_FILE}.pdf", bbox_inches="tight")
    if save_png:
        fig.savefig(f"{EFFICIENCY_OUTPUT_FILE}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Roboto", "Arial", "Helvetica", "DejaVu Sans"],
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9,
        "pdf.fonttype": 42,  # editable text in PDF
        "ps.fonttype": 42,
    })

    df = load_data()
    make_plot(df)
    make_efficiency_plot(df)


if __name__ == "__main__":
    main()
