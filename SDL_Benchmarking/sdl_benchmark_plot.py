"""
SDL Transfer Performance Benchmark
Bar charts of upload/download times from three network environments to the
CINECA Simulation Data Lake, styled like a plain Google Sheets column chart.

Reads data/SDL_Benchmarking_2025.csv: mean of 10 runs (per file, per
direction, per environment).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).parent
DATA_FILE = PROJECT_DIR / "data" / "SDL_Benchmarking_2025.csv"
BENCHMARK_OUTPUT_FILE = PROJECT_DIR / "sdl_benchmark"
THROUGHPUT_OUTPUT_FILE = PROJECT_DIR / "sdl_throughput"

# Row index -> (x-axis label, file size in MB), used for the throughput plot.
FILE_INFO = {
    "00_2MB": ("2 MB\n(receiver file)", 2),
    "01_448MB": ("448 MB\n(fault output)", 448),
    "02_10GB": ("10 GB\n(SumatraPF.h5)", 10240),
}

# One light/dark pair per environment (down/up), matching the palette from
# the reference Google Sheets chart.
SERIES_COLORS = {
    "Leonardo Down": "#6FA8DC",
    "Leonardo Up": "#1155CC",
    "University Down": "#93C47D",
    "University Up": "#38761D",
    "Homeoffice Down": "#A2C4C9",
    "Homeoffice Up": "#45818E",
}


def series_label(column: str) -> str:
    location, direction = column.rsplit(" ", 1)
    if location == "Homeoffice":
        location = "Home office"
    return f"{location} ({direction.lower()})"


def load_data(csv_path=DATA_FILE) -> pd.DataFrame:
    return pd.read_csv(csv_path, index_col=0)


def style_axes(ax):
    """Plain Google-Sheets-style axes: no border, light horizontal
    gridlines only, no tick marks."""
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(True, which="major", axis="y", color="#CCCCCC", linewidth=0.8)
    ax.grid(False, which="major", axis="x")
    ax.tick_params(axis="both", length=0)


def draw_grouped_bars(ax, x, columns, values_by_column, bar_width):
    n_bars = len(columns)
    for i, column in enumerate(columns):
        offset = (i - (n_bars - 1) / 2) * bar_width
        ax.bar(
            x + offset,
            values_by_column[column],
            bar_width,
            label=series_label(column),
            color=SERIES_COLORS[column],
        )


def make_plot(df: pd.DataFrame, save_pdf=True, save_png=True):
    """Grouped log-scale bar chart of transfer time per file/environment."""
    files = list(df.index)
    labels = [FILE_INFO[f][0] for f in files]
    columns = list(df.columns)
    x = np.arange(len(files))
    bar_width = 0.85 / len(columns)

    fig, ax = plt.subplots(figsize=(8.5, 4.8), constrained_layout=True)
    draw_grouped_bars(ax, x, columns, {c: df[c] for c in columns}, bar_width)

    ax.set_yscale("log")
    ax.set_ylim(1, 3000)
    ax.set_ylabel("Transfer time (s)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    style_axes(ax)

    ax.legend(ncol=3, loc="upper left", frameon=False, columnspacing=1.0, handlelength=1.2)
    ax.set_title("SDL transfer performance (CLI v0.13.55)", loc="left", pad=10)

    if save_pdf:
        fig.savefig(f"{BENCHMARK_OUTPUT_FILE}.pdf", bbox_inches="tight")
    if save_png:
        fig.savefig(f"{BENCHMARK_OUTPUT_FILE}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_plot_throughput(df: pd.DataFrame, save_pdf=True, save_png=True):
    """Alternative view: effective throughput (MB/s). Shows that small files
    are overhead-limited, large files bandwidth-limited."""
    files = list(df.index)
    labels = [FILE_INFO[f][0] for f in files]
    file_sizes_mb = np.array([FILE_INFO[f][1] for f in files])
    columns = list(df.columns)
    x = np.arange(len(files))
    bar_width = 0.85 / len(columns)

    throughput = {c: file_sizes_mb / df[c].to_numpy() for c in columns}

    fig, ax = plt.subplots(figsize=(8.5, 4.8), constrained_layout=True)
    draw_grouped_bars(ax, x, columns, throughput, bar_width)

    ax.set_yscale("log")
    ax.set_ylim(0.05, 200)
    ax.set_ylabel("Effective throughput (MB/s)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    style_axes(ax)

    ax.legend(ncol=3, loc="upper left", frameon=False, columnspacing=1.0, handlelength=1.2)
    ax.set_title("SDL effective throughput (CLI v0.13.55)", loc="left", pad=10)

    if save_pdf:
        fig.savefig(f"{THROUGHPUT_OUTPUT_FILE}.pdf", bbox_inches="tight")
    if save_png:
        fig.savefig(f"{THROUGHPUT_OUTPUT_FILE}.png", dpi=300, bbox_inches="tight")
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
        "text.color": "#333333",
        "axes.labelcolor": "#333333",
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        "pdf.fonttype": 42,  # editable text in PDF
        "ps.fonttype": 42,
    })

    df = load_data()
    make_plot(df)
    make_plot_throughput(df)


if __name__ == "__main__":
    main()
