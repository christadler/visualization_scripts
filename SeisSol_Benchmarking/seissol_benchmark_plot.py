"""
SeisSol Strong Scaling Benchmark
For every (version, order) benchmark series found in the CSV, and once
combining all of them, produces two charts:
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

META_COLUMNS = ["Version", "sp/dp", "order", "No. of Nodes"]

MEASURED_METRIC = "Total job time (Slurm) [mins]"
IDEAL_METRIC = "ideal scaling"

ORDER_LABELS = {"o5": "order5", "o4": "order4"}

# Dark/light color pair per series (dark for measured, light for ideal),
# cycled in the order each (version, order) combination first appears.
SERIES_PALETTE = [
    ("#1155CC", "#6FA8DC"),  # blue
    ("#38761D", "#93C47D"),  # green
    ("#B45F06", "#F6B26B"),  # orange
    ("#674EA7", "#B4A7D6"),  # purple
    ("#A61C00", "#EA9999"),  # red
    ("#134F5C", "#76A5AF"),  # teal
]


def load_data(csv_path=DATA_FILE) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def node_columns(df: pd.DataFrame) -> list[int]:
    return [int(c) for c in df.columns if c not in META_COLUMNS]


def series_keys(df: pd.DataFrame) -> list[tuple[str, str]]:
    """Unique (version, order) pairs, in first-appearance order."""
    return list(dict.fromkeys(zip(df["Version"], df["order"])))


def series_colors(keys: list[tuple[str, str]]) -> dict:
    return {key: SERIES_PALETTE[i % len(SERIES_PALETTE)] for i, key in enumerate(keys)}


def series_label(version: str, order: str) -> str:
    return f"{version} {ORDER_LABELS.get(order, order)}"


def row_series(row: pd.Series, nodes: list[int]) -> pd.Series:
    values = row[[str(n) for n in nodes]].astype(float)
    values.index = nodes
    return values.dropna()


def metric_row(df: pd.DataFrame, version: str, order: str, metric: str) -> pd.Series:
    match = df[(df["Version"] == version) & (df["order"] == order) & (df["No. of Nodes"] == metric)]
    return match.iloc[0]


def style_node_axis(ax, nodes: list[int]):
    """Log x-axis (node count) with plain-number tick labels, like the
    reference chart."""
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(FixedLocator(nodes))
    ax.xaxis.set_major_formatter(FixedFormatter([str(n) for n in nodes]))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlabel("number of nodes")


def style_time_axis(ax, time_ticks: list[int]):
    """Log y-axis (simulation time) with plain-number tick labels and a
    light horizontal grid."""
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(FixedLocator(time_ticks))
    ax.yaxis.set_major_formatter(FixedFormatter([str(t) for t in time_ticks]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_axisbelow(True)
    ax.grid(True, which="major", axis="y", color="#CCCCCC", linewidth=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def plot_scaling(df: pd.DataFrame, keys: list[tuple[str, str]], colors: dict, title: str, output_file: Path):
    nodes = node_columns(df)

    fig, ax = plt.subplots(figsize=(6.5, 5.5), constrained_layout=True)

    for version, order in keys:
        dark, light = colors[(version, order)]
        label = series_label(version, order)

        measured = row_series(metric_row(df, version, order, MEASURED_METRIC), nodes)
        ideal = row_series(metric_row(df, version, order, IDEAL_METRIC), nodes)

        ax.plot(
            measured.index, measured.values,
            linestyle="-", marker="o", markersize=5,
            color=dark, label=f"measured ({label})",
        )
        ax.plot(
            ideal.index, ideal.values,
            linestyle="--", marker="o", markersize=5,
            color=light, label=f"ideal ({label})",
        )

    time_ticks = [30, 60, 90, 120, 180, 240, 300, 360, 420]
    style_node_axis(ax, nodes)
    style_time_axis(ax, time_ticks)

    ax.set_ylabel("Simulation time (min)")
    ax.set_title(title)

    ncol = 2 if len(keys) > 1 else 1
    ax.legend(loc="upper right", ncol=ncol, frameon=True, facecolor="white", edgecolor="none", framealpha=1)

    fig.savefig(f"{output_file}.pdf", bbox_inches="tight")
    fig.savefig(f"{output_file}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_efficiency(df: pd.DataFrame, keys: list[tuple[str, str]], colors: dict, title: str, output_file: Path):
    """Parallel efficiency (%) = ideal time / measured time, per series."""
    nodes = node_columns(df)

    fig, ax = plt.subplots(figsize=(6.5, 5.5), constrained_layout=True)

    for version, order in keys:
        dark, _light = colors[(version, order)]
        label = series_label(version, order)

        measured = row_series(metric_row(df, version, order, MEASURED_METRIC), nodes)
        ideal = row_series(metric_row(df, version, order, IDEAL_METRIC), nodes)
        efficiency = ideal / measured * 100

        ax.plot(
            efficiency.index, efficiency.values,
            linestyle="-", marker="o", markersize=5,
            color=dark, label=label,
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
    ax.set_title(title)

    ax.legend(loc="lower left", frameon=True, facecolor="white", edgecolor="none", framealpha=1)

    fig.savefig(f"{output_file}.pdf", bbox_inches="tight")
    fig.savefig(f"{output_file}.png", dpi=300, bbox_inches="tight")
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
    keys = series_keys(df)
    colors = series_colors(keys)

    base_title = "AltoTiberina Catalog, SuperMUC-NG-Phase1, dp"
    plot_scaling(df, keys, colors, f"Strong Scaling ({base_title})", PROJECT_DIR / "seissol_benchmark")
    plot_efficiency(df, keys, colors, f"Parallel Efficiency ({base_title})", PROJECT_DIR / "seissol_efficiency")

    for version, order in keys:
        slug = f"{version}_{order}"
        entry_title = f"{base_title}, SeisSol {version} {ORDER_LABELS.get(order, order)}"
        plot_scaling(df, [(version, order)], colors, f"Strong Scaling ({entry_title})",
                     PROJECT_DIR / f"seissol_benchmark_{slug}")
        plot_efficiency(df, [(version, order)], colors, f"Parallel Efficiency ({entry_title})",
                         PROJECT_DIR / f"seissol_efficiency_{slug}")


if __name__ == "__main__":
    main()
