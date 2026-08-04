"""
SeisSol Strong Scaling Benchmark
Log-log strong-scaling chart (measured vs. ideal) in the style of the LUMI-G
reference chart, colored by discretization order.

Reads data/SeisSol_Benchmarking_AltoTiberinaCatalog_SuperMUCNGPhase1.csv:
one row per (version, precision, order), with total job time (minutes) per
node count. "Ideal" scaling is derived per order from its own smallest node
count (perfect linear speedup), over the same node-count range as that
order's measured data.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FixedFormatter, FixedLocator, NullLocator

PROJECT_DIR = Path(__file__).parent
DATA_FILE = PROJECT_DIR / "data" / "SeisSol_Benchmarking_AltoTiberinaCatalog_SuperMUCNGPhase1.csv"
OUTPUT_FILE = PROJECT_DIR / "seissol_benchmark"

META_COLUMNS = ["Version", "sp/dp", "order", "No. of Nodes"]

# One dark/light color pair per order: dark for measured, light for ideal.
ORDER_COLORS = {
    "o5": {"measured": "#1155CC", "ideal": "#6FA8DC"},  # blue
    "o4": {"measured": "#38761D", "ideal": "#93C47D"},  # green
}
ORDER_LABELS = {"o5": "order5", "o4": "order4"}


def load_data(csv_path=DATA_FILE) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def node_columns(df: pd.DataFrame) -> list[int]:
    return [int(c) for c in df.columns if c not in META_COLUMNS]


def measured_series(row: pd.Series, nodes: list[int]) -> pd.Series:
    values = row[[str(n) for n in nodes]].astype(float)
    values.index = nodes
    return values.dropna()


def ideal_series(measured: pd.Series) -> pd.Series:
    """Perfect linear scaling from the smallest measured node count."""
    base_nodes, base_time = measured.index[0], measured.iloc[0]
    return pd.Series({n: base_time * base_nodes / n for n in measured.index})


def style_axes(ax, nodes: list[int], time_ticks: list[int]):
    """Linear, evenly-spaced x-axis (node count); log y-axis with
    plain-number tick labels, like the reference chart."""
    ax.set_yscale("log")

    ax.xaxis.set_major_locator(FixedLocator(nodes))
    ax.xaxis.set_major_formatter(FixedFormatter([str(n) for n in nodes]))
    ax.xaxis.set_minor_locator(NullLocator())

    ax.yaxis.set_major_locator(FixedLocator(time_ticks))
    ax.yaxis.set_major_formatter(FixedFormatter([str(t) for t in time_ticks]))
    ax.yaxis.set_minor_locator(NullLocator())

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def make_plot(df: pd.DataFrame, save_pdf=True, save_png=True):
    nodes = node_columns(df)

    fig, ax = plt.subplots(figsize=(6.5, 5.5), constrained_layout=True)

    for _, row in df.iterrows():
        order = row["order"]
        colors = ORDER_COLORS[order]
        label = ORDER_LABELS[order]

        measured = measured_series(row, nodes)
        ideal = ideal_series(measured)

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

    time_ticks = [50, 60, 70, 80, 90, 100, 200, 300, 400, 500]
    style_axes(ax, nodes, time_ticks)

    for minutes, ref_label in [(60, "1 hour"), (120, "2 hours")]:
        ax.axhline(minutes, color="#999999", linewidth=1, linestyle="--")
        ax.text(nodes[-1], minutes * 1.03, ref_label, fontsize=8, color="#999999", ha="right", va="bottom")

    ax.set_xlabel("number of nodes")
    ax.set_ylabel("Simulation time (min)")
    ax.set_title("Strong Scaling (AltoTiberina Catalog, SuperMUC-NG-Phase1, dp, SeisSol v.1.3.1)")

    ax.legend(loc="upper right", frameon=False)

    if save_pdf:
        fig.savefig(f"{OUTPUT_FILE}.pdf", bbox_inches="tight")
    if save_png:
        fig.savefig(f"{OUTPUT_FILE}.png", dpi=300, bbox_inches="tight")
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


if __name__ == "__main__":
    main()
